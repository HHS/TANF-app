# System and Communications Protection
## SC-08 - TRANSMISSION CONFIDENTIALITY AND INTEGRITY

The information system protects the [Selection (one or more): confidentiality; integrity] of transmitted information.  

For CSP Only  
SC-8 [confidentiality AND integrity]  

### TDP Implementation

Data file uploads and downloads with PII are transmitted through connections encrypted via 
[Transport Layer Security (TLS)](https://www.cloudflare.com/learning/ssl/transport-layer-security-tls/).

All data transmitted between the frontend and backend of the web application are also
encrypted via TLS.

For our TLS connections, clients connect to cloud.gov through [AWS load balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-security-policy-table.html) which implement the [ELBSecurityPolicy-TLS-1-2-2017-01](https://cloud.gov/docs/compliance/domain-standards/#ssltls-implementation)

