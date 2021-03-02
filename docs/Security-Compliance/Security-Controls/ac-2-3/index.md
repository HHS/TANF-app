# Access Control
## AC-02(03) - DISABLE INACTIVE ACCOUNTS  

The information system automatically disables inactive accounts after [a maximum of 60 days of inactivity].  

For CSP Only: AC-2 (3) [90 days for user accounts]. 
AC-2 (3) Additional FedRAMP Requirements and Guidance:  
Requirement: The service provider defines the time period for non-user accounts (e.g., accounts associated with devices).  The time periods are approved and accepted by the Joint Authorization Board (JAB)/AO. Where user management is a function of the service, reports of activity of consumer users shall be made available.

### TDP Implementation  

The System Admin reviews the list of TDP application users on a monthly basis and/or when the status of a user is changed to inactive or terminated. Inactive accounts are removed from the system manually if their status has changed.

The Django Admin interface tells us when a user last logged in to the TDP Application, so we can determine the last date of a user's activity by checking the user's profile there.

Because most of the users of the TDP application will only need to log in every 90 days, we will disable inactive accounts after 180 days.

#### Related Files  
