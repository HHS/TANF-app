# Access Control
## AC-02(07) - Account Management | Role-Based Schemes

The organization:  
a. Establishes and administers privileged user accounts in accordance with a 
role-based access scheme that organizes allowed information system access and 
privileges into roles;  
b. Monitors privileged role assignments; and  
c. Takes [Assignment: organization-defined actions] when privileged role 
assignments are no longer appropriate.

### TDP Implementation

a. [Pull Request #95](https://github.com/HHS/TANF-app/pull/95) establishes the
implementation of roles and permissions in the TDP application.  It provides the endpoint that is used for reading existing roles and permissions. It also provides a method for checking if a user has elevated privileges.  

b. The System Admin reviews the list of TDP application users, including privileged accounts, on a monthly basis and/or when the status of a user is changed to inactive or terminated.  

c. If the status of a privileged account changes (inactive or terminated), the System Admin deactivates the privileged accounts through Django Admin.

#### Related Files

[This migration](tdrs-backend/tdpservice/users/migrations/0006_auto_20201117_1717.py) 
adds three roles by which privileged use will be established. Users without a role
will be able to log in and request access, but that is all. Users assigned the
`Data Prepper` role will have the most basic set of privileges, allowing them to 
upload and manage files for their specific STT. Users assigned the `OFA Admin` role will provide 
full administrative access, except for the ability to assign an `OFA Admin` role
to a user. This will only be allowed for the most privileged role `System Admin`.

[Pull Request #95](https://github.com/HHS/TANF-app/pull/95)
