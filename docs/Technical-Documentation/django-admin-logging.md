# Django Admin Logging

The TDP application logs various activities in the Django Admin section of the backend application. This document details the types of logs that can be found under the `Administration > Log entries` section of the Django Admin.

## Admin Interface

### Themes
Any changes made to the admin theme by a user through Django admin will be logged with the username and fields changed.

## Authentication and Authorization

### Groups

Any changes to groups made through the Django admin will be logged with the username and fields changed.

## Data Files

### Submissions
For each successful DataFile submission made through the UI a log entry will be created with the number of files submitted along with the filename, username and activity.

## Security

### Clam AV File Scans

The ClamAV Client defined in the Security model stores the results of all files scanned by ClamAV and adds an associated LogEntry that is viewable in the Django admin.

This is done through the use of the model `ClamAVFileScan` which represents an individual file scan performed by ClamAV. When the `ClamAVClient.scan_file` method is called it will create an instance of this model along with a LogEntry instance that is tied to the ClamAVFileScan instance. In the event the scan is successful and a DataFile is produced, it will also be linked to this ClamAVFileScan so that the scanned file can be retrieved as necessary for auditing purposes. In the event the scan is rejected, we will not store the file itself so the data_file link will be empty for these records.

### Nightly OWASP ZAP Scans

The Circle CI configuration for this repo declares a workflow which runs nightly to perform an automated penetration test using the OWASP ZAP scanner tool.

The results of these nightly scans are stored permanently through the use of the model `OwaspZapScan` which represents an individual security scan performed by OWASP ZAP. After Circle CI runs the nightly OWASP scans against the deployed staging site it will run a Cloud Foundry Task on the tdrs-backend-staging application in Cloud.gov. This task will execute a Django management command `process_owasp_scan` with the relevant build number and pass/fail/warn metrics. This management command will download all Circle CI Artifacts for the given build number and create the relevant `OwaspZapScan` instances with the HTML report, app target, and supplied metrics.

Since this repo is open source, the Circle CI artifacts are publicly available for 30 days and no authentication is required to retrieve them from the V2 Circle CI API so no new environment variables or secrets are needed in the project. The long term storage of the HTML reports will be in the private S3 instance used to store Data Files, and will only be accessible to users in the groups OFA Admin or OFA System Admin through the Django Admin. We could easily move this to a different bucket in the same S3 service or a different service, if desired.

The metrics provided to the CF task originate from modifications to the zap-scanner.sh script. Specifically, if the nightly argument is passed for the script environment then the output from the zap-full-scan.py script is extracted from the Docker output and formatted into specific metrics for pass_count, fail_count and warn_count. This is done for each app target (frontend vs backend) and exported to the Circle CI job environment variables (via BASH_ENV). These environment variables live only for the duration of the job and never need to be manually set.

## States, Tribes And Territories

### Regions

Any changes to regions made through the Django admin will be logged with the username and fields changed.

### STTs

Any changes to STTs made through the Django admin will be logged with the username and fields changed.

## Users

Any changes to users made through the Django admin will be logged with the username and fields changed.
