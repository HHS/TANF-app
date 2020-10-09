# Sprint 4 Bckend Vulnerability Report (10/09/2020) 

 This is a report of the vulnerabilities discovered during Sprint 4, the source of the notification, and the resolution implemented in response to it. 
 
**Snyk Issue Discovered:**
Upgrade django-filter to version 2.4.0 or higher to resolve medium vulnerability.

**Snyk Documentation:**
Details of the issue can be found here:

https://app.snyk.io/vuln/SNYK-PYTHON-DJANGOFILTER-1013846

**Resolution:**
Pipfile and Requirements.txt references to django-filter need to references version 2.4.0

**Actions:**
Pipfile and Requirements.txt references to django-filter has beed upgraded to references version 2.4.0
----