## Criteria for 456

The following criteria will be used to determine whether Django admin console can be used to meet security controls in lieu of user interface (UI) for OFA MVP. Django admin console is a backend-only action that a system admin would take. For Django admin console to be used, both of the criteria should be met: 

- Django admin console allows TDRS super admin to modify  account information and access management permissions of TDRS users 
- Django admin console logs actions including the user who made the change, what object the change was performed on, what the specific change was and the date and time the change was made
- Falls under the access control (AC), identification and authentication (IA), or audit and accountability (AU) family of security controls   

AC Template

- [ ] Django admin console enables super admin to edit user permissions or modify user information 
- [ ] Docs are updated with documentation for specific security control relevant to the issue

