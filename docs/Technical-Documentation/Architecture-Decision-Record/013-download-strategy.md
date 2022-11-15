# 13. Download Strategy

Date: 2021-04-06 (_Updated 2022-02-07_)

## Status

Accepted

## Context

In [this issue](https://github.com/raft-tech/TANF-app/issues/771) we are investigating the use of pre-signed URLs to determine whether there are security issues with the approach.

We had originally implemented pre-signed URLs for downloading files because the system would need to download the files from S3 and then download them again to the client, using resources on the backend for every download. This would not cause a problem in this stage of development, but when the backend will be charged with parsing data from potentially large files, those system resources would become more precious. Using pre-signed URLs takes the added pressure off of the backend entirely.

## Decision

We believe the use of time/IP address limited signed URLs is a reasonably secure approach to downloading files from S3. However, we also believe that it may cause issues with our ATO approval as the data is highly sensitive. Furthermore, 18F published a recommendation today, [recommending to not use pre-signed URLs](https://engineering.18f.gov/security/cloud-services/) for FISMA High projects.

In our investigation we discovered a way that we can [securely download the files from the backend while [streaming the files](https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py#L83) directly from S3 to the client, taking any pressure off of resources needed for parsing files on the backend. 

In light of these facts we have decided to shift our efforts to download files from the backend.

## Consequences

**Benefits**
- Ensures access to S3 is completely hidden from the frontend.
- Cuts down on latency in passing signed signatures back and forth.
- Simplifies frontend logic
    - Fewer requests get made, reducing the complexity of redux actions.
    - it is more obvious to the user where the file is (it is no longer potentially uploaded, but unsubmitted)
- Allows us to leverage django storage which makes it easier to reason about the files in our database.
- Reduces number of endpoints required on the backend.
- Eases path to ATO.

**Risks**
- None that the team is aware of at this time. 

## Notes
**<details><summary>Data Files Download Architecture</summary>**

This application provides a secure means to both store and download files from
AWS S3 through the use of an open source Django plugin `django-storages`. By
utilizing built in Django classes in conjunction with this plugin we can enable
downloading of these files through an API endpoint without having to write
the files to the local storage of the server, thus removing a performance
penalty that would be incurred by essentially downloading the file twice.

### Process Flow
![](diagrams/tdp-data-file-download-api.png)

### S3 File Storage
`django-storages` provides a custom Storage Backend for Django that enables
storing files in S3 instead of on the local Django server. This application
has historically used this library for collection and storage of static files
served for the Django admin. However, with this change we will move towards
using this to interface with the Data Files as well.

#### S3Boto3Storage
This storage backend provides the support for opening files in read or write
mode and supports streaming (buffering) data in chunks to S3 when writing.

[Source code](https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py#L233)

#### S3Boto3StorageFile
This class extends Django's File class to support file streaming using the
[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
library's multipart uploading functionality. It provides a wrapper to access
the buffered file contents.

[Source code](https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py#L79)

#### InMemoryUploadedFile
This file class is provided by Django and represents a file that has been
uploaded into memory via streaming. The file returned by `django-storages` for
a given FileField associated with an S3 object will leverage the functionality
of this class to prevent needing to write the file to disk, resulting in a more
performant download experience.

[Source code](https://github.com/django/django/blob/main/django/core/files/uploadedfile.py#L78)

### ReportFile model
This is a custom model for the application that stores information about a
Data File that has been uploaded to the system. To leverage the features
mentioned above this model will have a [FileField](https://docs.djangoproject.com/en/3.2/ref/models/fields/#filefield)
on the model which is linked to S3 via `django-storages`. From the perspective
of the API, this will make downloading the file as simple as calling the `open`
method on the file property of a `ReportFile` instance.
</details>
