# Access Control
## AC-06 - Least Privilege

The organization employs the principle of least privilege, allowing only authorized accesses for users (or processes acting on behalf of users) which are necessary to accomplish assigned tasks in accordance with organizational missions and business functions.

AC-6 (2) Additional FedRAMP Requirements and Guidance: Examples of security functions include but are not limited to: establishing system accounts, configuring access authorizations (i.e., permissions, privileges), setting events to be audited, and setting intrusion detection parameters, system programming, system and security administration, other privileged functions.

### TDP Implementation

In order to access the TDP application, users must login through Login.gov, using password and Multi-Factor Authentication (MFA).  Only authorized users can access TDP.  

AC-6 (2)  
Once users are logged in the application, users can only perform tasks associated to their user type as described in [AC-5, Part (b)](docs/controls/access_control/ac-05.md).  Privileged functions can only be performed by OFA Admins (e.g. approves new users, updates profile information, and inactivates/reactivates users).  New user accounts are established with no privileges upon creation and only System Admins can grant permissions to those users.

#### Related Files
[AC-5 | Separation of Duties](docs/controls/access_control/ac-05.md)
