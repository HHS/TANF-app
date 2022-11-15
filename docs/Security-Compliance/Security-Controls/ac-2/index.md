# Access Control
## AC-02 - Account Management
The organization:

a. Identifies and selects the following types of information system accounts to support organizational missions/business functions: (individual, shared, group, system, guest/anonymous, emergency, developer/manufacturer/vendor, temporary, and service);

b. Assigns account managers for information system accounts;

c. Establishes conditions for group and role membership;

d. Specifies authorized users of the information system, group and role membership, and access authorizations (i.e., privileges) and other attributes (as required) for each account;

e. Requires approvals by (applicable information system managers) for requests to create information system accounts;

f. Creates, enables, modifies, disables, and removes information system accounts in accordance with (the processes defined in the OS Standard Operating Procedures for Information Security: Access Control document (see Section AC-2));

g. Monitors the use of information system accounts;

h. Notifies account managers:

   1. When accounts are no longer required;
   2. When users are terminated or transferred; and
   3. When individual information system usage or need-to-know changes;

i. Authorizes access to the information system based on:

   1. A valid access authorization;
   2. Intended system usage; and
   3. Other attributes as required by the organization or associated missions/business functions;

j. Reviews accounts for compliance with account management requirements [at least every 180 days]; and

k. Establishes a process for reissuing shared/group account credentials (if deployed) when individuals are removed from the group.

For CSP Only: AC-2 (j) [at least annually]

## TDP Implementation
a. The TDP system accounts are OFA System Admin, OFA Admin, OFA Regional Staff, ACF OCIO and (STT) Data Analyst.  TDP Implementation is completed by the Developers.

b. The OFA System Admin is responsible for managing the system accounts.  

c. Members in the roles of OFA System Admin, OFA Admin, OFA Regional Staff, ACF OCIO and (STT) Data Analyst are based on their job responsibilities.  The activities of each of the roles can be found in [AC-05](../ac-5/index.md)

d. The roles in the TDP system follow the principles of least privilege and separation of duties as described in [AC-05](../ac-5/index.md) and [AC-06](../ac-6/index.md).  Users within each role inherit the responsibilities, duties, and permissions of that role.  Outside of the TDP system, groups/roles/access for Developers are enforced through the access management features of GitHub and Cloud.gov.

e. All internal (i.e. ACF) users who require access to TDP must authenticate via ACF AMS with their PIV/CAC credentials. All external (i.e. non-ACF) users who require access to the TDP application must create a Login.gov account.  In order to be able to submit/view reports within the TDP application, users must submit a request.  The OFA system admin reviews and approves the request.  Once the request is approved, the user will be able to perform their assigned duties.  Additionally, the OFA system admin approves requests for accounts to GitHub and Cloud.gov as well.

f. The OFA System Admin is the only role that has the ability to assign roles to new users, update profile information, inactivate and reactivate users.

g. The OFA System Admin reviews the list of TDP application users on a monthly basis and/or when the status of a user is changed to inactive or terminated.  Additinally, Django Admin provides logs of user actions that can be monitored and reviewed, and Cloud.gov provides tools to audit the logs of Developer actions.

h. For the OFA MVP, internal processes are done to satisfy this, including the OFA system admin manually checking the list of active/expected users with those registered in the system on a periodic basis.

i. All users must submit a request through the TDP application to be able to perform their duties.  Users identify their intended system usage in the request.  The OFA system admin reviews all requests and, as appropriate, assigns user permissions. 

j. The OFA system admin reviews the TDP application users list every 180 days.

k. Not Applicable - there are no shared/group account credentials in the TDP application.