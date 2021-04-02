# 12. Anti-virus Strategy Change

Date: 2021-04-01 (yyyy-mm-dd)

## Status

Accepted

## Context

Our original plan was to upload files to S3 using signed URLs from S3, and checking the files' headers to determine whether or not it was, in fact, a text file. Further research has revealed that there is no fool proof way of doing this and a malicious user would be able to spoof a virus as a text file.

## Decision

Instead of using a signed URL and sending the file directly to S3, we will instead send the file to the backend and scan it with Clam AV before sending it to S3. In the event there is a virus, we will destroy the file on the backend immediately and return an error to the frontend. 

In addition to this, the frontend is able to reliably determine if a file is a binary file. The client will check submitted files for this and immediately return an error to the user. These files will not be sent to the backend.

## Consequences

**Pros**

- Less Network Requests for User
- More timely User feedback
  - We can now tell the user if the file is rejected before it even gets to S3
  - Also removes the need for async notifications like email
- More assurance that the file is not malicious
  - ClamAV is already used for this purpose in other government projects with ATO 
- Provides an easier foundation for future planned efforts (such as parsing file contents)
- Compliance is more familiar with this approach

**Cons**

- Introduces slight risk of files not getting saved to S3 if an error occurs before our API sends it to S3
- This approach will require a heavier lift to accomplish, but the benefits to the new approach make it worth the effort

## What Needs To Be Done

- Frontend: Adjust upload to send to backend and wait for response instead of S3
- Backend: Endpoint to receive files and methods to handle scanning, update the database and send to S3
- DevOps: Set up application to host Clam AV for virus scanning and configure to receive requests from the backend
