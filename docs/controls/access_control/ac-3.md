# Access Control
## AC-03 - ACCESS ENFORCEMENT

The information system enforces approved authorizations for logical access to information and system resources in accordance with applicable access control policies.  

### TDP Implementation
Access enforcement to the TDP application is provided by Login.gov.  All users will login through Login.gov and Multi-Factor Authentication (MFA) to gain access to the TDP application.  Additionally, authorization is further limited through the use of Django admin since users will also need to have an active role before their account is fully "activated".
	
#### Related Files
