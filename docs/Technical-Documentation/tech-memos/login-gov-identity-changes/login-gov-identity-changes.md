# Email Verification Challenge Implementation Plan

**Audience**: TDP Software Engineers <br>
**Subject**:  Email Verification Challenge Implementation <br>
**Date**:     July 10, 2025 <br>

## Summary

This technical memorandum outlines the implementation of an Email Verification Challenge system to address the issue of users recreating their Login.gov accounts with the same email but different `sub` claims. When a user attempts to log in with a new `sub` claim with an email that matches an existing user, the system will require email verification before linking the new Login.gov account to the existing TANF Data Portal account.

## Background
In TDP, when users lose access to their Login.gov credentials, they often re-create their Login.gov accounts. This generates a new UUID (`sub` claim) for the same email address, causing identity conflicts within TDP. TDP currently relies on a static `sub` claim for authentication. When the claim changes, users are locked out, and the only recovery path currently is manual deletion of the TDP account via the Django shell — a risky process that deletes the user’s submitted data.

## Method

### User Model Updates

1. **Add Fields to User Model**
   ```python
   # tdpservice/users/models.py
   class User(AbstractUser):
       # Existing fields...
       
       # Store multiple sub claims for a user
       login_gov_uuid = models.UUIDField(
           editable=False, blank=True, null=True, unique=True
       )
       
       # Add fields for email verification
       email_verification_token = models.CharField(max_length=64, blank=True, null=True)
       email_verification_token_created_at = models.DateTimeField(blank=True, null=True)
       pending_login_gov_uuid = models.UUIDField(blank=True, null=True)
   ```

2. **Create Identity Verification Model**
   ```python
   class IdentityVerification(models.Model):
       """Model to track identity verification requests."""
       
       id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
       user = models.ForeignKey('users.User', on_delete=models.CASCADE)
       email = models.EmailField()
       new_sub_claim = models.UUIDField()
       verification_token = models.CharField(max_length=64)
       created_at = models.DateTimeField(auto_now_add=True)
       expires_at = models.DateTimeField()
       verified = models.BooleanField(default=False)
       verified_at = models.DateTimeField(null=True, blank=True)
       
       class Meta:
           ordering = ['-created_at']
           
       def is_expired(self):
           """Check if the verification request has expired."""
           return timezone.now() > self.expires_at
   ```

### 2. Email Verification Service

1. **Create Email Verification Service**
   ```python
   # tdpservice/users/services/email_verification.py
   import secrets
   import uuid
   from datetime import timedelta
   from django.utils import timezone
   from django.conf import settings
   from tdpservice.users.models import User, IdentityVerification
   
   class EmailVerificationService:
       """Service for handling email verification."""
       
       @staticmethod
       def generate_token():
           """Generate a secure random token."""
           return secrets.token_urlsafe(48)
       
       @staticmethod
       def create_verification_request(user, email, new_sub_claim):
           """Create a new identity verification request."""
           token = EmailVerificationService.generate_token()
           expires_at = timezone.now() + timedelta(hours=24) # Could be a shorter time frame
           
           verification = IdentityVerification.objects.create(
               user=user,
               email=email,
               new_sub_claim=new_sub_claim,
               verification_token=token,
               expires_at=expires_at
           )
           
           return verification
       
       @staticmethod
       def verify_token(token):
           """Verify a token and update the user if valid."""
           try:
               verification = IdentityVerification.objects.get(
                   verification_token=token,
                   verified=False
               )
               
               if verification.is_expired():
                   return False, "Verification link has expired."
               
               # Update the user's sub claim
               user = verification.user
               user.login_gov_uuid = verification.new_sub_claim
               user.save()
               
               # Mark verification as complete
               verification.verified = True
               verification.verified_at = timezone.now()
               verification.save()
               
               return True, "Identity verified successfully."
           except IdentityVerification.DoesNotExist:
               return False, "Invalid verification token."
   ```

2. **Create Email Sending Service**
   ```python
   # tdpservice/email/helpers/identity_verification.py
   from django.core.mail import send_mail
   from django.conf import settings
   from django.template.loader import render_to_string
   
   def send_identity_verification_email(user, verification):
       """Send an email with a verification link."""
       subject = "Verify Your Identity for TANF Data Portal"
       verification_url = f"{settings.FRONTEND_BASE_URL}/verify-identity/{verification.verification_token}"
       
       context = {
           "first_name": user.first_name,
           "verification_url": verification_url,
           "expires_at": verification.expires_at,
       }
       
       html_message = render_to_string("email/identity_verification.html", context)
       plain_message = render_to_string("email/identity_verification.txt", context)
       
       send_mail(
           subject=subject,
           message=plain_message,
           from_email=settings.DEFAULT_FROM_EMAIL,
           recipient_list=[user.email],
           html_message=html_message,
       )
   ```

3. **Create Email Templates**
   ```html
   <!-- tdpservice/templates/email/identity_verification.html -->
   <!DOCTYPE html>
   <html>
   <head>
       <meta charset="utf-8">
       <title>Verify Your Identity</title>
   </head>
   <body>
       <h1>Verify Your Identity for TANF Data Portal</h1>
       <p>Hello {{ first_name }},</p>
       <p>We noticed that you're trying to log in with a new identity provider account using the same email address.</p>
       <p>To link this new account to your existing TANF Data Portal account, please click the button below:</p>
       <p>
           <a href="{{ verification_url }}" style="background-color: #0071bc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               Verify My Identity
           </a>
       </p>
       <p>Or copy and paste this URL into your browser: {{ verification_url }}</p>
       <p>This link will expire on {{ expires_at|date:"F j, Y, g:i a" }}.</p>
       <p>If you did not request this verification, please ignore this email.</p>
       <p>Thank you,<br>TANF Data Portal Team</p>
   </body>
   </html>
   ```

   ```
   <!-- tdpservice/templates/email/identity_verification.txt -->
   Verify Your Identity for TANF Data Portal
   
   Hello {{ first_name }},
   
   We noticed that you're trying to log in with a new identity provider account using the same email address.
   
   To link this new account to your existing TANF Data Portal account, please visit the following URL:
   
   {{ verification_url }}
   
   This link will expire on {{ expires_at|date:"F j, Y, g:i a" }}.
   
   If you did not request this verification, please ignore this email.
   
   Thank you,
   TANF Data Portal Team
   ```

### 3. Update Authentication Flow

1. **Modify Handle User Method**
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
               # User exists with this email but has a different sub claim
               # Create verification request and send email
               verification = EmailVerificationService.create_verification_request(
                   user=existing_user,
                   email=email,
                   new_sub_claim=sub
               )
               
               send_identity_verification_email(existing_user, verification)
               
               # Return a response indicating that verification is required
               return Response({
                   "status": "verification_required",
                   "message": "Please check your email to verify your identity."
               }, status=status.HTTP_202_ACCEPTED)
           else:
               # No existing user with this email, create a new one
               # Existing user creation code...
   ```

2. **Create Verification Endpoint**
   ```python
   # tdpservice/users/api/verify_identity.py
   from rest_framework import status
   from rest_framework.response import Response
   from rest_framework.views import APIView
   from tdpservice.users.services.email_verification import EmailVerificationService
   
   class VerifyIdentityView(APIView):
       """View for verifying user identity."""
       
       permission_classes = []  # Allow unauthenticated access
       
       def get(self, request, token):
           """Verify the token and update the user."""
           success, message = EmailVerificationService.verify_token(token)
           
           if success:
               return Response({
                   "status": "success",
                   "message": message
               })
           else:
               return Response({
                   "status": "error",
                   "message": message
               }, status=status.HTTP_400_BAD_REQUEST)
   ```

3. **Add URL Route**
   ```python
   # tdpservice/users/urls.py
   from django.urls import path
   from .api.verify_identity import VerifyIdentityView
   
   urlpatterns = [
       # Existing URLs...
       path('verify-identity/<str:token>/', VerifyIdentityView.as_view(), name='verify-identity'),
   ]
   ```

### 4. Frontend Implementation

1. **Create Verification Required Page**
   ```jsx
   // src/pages/VerificationRequired.jsx
   import React from 'react';
   
   const VerificationRequired = () => {
     return (
       <div className="verification-required">
         <h1>Verification Required</h1>
         <p>
           We've detected that you're trying to log in with a new identity provider account
           using an email address that's already associated with an existing account.
         </p>
         <p>
           To protect your account security, we've sent a verification email to your address.
           Please check your inbox and click the verification link to link these accounts.
         </p>
         <p>
           If you don't receive the email within a few minutes, please check your spam folder
           or contact support for assistance.
         </p>
       </div>
     );
   };
   
   export default VerificationRequired;
   ```

2. **Create Verification Confirmation Page**
   ```jsx
   // src/pages/VerifyIdentity.jsx
   import React, { useEffect, useState } from 'react';
   import { useParams, useNavigate } from 'react-router-dom';
   import axios from 'axios';
   
   const VerifyIdentity = () => {
     const { token } = useParams();
     const navigate = useNavigate();
     const [status, setStatus] = useState('verifying');
     const [message, setMessage] = useState('');
     
     useEffect(() => {
       const verifyToken = async () => {
         try {
           const response = await axios.get(`/api/users/verify-identity/${token}/`);
           setStatus('success');
           setMessage(response.data.message);
           
           // Redirect to login after successful verification
           setTimeout(() => {
             navigate('/login');
           }, 5000);
         } catch (error) {
           setStatus('error');
           setMessage(error.response?.data?.message || 'Verification failed.');
         }
       };
       
       verifyToken();
     }, [token, navigate]);
     
     return (
       <div className="verify-identity">
         <h1>Identity Verification</h1>
         
         {status === 'verifying' && (
           <p>Verifying your identity...</p>
         )}
         
         {status === 'success' && (
           <>
             <div className="success-icon">✓</div>
             <p>Your identity has been verified successfully!</p>
             <p>You will be redirected to the login page in a few seconds.</p>
             <button onClick={() => navigate('/login')}>
               Go to Login
             </button>
           </>
         )}
         
         {status === 'error' && (
           <>
             <div className="error-icon">✗</div>
             <p>Verification failed: {message}</p>
             <p>Please try again or contact support for assistance.</p>
             <button onClick={() => navigate('/login')}>
               Go to Login
             </button>
           </>
         )}
       </div>
     );
   };
   
   export default VerifyIdentity;
   ```

3. **Update Login Flow**
   ```jsx
   // src/pages/Login.jsx
   // Update login flow to handle verification_required response
   
   const handleLogin = async () => {
     try {
       const response = await loginService.login();
       
       if (response.data.status === 'verification_required') {
         // Redirect to verification required page
         navigate('/verification-required');
       } else {
         // Normal login flow
         // ...
       }
     } catch (error) {
       // Handle error
     }
   };
   ```

4. **Add Routes**
   ```jsx
   // src/App.jsx or router configuration
   import VerificationRequired from './pages/VerificationRequired';
   import VerifyIdentity from './pages/VerifyIdentity';
   
   // In your routes configuration
   <Route path="/verification-required" element={<VerificationRequired />} />
   <Route path="/verify-identity/:token" element={<VerifyIdentity />} />
   ```

### 5. Security Considerations

1. **Token Security**
   - Use cryptographically secure random tokens
   - Set appropriate expiration times
   - Implement rate limiting for verification attempts

2. **Email Security**
   - Use SPF, DKIM, and DMARC for email authentication
   - Implement anti-phishing measures in emails
   - Use TLS for email transmission

3. **Verification Flow Security**
   - Implement CSRF protection
   - Use HTTPS for all verification links
   - Implement proper error handling

4. **Audit Logging**
   ```python
   # tdpservice/users/services/email_verification.py
   import logging
   
   logger = logging.getLogger(__name__)
   
   # In verification methods
   logger.info(f"Identity verification requested for user {user.id} with email {email}")
   logger.info(f"Identity verification successful for user {user.id}")
   ```

### 6. Testing

1. **Unit Tests**
   ```python
   # tdpservice/users/test/test_email_verification.py
   from django.test import TestCase
   from django.utils import timezone
   from datetime import timedelta
   from tdpservice.users.models import User, IdentityVerification
   from tdpservice.users.services.email_verification import EmailVerificationService
   
   class EmailVerificationTests(TestCase):
       def setUp(self):
           self.user = User.objects.create_user(
               username='test@example.com',
               email='test@example.com',
               login_gov_uuid='11111111-1111-1111-1111-111111111111'
           )
           
       def test_create_verification_request(self):
           verification = EmailVerificationService.create_verification_request(
               user=self.user,
               email=self.user.email,
               new_sub_claim='22222222-2222-2222-2222-222222222222'
           )
           
           self.assertEqual(verification.user, self.user)
           self.assertEqual(verification.email, self.user.email)
           self.assertEqual(verification.new_sub_claim, '22222222-2222-2222-2222-222222222222')
           self.assertIsNotNone(verification.verification_token)
           
       def test_verify_token_success(self):
           verification = IdentityVerification.objects.create(
               user=self.user,
               email=self.user.email,
               new_sub_claim='22222222-2222-2222-2222-222222222222',
               verification_token='test-token',
               expires_at=timezone.now() + timedelta(hours=1)
           )
           
           success, message = EmailVerificationService.verify_token('test-token')
           
           self.assertTrue(success)
           self.user.refresh_from_db()
           self.assertEqual(self.user.login_gov_uuid, '22222222-2222-2222-2222-222222222222')
           
       def test_verify_token_expired(self):
           verification = IdentityVerification.objects.create(
               user=self.user,
               email=self.user.email,
               new_sub_claim='22222222-2222-2222-2222-222222222222',
               verification_token='test-token',
               expires_at=timezone.now() - timedelta(hours=1)
           )
           
           success, message = EmailVerificationService.verify_token('test-token')
           
           self.assertFalse(success)
           self.user.refresh_from_db()
           self.assertEqual(self.user.login_gov_uuid, '11111111-1111-1111-1111-111111111111')
   ```

2. **Integration Tests**
   ```python
   # tdpservice/users/test/test_api/test_verify_identity.py
   from django.test import TestCase
   from django.urls import reverse
   from django.utils import timezone
   from datetime import timedelta
   from rest_framework.test import APIClient
   from tdpservice.users.models import User, IdentityVerification
   
   class VerifyIdentityViewTests(TestCase):
       def setUp(self):
           self.client = APIClient()
           self.user = User.objects.create_user(
               username='test@example.com',
               email='test@example.com',
               login_gov_uuid='11111111-1111-1111-1111-111111111111'
           )
           
       def test_verify_identity_success(self):
           verification = IdentityVerification.objects.create(
               user=self.user,
               email=self.user.email,
               new_sub_claim='22222222-2222-2222-2222-222222222222',
               verification_token='test-token',
               expires_at=timezone.now() + timedelta(hours=1)
           )
           
           url = reverse('verify-identity', kwargs={'token': 'test-token'})
           response = self.client.get(url)
           
           self.assertEqual(response.status_code, 200)
           self.assertEqual(response.data['status'], 'success')
           
           self.user.refresh_from_db()
           self.assertEqual(self.user.login_gov_uuid, '22222222-2222-2222-2222-222222222222')
           
       def test_verify_identity_invalid_token(self):
           url = reverse('verify-identity', kwargs={'token': 'invalid-token'})
           response = self.client.get(url)
           
           self.assertEqual(response.status_code, 400)
           self.assertEqual(response.data['status'], 'error')
   ```

3. **End-to-End Tests**
   - Test the complete flow from login to verification
   - Test email delivery
   - Test frontend components

### 7. Monitoring and Logging

1. **Add Monitoring**
   - Monitor verification request rates
   - Monitor verification success/failure rates
   - Set up alerts for unusual activity

2. **Enhanced Logging**
   ```python
   # In verification service
   logger.info(f"Identity verification requested for user {user.id} with email {email}")
   logger.info(f"Identity verification successful for user {user.id}")
   logger.warning(f"Identity verification failed for token {token}")
   ```

3. **Metrics Collection**
   - Track verification request counts
   - Track verification success/failure rates
   - Track time to complete verification

### 8. Documentation

1. **User Documentation**
   - Document the verification process
   - Create FAQ for common issues
   - Provide support contact information

2. **Developer Documentation**
   - Document the verification flow
   - Document API endpoints
   - Document security considerations

3. **Admin Documentation**
   - Document monitoring and alerting
   - Document troubleshooting steps
   - Document verification request management

## Timeline

- **Week 1**: Database schema updates and service implementation
- **Week 2**: Email templates and frontend implementation
- **Week 3**: Testing and refinement
- **Week 4**: Documentation and deployment

## Resources Required

- **Personnel**: Backend developer, frontend developer, QA engineer
- **Infrastructure**: Email delivery service
- **External Services**: None (all self-hosted)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Email delivery issues | High | Medium | Use reliable email service, implement retry logic, provide alternative verification methods |
| User confusion | Medium | Medium | Clear instructions, support resources, user-friendly error messages |
| Security vulnerabilities | High | Low | Security review, penetration testing, regular updates |
| Verification spam | Medium | Low | Rate limiting, captcha, monitoring for unusual activity |

## Conclusion

The Email Verification Challenge approach provides a secure and user-friendly solution to the issue of users recreating their IdP accounts. It ensures that only the legitimate owner of an email address can link a new identity to an existing account, preventing unauthorized account takeovers. The implementation is relatively straightforward and builds on existing infrastructure, making it a practical solution that can be implemented quickly.
