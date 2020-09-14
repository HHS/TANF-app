# Sprint 3 Backend Vulnerability Report (09/11/2020) 

 This is a report of the vulnerabilities discovered during Sprint 3, the source of the notification, and the resolution implemented in response to it. 


**Snyk Issue Discovered:** 
Insecure Permissions  (High Severity) 

**Snyk Documentation:**
https://snyk.io/vuln/SNYK-PYTHON-DJANGO-609368 

**Resolution:**
Upgrade Django from version 3.1 to 3.1.1 

**Actions:**
Backend DJango version was upgraded to version 3.1.1  with no adverse reactions in the code base. 

----

**Snyk Issue Discovered:**
MPL-2.0 license (Medium Severity) 

**Snyk Documentation:**
https://spdx.org/licenses/MPL-2.0.html 

**Resolution:**
No immediate resolution, this was deemed as a false positive and after reviewing the Snyk License compliance management blog it was deemed OK to ignore these warnings. 
https://snyk.io/blog/license-compliance-management. 

**Actions:**
Manually configure the Snyk.io project settings under  the Raft-Tech and HHS respective dashboards to ignore warnings in regards to the MPL-2.0 license. 

----

**Snyk Issue Discovered:**
LGPL-2.1 license (Medium Severity) 

**Snyk Documentation:**
https://spdx.org/licenses/LGPL-2.1-only.html 

**Resolution:**
No immediate resolution, this was deemed as a false positive and after reviewing the Snyk License compliance management blog it was deemed OK to ignore these warnings. 
https://snyk.io/blog/license-compliance-management/ 

**Actions:**
Manually configure the Snyk.io project settings under  the Raft-Tech and HHS respective dashboards to ignore warnings in regards to the LGPL-2.1 license. 

**Snyk Issue Discovered:**

LGPL-3.0 license (Medium Severity) 

**Snyk Documentation:**
https://spdx.org/licenses/LGPL-3.0-or-later.html 

**Resolution:**
No immediate resolution, this was deemed as a false positive and after reviewing the Snyk License compliance management blog it was deemed OK to ignore these warnings. 
https://snyk.io/blog/license-compliance-management/ 

**Actions:**
Manually configure the Snyk.io project settings under  the Raft-Tech and HHS respective dashboards to ignore warnings in regards to the LGPL-3.0 license.