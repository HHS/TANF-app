# Sprint 4 Frontend Vulnerability Report (09/29/2020) 

 This is a report of the vulnerabilities discovered during Sprint 4, the source of the notification, and the resolution implemented in response to it. 
 

**Snyk Issue Discovered:**
Upgrade react-scripts dependency node-forge from `0.9.0` to `0.10.0` (Recommendation) 

**Snyk Documentation:**
Details of the issue can be found here:

https://snyk.io/vuln/SNYK-JS-NODEFORGE-598677

**Resolution:**
Define a resolution in the frontend project `package.json` to override any dependency on node-forge `0.9.0` to default to `0.10.0`.

**Actions:**
The `package.json` file and `yarn.lock` now default to use node-forge `0.10.0` when the library is needed. 
----
 

 