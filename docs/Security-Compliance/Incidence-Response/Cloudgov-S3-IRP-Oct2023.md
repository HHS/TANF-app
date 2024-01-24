# Response Strategy for Cloud.gov Security Incident (Oct 2023)

TDP is hosted in cloud.gov, and our team was recently informed of a security incident that potentially exposed the secret keys that are used to access our AWS S3 buckets, which are used to store raw data files submitted through the system. 

While, there's been no indication from cloud.gov or our audit logs of unusual activity on TDP, we were advised to rotate the S3 bucket access keys.

This document captures the steps we followed to respond to this incident, from the point of initial notification to resolution. These steps should be repeated in the event of another incident on platform.

## Summary of the security incident reported by cloud.gov support on 10/17/2023

> Dear cloud.gov customer,
>
> We are writing to notify you of an incident involving brokered service credentials on the cloud.gov platform. We do not believe there was any impact to confidentiality, integrity, or availability of your data as a result of this incident, but we are sharing this information with you so your teams can assess the risk and take action as needed. 
> 
> **What happened?**
On Friday October 16, a cloud.gov engineer found that the cloud.gov S3 broker, which manages the S3 buckets that customers broker using the platform, was printing AWS secret access keys in clear text to its logs. Specifically, whenever a customer created a “binding” between the bucket and one of their applications, the newly created key was written to the broker log and indexed by our log management system. 
>
> **How has cloud.gov responded?**
>We have modified the S3 broker to stop printing these credentials and we have removed all log lines containing the keys from our active log indices. However, the log lines will remain in our long-term log archives due to our retention obligations. 
>
>**What is the scope of the issue?**
>
>The relevant code and configuration was introduced more than six years ago. Because of the time span, it is likely that all current and past brokered S3 buckets are affected. 
>
>**Next steps**
>Because of the factors listed above, although there was no public compromise of your credentials, we recommend rotating your access keys at this time. 
>
>You can rotate your keys by un-binding and re-binding your S3 buckets to each bound application. In a terminal, using the cf command line tool: 

               
                       # list all spaces in your organization
                       cf spaces

                       # target a space
                       cf target -s SPACE-NAME

                       # list all s3 services in the space and the applications bound to them.
                       cf services | grep s3

                       # for each application bound to the service, un-bind it from the service, re-bind it, and restage it.
                       cf unbind-service YOUR-APPLICATION YOUR-SERVICE
                       cf bind-service YOUR-APPLICATION YOUR-SERVICE
                       cf restage YOUR-APPLICATION
               
        
> Note that re-staging your application may cause downtime. 
> You will also need to delete and recreate any service keys for your S3 services:

               
                       # delete and recreate service keys for each service
                       cf delete-service-key SERVICE SERVICE_KEY
                       cf create-service-key SERVICE SERVICE_KEY
               
        
> **Is my data at risk?**
Cloud.gov does not believe your data is at risk. The logging system is designed to segregate logs from customer tenant access, and we have no indications of unauthorized access. We are continually monitoring our system and will reach out to your team directly if we detect any suspicious activity.
>
>**Why did this happen?**
>Cloud.gov will hold an incident postmortem in the coming weeks to discuss the root cause of this incident and how similar incidents will be prevented in the future. We will share our findings and corrective actions at that time.
> Please feel free to reach out to our support team at support@cloud.gov if you have questions or concerns. 

> **Update from cloud.gov on 10/31/2023**
> First, here are some corrections and updates to the original email: 
> * The original email said that the incident occurred on Friday October 16. The correct date is Friday October 13. 
> * The original email said, “[Whenever] a customer created a “binding” between the bucket and one of their applications, the newly created key was written to the broker log”. This is correct but incomplete; credentials were also written to the log when service keys were created, not only when bindings were created. The remediation guidance under “Next steps” includes a section addressing service key rotation and remains the same. 
> * If you are still working on rotating keys that are created by service bindings, please be aware that if you have enough memory in your organization for additional application instances, you can run cf restage APPNAME --strategy rolling to restage your applications without downtime. 
> * Lastly, we have posted a public incident and postmortem to our status page. You can view the write-up here. The cloud.gov team is making several changes to the platform to reduce the likelihood of keys being sent to the logging system, and to reject them from the logging system and alert platform operators if keys are detected in logs. 


---

## Response Strategy

### 1. User Reporting of Security Incident 

The cloud.gov platform team reported the security incident (copied above) to the TDP system owner and government technical monitor (GTM) via e-email on 10-17-2023. 

### 2. TANF Data Portal (OFA-Raft) Team Procedures and Reporting

Upon confirming receipt of the reported incident, TDP GTM activated the [secret key incident response communication protocol](https://github.com/HHS/TANF-app/blob/main/docs/Security-Compliance/Incidence-Response/Secret-Key-Mgmt.md/#communication-protocol-if-secret-keys-are-leaked).

On 10-18-2023, TDP GTM and the development team (responding team) met to assess the incident and plan remediation steps. *This information was also shared with the ACF IRT via e-mail on 10-18-2023.* 

Please note the following assessment and remediation plan: 
* the access keys were printed out only to the platform’s logs, which only authorized personnel from cloud.gov can see. There was no reported exposure of these keys outside of cloud.gov personnel
* A [review of historic logs via cloud.gov](https://cloud.gov/docs/deployment/logs/#web-based-logs-with-historic-log-data) for the backend production app (`tdp-backend-prod`) during the time period of the security incident does not show any evidence of unauthorized access to these buckets; 
* Additionally,  there is no evidence of any content missing from or added to TDP's S3 buckets.
* As recommended by cloud.gov platform team, the TDP GTM will be following the guidance above to rotate the access keys. This change will take less than 4 hours; therefore, we do not anticipate needing to activate the TDP contingency plan (which is to be activated when the system will be down for more than 1 day). 

### 3. Mitigation steps

The TDP GTM followed the mitigation steps below for the TDP staging and prod environments. 

1. Save a backup of env variables for tdp-backend-staging
    `cf env tdp-backend-staging > backupstaging`
    
2. Follow steps outlined above to rotate s3 keys in staging (`hhs:main` branch)

    ```
    # list all spaces in your organization
    cf spaces
    
        # output
        Getting spaces in org hhs-acf-ofa as alexandra.pennington@acf.hhs.gov...

        name
        tanf-dev
        tanf-prod
        tanf-staging

    # target a space
    cf target -s tanf-staging

        #output
        API endpoint:   https://api.fr.cloud.gov
        API version:    3.149.0
        user:           alexandra.pennington@acf.hhs.gov
        org:            hhs-acf-ofa
        space:          tanf-staging


    # list all s3 services in the space and the applications bound to them.
    cf services | grep s3

        #output
        tdp-datafiles-develop     s3                          basic-sandbox          tdp-backend-develop                        create succeeded   s3-broker
        tdp-datafiles-staging     s3                          basic-sandbox          tdp-backend-develop, tdp-backend-staging   create succeeded   s3-broker
        tdp-staticfiles-develop   s3                          basic-public-sandbox   tdp-backend-develop                        create succeeded   s3-broker
        tdp-staticfiles-staging   s3                          basic-public-sandbox   tdp-backend-develop, tdp-backend-staging   create succeeded   s3-broker
        tdp-tf-states             s3                          basic-sandbox                                                     create succeeded   s3-broker

    # take frontend down for maintenance to update backend
    ssh tdp-frontend-staging
    # commands:
	    cd ~/app/public
	    mv 503_.html 503.html
	    exit


    # for each application bound to the service, un-bind it from the service, re-bind it, and restage it.
    cf unbind-service tdp-backend-staging tdp-staticfiles-staging
    cf bind-service tdp-backend-staging tdp-staticfiles-staging
    cf unbind-service tdp-backend-staging tdp-datafiles-staging
    cf bind-service tdp-backend-staging tdp-datafiles-staging
    cf restage tdp-backend-staging

    # verify access_key_id and secret_access_key have been rotated for each s3 resource
    cf env tdp-backend-staging

    # restart frontend
    cf restart tdp-frontend-staging
    
    # check for service keys that need to be rotated
    apennington@HHSLBDSWL73 MINGW64 /
    $ cf service-keys tdp-staticfiles-staging
    Getting keys for service instance tdp-staticfiles-staging as         alexandra.pennington@acf.hhs.gov...
    No service key for service instance tdp-staticfiles-staging

    apennington@HHSLBDSWL73 MINGW64 /
    $ cf service-keys tdp-datafiles-staging
    Getting keys for service instance tdp-datafiles-staging as     alexandra.pennington@acf.hhs.gov...

    name
    s3-versioning-key 


    # rotate service-key
    cf delete-service-key tdp-datafiles-staging s3-versioning-key

    Really delete the service key s3-versioning-key?> y
    Deleting key s3-versioning-key for service instance tdp-datafiles-staging as     alexandra.pennington@acf.hhs.gov...
    OK
    
    cf create-service-key tdp-datafiles-staging s3-versioning-key
    Creating service key s3-versioning-key for service instance tdp-datafiles-staging as alexandra.pennington@acf.hhs.gov...
    OK
    
    # verify rotation
    cf service-key tdp-datafiles-staging s3-versioning-key
    Getting key s3-versioning-key for service instance tdp-datafiles-staging as alexandra.pennington@acf.hhs.gov...

    <redacted>

    #restage
    cf restage tdp-backend-staging

    ```
    
3. test file submission and verify that file is stored in s3 via DAC
      
4. Follow rotation steps for `tanf-prod` space (`hhs:master` branch). Documentation saved [here](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/_layouts/15/Doc.aspx?sourcedoc={cbce2e75-17b2-4e70-b422-60d034fcd4af}&action=edit&wd=target%28Admin%20Notes.one%7C8e533710-461e-4b99-a33c-94e9b67b197e%2FSystem%20admin%20sync%20log%7C47928620-33e4-4cd0-8a3c-0542b83ef9b0%2F%29&wdorigin=NavigationUrl) :lock: 

5. Inform team that key rotation steps were completed. 

---


