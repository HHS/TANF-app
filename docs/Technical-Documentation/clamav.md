# CLAMAV 

In order to have one CLAMAV instance, existing in prod, the Nginx router is created
for CLAMAV to forward the traffic from 'dev' and 'staging' spaces into
prod space, where the CLAMAV service exists.

## Deploy Nginx instance
To route the clamav traffic to clamav in prod, each space needs to have one instance of _Nginx Router_ which routes traffic to clamav.

In order to deploy the nginx router instance, change your directory to `tdrs-backend/clamav-router/` and run the following command while logged into the target space:


>`cf push tdp-clamav-nginx-${cf-shortened-space} -f manifest.yml --no-route`

, where _cf-shortened-space_ can be : _dev_, _staging_, or _prod_. 

The instance name then will be set as an environment variable to redirect each instance traffic. This will deploy the nginx instance to the target environment.
 
## Further communication configurations

### Setup Individual Instances

First, set the environment variable __AV_SCAN_URL__ as follows:
```
Environment variable name: AV_SCAN_URL
Environment variable value: http://{nginx_instance}.apps.internal:9000/scan/
```

### Add network policy from _{tdp-clamav-nginx}_ to clamav in prod
To enable traffic between the "__nginx instance__" and "__clamav instance in production__", we need to add the network policiy and route between the two:

>`cf add-network-policy {nginx_instance} "clamav-rest" -s "tanf-prod" --protocol tcp --port 9000`
e.g: `{nginx_instance_name} = tdp-clamav-nginx-dev`

### Add network policy from _{backend_instance}_ to _tdp-clamav-nginx_

>`cf add-network-policy {backend_instance} {nginx_instance} --protocol tcp --port 9000`

where e.g: `backend_instance = tdp-backend-develop`

### Add route for _tdp-clamav-nginx_

 Note: Make sure to delete (if existing) routes that are not being used. In some rare cases, a mal-assigned network policy can interfere with outgoing traffic. As an example, a policy like 
 >`cf delete-route app.cloud.gov --hostname tdp-frontend-staging`

Add route:

>`cf map-route {nginx_instance} apps.internal --hostname {nginx_instance}`