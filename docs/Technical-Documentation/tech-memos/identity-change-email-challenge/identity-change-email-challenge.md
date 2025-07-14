Ideas:
- Consider just "accepting" the new claim since login.gov makes the user prove they own the email, etc...
- If new sub comes in force user approval status to in_review (user change request) and notify the user and admin that we detected a change in their account and that it requires manual approval.

# Identity Change Email Verification Challenge Implementation Plan

**Audience**: TDP Software Engineers <br>
**Subject**:  Identity Change Email Verification Challenge Implementation <br>
**Date**:     July 10, 2025 <br>

## Summary

This technical memorandum outlines the suggested implementation of an identity change email verification challenge system to address the issue of users recreating their Login.gov accounts with the same email but different `sub` claims. When a user attempts to log in with a new `sub` claim with an email that matches an existing user, the system will require email verification before linking the new Login.gov account to the existing TANF Data Portal (TDP) account.

## Background
In TDP, when users lose access to their Login.gov credentials, they often re-create their Login.gov accounts. This generates a new UUID (`sub` claim) for the same email address, causing identity conflicts within TDP. TDP currently relies on a static `sub` claim for authentication. When the claim changes, users are locked out, and the only recovery path currently is manual deletion of the TDP account via the Django shell — a risky process that deletes the user’s submitted data.

## Method/Design

### User Model Updates

1. **Add Fields to User Model**
   ```python
   # tdpservice/users/models.py
   class User(AbstractUser):
       # Existing fields...
       
       # New fields for identity tracking
       previous_identities = models.JSONField(
           default=dict, 
           blank=True, 
           help_text="Dictionary of previous identity information, keyed by provider"
       )
       
       # Helper methods for identity tracking
       def add_previous_identity(self, provider, identity_id):
           """Add a previous identity to the user's record."""
           if not self.previous_identities:
               self.previous_identities = {}
               
           if provider not in self.previous_identities:
               self.previous_identities[provider] = []
               
           if identity_id and identity_id not in self.previous_identities[provider]:
               self.previous_identities[provider].append(identity_id)
               self.save(update_fields=['previous_identities'])
   ```

2. **Create Identity Verification Model**
   ```python
   # tdpservice/users/models.py
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
           expires_at = timezone.now() + timedelta(hours=24)
           
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
               user.add_previous_identity('login-gov', str(user.login_gov_uuid))
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

2. **Create Email Flow**
   ```python
   # tdpservice/email/helpers/identity_verification.py
   from django.core.mail import send_mail, prepare_email
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
       
       html_message = prepare_email(...)
       
       send_mail(
           subject=subject,
           from_email=settings.DEFAULT_FROM_EMAIL,
           recipient_list=[user.email],
           html_message=html_message,
       )
   ```

3. **Create Email Templates**
   ```html
   <!-- tdpservice/templates/email/identity_verification.html -->
   {% extends 'base.html' %}
   {% block content %}
   <!-- Body copy -->
   <p style="color: #000000;">


   </p>
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
   {% endblock %}
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
   // src/components/VerificationRequired/VerificationRequired.jsx
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
           const response = await axios.get(`/v1/users/verify-identity/${token}/`);
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
   // src/components/Routes/Routes.js
   import VerificationRequired from '../VerificationRequired';
   import VerifyIdentity from '../VerifyIdentity';
   
   // Note these aren't private routes
   <Route path="/verification-required" element={<VerificationRequired />} />
   <Route path="/verify-identity/:token" element={<VerifyIdentity />} />
   ```

## Conclusion

The Email Verification Challenge approach provides a secure and user-friendly solution to the issue of users recreating their IdP accounts. It ensures that only the legitimate owner of an email address can link a new identity to an existing account, preventing unauthorized account takeovers. The implementation is relatively straightforward and builds on existing infrastructure, making it a practical solution that can be implemented quickly.

## Affected Systems
- TDP backend
- TDP frontend
