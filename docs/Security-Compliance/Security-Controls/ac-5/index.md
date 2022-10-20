# Access Control
## AC-05 - Separation of Duties

The organization:  
a. Separates [at a minimum, data creation and control, software development and maintenance, and security functions];

b. Documents separation of duties of individuals; and 

c. Defines information system access authorizations to support separation of duties.

### TDP Implementation

**Part a.**  
The TANF Data Portal (TDP) system has explicitly defined the roles and responsibilities that accounts perform to operate and maintain the system. This includes data creation and processing, software development, maintenance, and security implementation.

The TDP system has five roles: [OFA System Admin, OFA Admin, OFA Regional Staff, ACF OCIO, and (STT) Data Analyst](../../../Technical-Documentation/images/group_list.png). These roles are defined herein under part b. 

**Part b.**  

**OFA System Admin**
The OFA System Admin can access Django Admin and has the ability to manage TDP user accounts, access all data files, monitor activity logs throughout the system, and access all system security scans.  OFA System Admin approves new users, updates profile information, deactivates/reactivates users (no other user roles do have access to Django Admin, except ACF OCIO who can view security documentation only)


**Users (OFA Admin, OFA Regional Staff, ACF OCIO, and (STT) Data Analysts)**
  * OFA Admin can upload data on behalf of (STT) Data Analysts.
  * OFA Regional Staff can manage user accounts associated with an STT in their region. Staff with this role will manage accounts from the frontend and do not have access to Django Admin. 
  * ACF OCIO can view security scans in Django Admin. Staff with this role cannot access any other functions in Django Admin. 
  * (STT) Data Analyst roles are users from the states, tribes, and territories (STT) who will be uploading data. Data Analysts collect TANF data, create data files, and transmit final data to OFA through the TANF application.  Data Analysts do not have access to Django Admin, cannot provision new TDP accounts, and do not have access to the account management functionality.

Developers of the TDP application are responsible for the software development and maintenance of the system.
  * Developers are granted only enough permission in GitHub and Cloud.gov to support their duties. 


**Developers**  
Developers are granted only enough permission in GitHub and Cloud.gov in order to support their duties.  All code and documentation committed to HHS has to be approved by the Product Owner and the HHS Tech Lead.  
  
**Part c.**   
When new users go to the TDP landing page, they must click on the "Sign in with Login.gov for grantees" (for external users) or "Sign in with ACF AMS for ACF users" (for internal users, including OFA System Admin) button.  Once they click on that button, the user is redirected to the Login.gov or ACF AMS website.  To gain access to the TDP system, internal users use PIV/CAC for authentication. External users must first create an account at Login.gov.  By creating an account in Login.gov, the user's profile is created within TDP and they have access to the TDP system without user functionality.  After they are authenticated with Login.gov, the user is redirected to the TDP frontend landing page.  Once a user is logged into the TDP system, they can request user functionality by submitting their information through the request form.  The OFA System Admin can view the request through the Django Admin and grant the user the appropriate permissions based on their job responsibilities.
