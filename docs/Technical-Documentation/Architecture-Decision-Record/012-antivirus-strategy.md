# 12. Anti-virus Strategy Change

Date: 2021-04-01 (_Updated 2021-12-28_)

## Status

Accepted

## Context

Our original plan was to upload files to S3 using signed URLs from S3, and checking the files' headers to determine whether or not it was, in fact, a text file. Further research has revealed that there is no fool proof way of doing this and a malicious user would be able to spoof a virus as a text file.

## Decision

Instead of using a signed URL and sending the file directly to S3, we will instead send the file to the backend and scan it with Clam AV before sending it to S3. In the event there is a virus, we will destroy the file on the backend immediately and return an error to the frontend. 

By using the [ClamAV REST server](https://github.com/ajilaag/clamav-rest) implementation we are able to scan files for viruses and malicious behavior. Additionally, Anti-Virus definitions are kept up to date automatically by use of the included [freshclam](https://www.clamav.net/documents/signature-testing-and-management#freshclam) tool which automatically downloads and updates an internal database of virus signatures using the official ClamAV source.

In addition to this, the frontend is able to reliably determine if a file is a binary file. The client will check submitted files for this and immediately return an error to the user. These files will not be sent to the backend.

## Consequences

**Benefits**
- Less network requests for user
- More timely user feedback
  - We can now tell the user if the file is rejected before it even gets to S3
  - Also removes the need for async notifications like email
- More assurance that the file is not malicious
  - ClamAV is already used for this purpose in other government projects with ATO (e.g. [Head Start TTADP](https://github.com/HHS/Head-Start-TTADP/wiki/TTAHUB-System-Operations))
- Provides an easier foundation for future planned efforts (such as parsing file contents)
- Compliance is more familiar with this approach

**Risks**
- Introduces slight risk of files not getting saved to S3 if an error occurs before our API sends it to S3
- This approach will require a heavier lift to accomplish (vs the signed URL strategy), but the benefits to the new approach make it worth the effort

## Notes