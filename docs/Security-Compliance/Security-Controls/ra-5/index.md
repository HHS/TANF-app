# Risk Assessment
## RA-05 - VULNERABILITY SCANNING

The organization:  
a. Scans for vulnerabilities in the information system and hosted applications (Assignment: organization-defined frequency and/or randomly in accordance with organization-defined process) and when new vulnerabilities potentially affecting the system/applications are identified and reported;  

b. Employs vulnerability scanning tools and techniques that facilitate interoperability among tools and automate parts of the vulnerability management process by using standards for:  
   1. Enumerating platforms, software flaws, and improper configurations;  
   2. Formatting checklists and test procedures; and  
   3. Measuring vulnerability impact;  

c. Analyzes vulnerability scan reports and results from security control assessments;  

d. Remediates legitimate vulnerabilities (Assignment: organization-defined response times) in accordance with an organizational assessment of risk; and  

e. Shares information obtained from the vulnerability scanning process and security control assessments with (Assignment: organization-defined personnel or roles) to help eliminate similar vulnerabilities in other information systems (i.e., systemic weaknesses or deficiencies).  

### TDP Implementation

a. As part of the TDP Test Plan, security scans are completed on an ongoing basis, throughout the Continuous Integration (CI).  Automated scans are run on every push, pull request and merge on GitHub.  

b. Security scanning is completed using OWASP ZAP dynamic security scans and Dependabot vulnerability dependency scanning.  Dependabot will automatically open Pull Requests if there is a vulnerability dependency.  If there are no findings, no Pull Requests will be opened.  OWASP Zap scans are the last step for each CI run.  The results for the scans are summarized and accessed through CircleCI.  If vulnerabilities are found in the scan results, the code will be prevented from being deployed until the vulnerabilities are remediated.

c. Summaries of the security scan reports are reviewed in CircleCI. (see screenshot of summaries of scan reports below)  

![screenshot - Summaries of security scan reports](images/owasp.png)

d. Summaries of the security scan reports are available in CircleCI.  If there are any vulnerability dependencies found by Dependabot, pull requests are automatically opened.  These pull requests are reviewed and remediated as necessary.

e. Information from the scan reports and control assessments are shared with the appropriate security stakeholders and are available for review in CircleCI. 
	
#### Related Files
