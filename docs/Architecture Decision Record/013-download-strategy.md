# 13. Download Strategy

Date: 2021-04-06 (yyyy-mm-dd)

## Status

Approved

## Context

In [this issue](https://github.com/raft-tech/TANF-app/issues/771) we are investigating the use of pre-signed URLs to determine whether there are security issues with the approach.

We had originally implemented pre-signed URLs for downloading files because the system would need to download the files from S3 and then download them again to the client, using resources on the backend for every download. This would not cause a problem in this stage of development, but when the backend will be charged with parsing data from potentially large files, those system resources would become more precious. Using pre-signed URLs takes the added pressure off of the backend entirely.

## Decision

We believe the use of time/IP address limited signed URLs is a reasonably secure approach to downloading files from S3. However, we also believe that it may cause issues with our ATO approval as the data is highly sensitive. Furthermore, 18F published a recommendation today, [recommending to not use pre-signed URLs](https://engineering.18f.gov/security/cloud-services/) for FISMA High projects.

In our investigation we discovered a way that we can [ecurely download the files from the backend while [streaming the files](https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py#L83) directly from S3 to the client, taking any pressure off of resources needed for parsing files on the backend. 

In light of these facts we have decided to shift our efforts to download files from the backend.

## Consequences

**Pros**
- Ensures access to S3 is completely hidden from the frontend.
- Cuts down on latency in passing signed signatures back and forth.
- Simplifies frontend logic
    - Fewer requests get made, reducing the complexity of redux actions.
    - it is more obvious to the user where the file is (it is no longer potentially uploaded, but unsubmitted)
- Allows us to leverage django storage which makes it easier to reason about the files in our database.
- reduces number of endpoints required on the backend.
- Eases path to ATO.


**Cons**
- Additional effort on the frontend and backend will be required for this shift. However, it's a fairly small lift for both.
- The original con of added resource expenditure on the backend is no longer an issue.
