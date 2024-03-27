# AWS Elastic Search Proxy

## Background
TDP leverages the Elastic stack to provide fast search capabilities along with powerful visualizations to provide OFA insight into the data collected from STTs. TDP deploys it's own Kibana instance and relies on Cloud.gov and AWS to provides Elastic Search as a service. Because TDP leverages Elastic Search as a service, the app is subject to constraints imposed by this choice.

## AWS ES Proxy
TDP leverages Elastic Search as a service through Cloud.gov/AWS. However, AWS has specific requirements to accept requests flowing to their services. That is, all requests coming to an AWS hosted service must be signed according to the [AWS Signature Version 4](https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html) signing method. Therefore, when deploying your own services that need to connect to an AWS service (Kibana in our case), you must also deploy/introduce a proxy application that will sign your app's requests appropriately. AWS provides [this resource](https://aws.amazon.com/blogs/security/how-to-control-access-to-your-amazon-elasticsearch-service-domain/) on how an app can have it's requests signed appropriately. Using this resource, the engineering team introduced the [AWS ES Proxy](https://github.com/raft-tech/aws-es-proxy) which is a V4 signing proxy forked off of [this proxy](https://github.com/abutaha/aws-es-proxy). The engineering team forked this repo to allow for the modification of ports that the proxy opens during it's deployment.

The AWS ES Proxy sits between TDP's Cloud.gov/AWS ES service instance and any other service that would like to communicate with the ES service. The proxy obtains all the required information to sign each request coming to it via environment variables in the deployed environment. The proxy is extremely lightweight, can handle many concurrent requests, and per our configuration, only performs signing the incoming request and returning the response to the original requester.


Since the image does not hold any credentials and only imports them as environment variables, the docker image itself is considered to be secured and can be housed in external hub.
