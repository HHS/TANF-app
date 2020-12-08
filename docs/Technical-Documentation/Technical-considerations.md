## [Cloud.gov](https://cloud.gov/)
Cloud.gov is a cloud-foundry-based platform-as-a-service hosted in Amazon Web Services GovCloud-based that provides infrastructure monitoring and maintenance. A [prototyping account](https://cloud.gov/pricing/) is already procured for OFA. Cloud.gov has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. FedRAMP is a standardized federal security assessment for cloud services, and the FedRAMP ATO helps agencies by providing confidence in the security of cloud solutions and security assessments. In addition to compliance features such as inherited security controls, it provides organizational management and service workers to allow for secure continuous deployment through configurations-as-code.

Cloud.gov supports many modern software development frameworks so the contractor team does not need to continue in Python/Django if they prefer another language/framework.

## [Login.gov](https://login.gov)
The TDRS application requires strong multi-factor authentication for the states, tribes, and territories and Personal Identity Verification (PIV) authentication for OFA staff. Login.gov can meet both of these requirements and HHS already has an IAA for this service. Login.gov has a FedRAMP ATO on file. The use of the login.gov system will help the new TDRS system address NIST SP 800-53 AC-2 and AC-3 security controls.


## GitHub
TDRS will use Github as its SaaS based source version control manager to allow for tracked collaborative software development.

## CircleCI
CircleCI This is a continuous integration and delivery SaaS tool to ensure quality assurance of 18F developed products. It is used to automate builds, testing, and deploys from GitHub. CircleCI has an FedRAMP ATO on file.

## Known data validation constraints
Data reports are checked by TDRS to ensure that they are in the right format and meet the data validation rules. There are a couple reasons why an error can occur. Here's the ones we've identified so far:

* Out-of-range errors: When an invalid value is submitted. Example: submitting 3 for the gender field, which only accepts values of 1 or 2.

* Cross-element errors: When data elements show conflicting information within the same section / file . Example: A family's benefits come from a federal funding stream, but is then later shown to be exempt from federal time limits.

* Cross-section errors: When data elements show conflicting information across sections / files.

The most common errors are out-of-range errors and cross-element errors.

OFA provides documentation on current data validation rules on their website. However, the current validation still lets bad data in. We'll need to identify the validation we want rather than tracing what errors are currently produced by the system .

### Existing data constraints for the current system:
* [Final TANF & SSP-MOE Data Reporting System Transmission Files Layouts and Edits](https://www.acf.hhs.gov/ofa/resource/tanf-acf-pi-2017-05)

* [TANF-ACF-PI-2017-05 (Form ACF-199, TANF Data Report, and Form ACF-209, SSP-MOE Data Report)](https://www.acf.hhs.gov/ofa/resource/tanfedit/index#transmission-file-header)

* [Tribal TANF Data Coding Instructions](https://www.acf.hhs.gov/ofa/resource/tribal-tanf-data-coding-instructions)