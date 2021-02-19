# Access Control
## AC-05 - Separation of Duties

The organization:  
a. Separates [at a minimum, data creation and control, software development and maintenance, and security functions];

b. Documents separation of duties of individuals; and 

c. Defines information system access authorizations to support separation of duties.

### TDP Implementation

**Part a.**  
The TANF Data Portal (TDP) system has explicitly defined the roles and responsibilities that accounts perform to operate and maintain the system. This includes data creation and processing, software development, maintenance, and security implementation.

The TDP system has three roles: System Admin, OFA Admin and Data Prepper.
  * System Admin can access Django Admin and manage TDP accounts, including provisioning new user accounts on request.    
  * OFA Admin can upload data on behalf of Data Preppers and upload data files locally into the web application  
  * Data Prepper roles are users from the states, tribes, and territories (STT) who will be uploading data.  Data Preppers collect TANF data, create data files, and transmit final data to OFA through the TANF application.  Data Preppers reads data over assigned region and are able to upload and submit new TANF reports, replace and resubmit TANF reports.Data Preppers do not have access to Django Admin, cannot provision new TDP accounts, and do not have access to the account management functionality.

Developers of the TDP application are responsible for the software development and maintenance of the system.
  * Developers are granted only enough permission in GitHub and Cloud.gov to support their duties.    

**Part b.**  

**System Admin**
The System Admin can access Django Admin and has the ability to manage TDP accounts.  System Admin approves new users, updates profile information, deactivates, and reactivates users (Data Preppers (STTs) do not have access to this).

**Users (OFA Admin and Data Preppers)**
The OFA Admin has the ability to upload data on behalf of Data Preppers and upload data files locally into the web application. 

Users from the states, tribes, and territories (STT) who will be uploading data will have the role Data Preppers.  For the OFA MVP, STT will not have access to the TDP system, but OFA Admin will act as Data Prepper roles. Data Preppers are able to upload new TANF reports, replace and resubmit TANF reports, and download their uploaded reports.  

**Developers**  
Developers are granted only enough permission in GitHub and Cloud.gov in order to support their duties.  All code and documentation committed to HHS has to be approved by the Product Owner and the HHS Tech Lead.  


**Part c.**   
When new users go to the TDP landing page, they must click on the "Sign in with Login.gov" button.  Once they click on that button, the user is redirected to the Login.gov website.  To gain access to the TDP system, users must first create an account at Login.gov.  By creating an account in Login.gov, the user's profile is created within TDP and they have access to the TDP system without user functionality.  After they are authenticated with Login.gov, the user is redirected to the TDP frontend landing page.  Once a user is logged into the TDP system, they can request user functionality by submitting their information through the request form.  The OFA Admin can view the request through the Django Admin and grants the user the appropriate permissions based on their job responsibilities.  


#### Related Files
