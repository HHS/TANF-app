# Configuration Management
## CM-07(02) - PREVENT PROGRAM EXECUTION 

The information system prevents program execution in accordance with [list of authorized software programs; list of unauthorized software programs; rules authorizing the terms and conditions of software program usage].  

CM-7 (2) Additional FedRAMP Requirements and Guidance:  
Guidance: This control shall be implemented in a technical manner on the information system to only allow programs to run that adhere to the policy (i.e., white listing).  This control is not to be based off of strictly written policy on what is allowed or not allowed to run.  

### TDP Implementation
ACF reviews the TDP cloud.gov environments at least annually to identify unnecessary and/or nonsecure functions, ports, protocols, and services; and disables functions, ports, protocols, and/or services deemed to be unnecessary and/or unsecure within the information system.  Please refer to the [architecture decision record](https://github.com/HHS/TANF-app/tree/main/docs/Architecture%20Decision%20Record), [security compliance documents](https://github.com/HHS/TANF-app/tree/main/docs/Security-Compliance), and other [technical documentation](https://github.com/HHS/TANF-app/tree/main/docs/Technical-Documentation) for additional implementation information.
[Architectural decision record 012](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/012-antivirus-strategy.md) captures information regarding the TDP virus scanning process and includes a description for how anti-virus definitions will be kept up to date automatically. These definitions will be used to isolate known malicious files and prevent them from being uploaded into the system.

#### Related Files

