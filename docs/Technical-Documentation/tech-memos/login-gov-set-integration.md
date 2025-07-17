# Login.gov Security Event Token (SET) Integration

**Audience**: TDP Software Engineers <br>
**Subject**: Integration of Login.gov Security Event Tokens with Account Recreation Handling <br>
**Date**: July 17, 2025 <br>

## Summary
This technical memorandum outlines the implementation plan for integrating Security Event Tokens (SETs) from Login.gov into the TDP application. The integration will enable TDP to:
1. Handle security-related notifications about user accounts
2. Automatically manage account recreation scenarios when users delete and recreate their Login.gov accounts
3. Maintain audit history and respond appropriately to security events

## Background
Login.gov provides a Security Event Token (SET) notification system that follows the OpenID RISC Event Types specification. These notifications are sent as JWT tokens via HTTP POST requests when specific security events occur for users, such as:
- Account disabling
- Account purging (when users delete their accounts)
- Password resets
- Recovery information changes

A common issue in production is that users sometimes delete their Login.gov accounts and recreate them, which results in a new `sub` claim for the same email address. This causes authentication issues in TDP since it relies on the `sub` claim for user identification. By implementing SET handling, particularly for the "Account Purged" event, we can automatically manage these account recreation scenarios without requiring additional user verification steps.

## Out of Scope
* Changes to the existing Login.gov authentication flow
* Frontend UI components for displaying security events (may be considered in a future enhancement)
* Integration with other identity providers' security event systems
* Real-time notifications to users about security events

## Method/Design

### Security Event Token Model

Create a model to store Security Event Tokens from Login.gov.

```python
# tdpservice/security/models.py

class SecurityEventToken(models.Model):
    """Model to store Security Event Tokens from Login.gov."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='security_events',
        null=True,
        blank=True
    )
    email = models.EmailField(null=True, blank=True)
    event_type = models.CharField(max_length=255)
    event_data = models.JSONField()
    jwt_id = models.CharField(max_length=255, unique=True)  # jti claim
    issuer = models.CharField(max_length=255)
    issued_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['user']),
            models.Index(fields=['email']),
            models.Index(fields=['processed']),
        ]
```

### SET Receiver Endpoint
Create a dedicated endpoint to receive and process SETs from Login.gov. The endpoint will be a POST endpoint that will receive the SETs from Login.gov. The endpoint will be protected by no authentication and no authorization. The endpoint needs to grab existing Login.gov public keys to verify the JWTs. Once verified and decoded, the data is passed to an event handler for remaining processing.

```python
# tdpservice/security/api/views.py

class SecurityEventTokenView(APIView):
    """
    Endpoint to receive Security Event Tokens (SETs) from Login.gov.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """
        Process incoming Security Event Token from Login.gov.
        """
        try:
            # Get the JWT from the request
            if request.content_type != 'application/secevent+jwt':
                logger.error(f"Invalid content type: {request.content_type}")
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # Get the JWT from the request body
            jwt_token = request.body.decode('utf-8').strip()

            # Fetch Login.gov's public key from the certificates endpoint
            certs_response = requests.get(settings.LOGIN_GOV_CERTS_URL)
            certs = certs_response.json()

            # Find the key that matches the kid in the JWT header
            header = jwt.get_unverified_header(jwt_token)
            key_id = header.get('kid')

            if not key_id:
                logger.error("No 'kid' found in JWT header")
                return Response(status=status.HTTP_400_BAD_REQUEST)

            public_key = None
            for key in certs.get('keys', []):
                if key.get('kid') == key_id:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break

            if not public_key:
                logger.error(f"No public key found for kid: {key_id}")
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # Decode and verify the JWT
            decoded_jwt = jwt.decode(
                jwt_token,
                public_key,
                algorithms=['RS256'],
                audience=settings.LOGIN_GOV_SET_AUDIENCE,
                options={'verify_exp': True}
            )

            # Process the event
            events = decoded_jwt.get('events', {})
            if not events:
                logger.error("No events found in JWT")
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # Process each event in the JWT
            for event_type, event_data in events.items():
                SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

            return Response(status=status.HTTP_200_OK)

        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Error processing SET: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Event Processing System
To handle the myriad of events that Login.gov publishes it is suggested to implement a class based handler. The handler will maintain a map of event types to event handlers. The handlers are responsible for the unique logic to handle their event.

```python
# tdpservice/security/handlers.py

class SecurityEventHandler:
    """Handler for security events."""

    # Should we care about these?
    # Account Locked Due to MFA (Multi-Factor Authentication) Limit Reached
    # Identifier Changed
    # Identifier Recycled
    # Reproofing Completed

    handler_map = {
        "https://schemas.openid.net/secevent/risc/event-type/account-disabled":
            SecurityEventHandler.handle_account_disabled,
        "https://schemas.openid.net/secevent/risc/event-type/account-enabled":
            SecurityEventHandler.handle_account_enabled,
        "https://schemas.openid.net/secevent/risc/event-type/account-purged":
            SecurityEventHandler.handle_account_purged,
        "https://schemas.login.gov/secevent/risc/event-type/password-reset":
            SecurityEventHandler.handle_password_reset,
        "https://schemas.openid.net/secevent/risc/event-type/recovery-activated":
            SecurityEventHandler.handle_recovery_activated,
        "https://schemas.openid.net/secevent/risc/event-type/recovery-information-changed":
            SecurityEventHandler.handle_recovery_information_changed,
    }

    @classmethod
    def handle_event(cls, event_type, event_data, decoded_jwt):
        """
        Handle specific event types.
        """
        try:
            subject = event_data.get("subject")
            if "sub" not in subject:
                logger.warn(f"No 'sub' found in subject: {subject} for event: {event_type}. SKIPPING.")
                return

            user = User.objects.get(login_gov_uuid=subject.get("sub"))

            security_event = SecurityEventToken.objects.create(
                event_type=event_type,
                event_data=event_data,
                jwt_id=decoded_jwt.get('jti'),
                issuer=decoded_jwt.get('iss'),
                issued_at=decoded_jwt.get('iat'),
                received_at=timezone.now(),
                user=user,
                email=user.email,
            )

            # Call the appropriate handler if available
            handler = cls.handler_map.get(event_type)
            if handler:
                handled = handler(security_event)
                security_event.processed = handled
                security_event.processed_at = timezone.now()
                security_event.save()
            else:
                logger.info(f"No specific handler for event type: {event_type}")

        except Exception as e:
            logger.exception(f"Error handling event {event_type}: {e}")

    @classmethod
    def _handle_account_disabled(cls, security_event):
        """Handle account-disabled event."""
        user = security_event.user
        if user:
            user.account_approval_status = AccountApprovalStatusChoices.DEACTIVATED
            user.is_active = False
            user.save()
            logger.info(f"User {user.username} account disabled due to Login.gov event")
            return True
        return False

    @classmethod
    def _handle_account_enabled(cls, security_event):
        """Handle account-enabled event."""
        user = security_event.user
        if user and user.account_approval_status == AccountApprovalStatusChoices.DEACTIVATED:
            # Only re-enable if previously deactivated, don't override other statuses
            user.account_approval_status = AccountApprovalStatusChoices.APPROVED
            user.is_active = True
            user.save()
            logger.info(f"User {user.username} account re-enabled due to Login.gov event")
            return True
        return False

    @classmethod
    def _handle_account_purged(cls, security_event):
        """Handle account-purged event when a user deletes their Login.gov account."""
        # Find user by Login.gov UUID
        user = security_event.user

        # Set login_gov_uuid to null and deactivate user
        user.login_gov_uuid = None
        user.account_approval_status = AccountApprovalStatusChoices.DEACTIVATED
        user.is_active = False
        user.save()

        logger.info(f"User {user.username} Login.gov account was purged. Prepared for potential recreation.")
        return True

    @classmethod
    def _handle_password_reset(cls, security_event):
        """Handle password-reset event."""
        user = security_event.user
        logger.info(f"User {user.username} performed a password reset")
        return True

    @classmethod
    def _handle_recovery_activated(cls, security_event):
        """Handle recovery-activated event when user initiates account recovery."""
        user = security_event.user
        logger.info(f"User {user.username} initiated account recovery")
        return True

    @classmethod
    def _handle_recovery_information_changed(cls, security_event):
        """Handle recovery-information-changed event when user modifies their recovery methods."""
        user = security_event.user
        logger.info(f"User {user.username} changed their recovery information")
        return True
```

### Update Authentication Flow

Update the authentication flow to handle account recreation scenarios. If we find a user with an existing email, a different sub, a purge event, and a account enabled event we can guarantee the user re-created and verified their account with Login.gov. In this case we immediately update the user login_gov_uuid and proceed as normal. In the event that all these criteria aren't met, we flag the user's account and indicate admin intervention and verification is required. In the intervention case, the users account is put into a review state and they are not allowed to authenticate to TDP until the admin confirms this was a valid ID change.

```python
# tdpservice/users/api/login.py
def handle_user(self, request, id_token, decoded_token_data):
    """Handle the incoming user."""
    # Existing code...

    # Authenticate with `sub` and not username, as user's can change their
    # corresponding emails externally.
    user = CustomAuthentication.authenticate(**auth_options)

    if user and user.is_active:
        # Existing code for active user...
    elif user and not user.is_active:
        # Existing code for inactive user...
    else:
        User = get_user_model()

        # Check if a user with the same email already exists
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            # TODO: write user update or admin flow
        else:
            # Existing user creation code...

```

### Configuration Settings
We will add the necessary configuration settings:

```python
# tdpservice/settings/common.py

# Login.gov SET Integration
LOGIN_GOV_SET_AUDIENCE = env.str('LOGIN_GOV_SET_AUDIENCE', 'https://your-app-domain.gov/api/security/events/login-gov/')
LOGIN_GOV_CERTS_URL = env.str('LOGIN_GOV_CERTS_URL', 'https://idp.int.identitysandbox.gov/api/openid_connect/certs')
```

### Admin Interface
Create an admin model to view and manage security events.

```python
# tdpservice/security/admin.py

class SecurityEventTokenAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'email', 'issued_at', 'received_at', 'processed')
    list_filter = ('user', 'event_type', 'processed', 'received_at')
    search_fields = ('user__username', 'user__email', 'email', 'event_type')
    readonly_fields = ('id', 'jwt_id', 'issuer', 'issued_at', 'received_at', 'event_data')
    date_hierarchy = 'received_at'
```

## Affected Systems
- **Django Backend**: New models, views, and handlers for SET processing
- **User Authentication System**: Enhanced handling of account recreation scenarios
- **Admin Interface**: New admin views for security events
- **Deployment Configuration**: Registration of SET endpoint with Login.gov
- **Logging and Monitoring**: Enhanced logging for security events and account recreation

## Use and Test Cases to Consider

### Use Cases
1. **Account Disabled**: Login.gov disables a user account, TDP receives the SET and marks the user as deactivated
2. **Account Enabled**: Login.gov re-enables a previously disabled account, TDP updates the user status
3. **Account Purged**: Login.gov purges a user account, TDP prepares for potential recreation
4. **Account Recreation**: User deletes and recreates their Login.gov account, TDP automatically links the new account
5. **Password Reset**: User resets their password in Login.gov, TDP logs the event
6. **Recovery Activated**: User initiates account recovery in Login.gov, TDP logs the event
7. **Recovery Information Changed**: User changes their recovery methods, TDP logs the event

### Test Cases
1. **Valid SET Processing**: Verify that valid SETs are properly received, validated, and processed (Requires mocking/code injection to fake the Login.gov private key)
2. **Invalid SET Handling**: Test handling of invalid SETs (wrong signature, expired, etc.)
