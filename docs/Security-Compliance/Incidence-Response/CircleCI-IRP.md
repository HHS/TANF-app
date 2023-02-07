# Response Strategy for CircleCI Security Incident (Dec 2022)

## Scenario: Security of CI/CD tool compromised

TDP uses CircleCI as its CI/CD platform, and our team was recently informed of a [security incident](https://circleci.com/blog/january-4-2023-security-alert/) that potentially exposed the secret keys that we store as environment variables on the platform (see notification snapshot below).  

While, there's been no indication from CircleCI or our audit logs of unusual activity on TDP, we were advised to rotate the `production` secret keys. 

**This document captures the steps we followed to respond to this incident, from the point of initial notification to resolution. These steps should be repeated in the event of another incident on platform.**

![CircleCIDec2022](https://user-images.githubusercontent.com/84722778/210823266-c3874fd7-f3d5-4eaa-bff9-99661db46397.png)



## Mitigation steps
1.  Follow [secret key incident response communication protocol](./Secret-Key-Mgmt.md/#communication-protocol-if-secret-keys-are-leaked).


2. Identify and remove secret keys stored in `HHS/TANF-app` CircleCI as environment variables. 

```
CF_USERNAME_PROD + CF_PASSWORD_PROD
JWT_KEY
ACFTITAN_KEY
AMS_CLIENT_SECRET
```
3. Review [historic logs via cloud.gov](https://cloud.gov/docs/deployment/logs/#web-based-logs-with-historic-log-data) for the backend production app (`tdp-backend-prod`) during the time period of the security incident. Check for anomalous activity and report back to the team. 

4. Follow steps [here](../../Technical-Documentation/secret-key-rotation-steps.md) for rotating abovementioned keys.  

5. Once all keys have been rotated the new ones should be added back to CircleCI and the production deployment workflow should be initiated to restage the production apps and confirm that the system is functioning normally. If there is any unintended downtime impacting system users, OFA product team should be informed immediately so that a contingency plan can be activated until the system is restored. 

