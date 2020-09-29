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

**Snyk Issue Discovered**

 Multiple issues with `Node-Sass` due to the `libsass` dependancy 

 **Snyk Documentation:**

This is being tracked in the `.snyk` ignore file hosted in the `tdrs-frontend` directory [snyk ignored vulnerability file](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-frontend/.snyk).


**Resolution:**
Attempted to resolve the `node-sass` dependency `libsass` vulnerabilities as the `.synk` file ignore date expired on `9/27/2020`. Forcing a resolution of the github repo to use the latest `libsass` version did not resolve vulnerabilities discovered by Snyk.
The maintainers of the `node-sass` repo are aware of the vulnerabilities:
https://github.com/sass/node-sass/issues/2795

They are not addressing the `libsass` issue until the `5.0` release of `node-sass` which does not have a target date:
https://github.com/sass/node-sass/issues/2685#issuecomment-547870498

**Actions:**
 There is still no reported resolution from Synk, therefore the ignore setting will be extended to `10/29/2020` for these existing issues.