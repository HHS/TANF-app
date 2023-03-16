# Connect-to-Service dependencies

From [this github](https://github.com/cloud-gov/cf-service-connect) which has some of these instructions.



## For OSX
1. Install psql

> `brew install postgresql`

2. Install plugin

> `cf install-plugin https://github.com/cloud-gov/cf-service-connect/releases/download/1.1.0/cf-service-connect-darwin-amd64`

[Releases](https://github.com/cloud-gov/cf-service-connect/releases), if needed.

3. Use connection

> `cf connect-to-service tdp-backend-<name> tdp-db-dev`

