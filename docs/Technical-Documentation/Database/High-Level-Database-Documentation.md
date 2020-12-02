# High-level database documentation

### How

This project uses Postgres as its database management system. Postgres is a free, open-source, relational database management system (RDBMS).

Our Postgres infrastructure is managed via the Cloud.gov Platform as a Service, which in turn uses Amazon Web Services infrastructure. For more documentation on Cloud.gov relational databases, see: https://cloud.gov/docs/services/relational-database/.

See the `deploy-cloudgov-docker.sh` script for details on Cloud.gov Postgres provisioning and deployment.

### What

For a physical data model including data elements, relationships, columns and column types, see the project's [Entity Relationship Diagram](./tdp-erd.png).

# High-level object storage documentation

### How

This project intends to use the Cloud.gov platform's Amazon Web Service S3 object storage to store flat files.

For more information on Cloud.gov's S3 object storage, see: https://cloud.gov/docs/services/s3/.

### What

For information about the data files intended for upload, see [Background/Current-TDRS.md](../../Background/Current-TDRS.md).

* **Format**: .txt
* **Update frequency**: Quarterly (with revisions)
* **Record structure**: See [Data Layouts](../../Background/Current-TDRS.md#data-layouts).
* **File sizes**: File size ranges for 199/209 data files are as follows:
  * Section 1: 123kb - 50,000kb
  * Section 2: 14kb - 2,000kb
  * Section 3: 1kb - 2kb
  * Section 4: 1kb - 2kb
