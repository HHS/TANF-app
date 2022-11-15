# System Admin Account Restoration Strategy

## Scenario: Sys Admin Account(s) Compromised

**TDP has 2 sys admins, and one has turned evil :smiling_imp: and decided to compromise the other's account such that they can no longer access TDP DAC. Below is a screenshot of the compromised account:**

_Sys admin account (i.e. `alexandra.pennington@acf.hhs.gov`)  has been modified with a different username/email address, first name, and last name._
![incident_sysadmin](https://user-images.githubusercontent.com/63075587/162066471-cc5a1f88-aada-4309-9629-b341e61cdb5d.PNG)

_When the sys admin tries to sign back in, she is taken to the request access page. She will be unable to access TDP DAC until this request is approved by a user with `OFA System Admin` permissions_

![incident_sysadmin1](https://user-images.githubusercontent.com/63075587/162066631-86c90d4c-1168-48e2-941f-9212c811581e.PNG)


## Example mitigation steps
- Follow [communication protocol](#communication-protocol-if-sys-admin-account-compromised)
- Sys admin with compromised account should work with System owner to confirm appropriate admin roles are assigned to their cloud.gov account. This account will be necessary to change TDP DAC access remotely. 
- Sys admin with compromised account should use CF CLI to remotely restore permissions: 

**<details><summary>CF CLI commands</summary>**
    
**1. Login via CF CLI**

```
$ cf login -a api.fr.cloud.gov  --sso
API endpoint: api.fr.cloud.gov

Temporary Authentication Code ( Get one at https://login.fr.cloud.gov/passcode ): <redacted passcode>

Authenticating...
OK

Select an org:
1. hhs-acf-prototyping
2. sandbox-hhs

Org (enter to skip): hhs-acf-prototyping
hhs-acf-prototyping
Targeted org hhs-acf-prototyping.

Select a space:
1. tanf-dev
2. tanf-prod
3. tanf-staging

Space (enter to skip): tanf-staging
tanf-staging
Targeted space tanf-staging.
```
**2.  Target the appropriate backend application and initiate django shell**

2a. _The following commands work on **non-GFE** (press <enter> after each command)_
```
cf ssh tdp-backend-staging
/tmp/lifecycle/shell
python manage.py shell_plus
```
2b. _If 2a does not work on **GFE**, the following commands should work ([reference](https://cloud.gov/knowledge-base/2021-05-17-troubleshooting-ssh-connections/#troubleshooting-ssh-connections)) (**make sure you are NOT connected to VPN**):_

* Retrieve the PROCESS_GUID for the web process for your app. You will be prompted for this value below.  
    
```
cf curl v3/apps/$(cf app tdp-backend-staging --guid)/processes | jq --raw-output '.resources | .[]? | select(.type == "web").guid'

```

* Retrieve a one-time ssh passcode. You will be prompted for this code below.

```
cf ssh-code
```
* Use ssh to connect to your app container. Insert the value for your PROCESS_GUID obtained above. 
```
ssh -p 22 cf:<PROCESS_GUID>/0@ssh.fr.cloud.gov
```
* You will be prompted to enter a password. Use the one-time ssh passcode  generated from `cf ssh-code` above (Note: pasting the value will be invisible). If this is successful, the command line will appear like this:
    
```
vcap@SomeHashValue...
```

* Initiate interactive SSH session using the following 2 commands (press `enter` after each command):

```
/tmp/lifecycle/shell 
python manage.py shell_plus 
```

You will know you are in an interactive session if the command line appears like this:
    
```
    In [1]:
```
    
**3. In the Django shell, give your user account (the one associated with PIV/CAC) the appropriate permissions:**
```
user = User.objects.get(username='alexandra.pennington@acf.hhs.gov')
user.groups.set(Group.objects.filter(name='OFA System Admin'))
user.is_staff = True
user.is_superuser = True
user.is_deactivated = False
user.save()
```
**4. Login to TDP frontend via ACF AMS and confirm access to TDP DAC restored.**

_Note: be sure to request access again, if prompted. after submitting the request, all appropriate access should be restored._

_TDP frontend view:_
![incident_sysadmin2](https://user-images.githubusercontent.com/63075587/162066853-6d9b78b3-4425-4881-9fee-8b975a1b7180.PNG)


_TDP backend DAC view:_
![incident_sysadmin3](https://user-images.githubusercontent.com/63075587/162067096-039cc639-60ed-4c4d-abc5-b2c9f6571bf0.PNG)

</details>
    
- Conduct post-mortem:

    - How did the system admin's account get compromised? What facilitated this? 
    - What was the impact of this compromise?
    - What lessons were learned?
    - Next steps?

### Communication protocol if `sys admin` account compromised
- Contact system owner via [Mattermost OFA TDP Product Channel](https://mattermost.goraft.tech/goraft/channels/ofa-tdp-product). If Mattermost isn't available, please send an email and cc: ACF Tech Lead, Product Manager, vendor Tech Lead. 

- Include details of the compromise, which should include:
    - where compromise occurred (e.g. TDP? cloud.gov?)
    - how the compromise occurred (if known)
    - preliminary assessment of the scope and impact of the compromise (e.g. were spaces and/or services deleted? was PII compromised? exposed?)
    - Next steps (e.g. schedule mtg to discuss incident response plan, rotate keys, etc.)
    
- If system admin's compromised account is not restored by following the abovementioned steps, this could be because the evil user also changed the admin's cloud.gov account permissions and/or compromised other components of TDP. If this is the case, the `system owner` should reach out to cloud.gov (https://cloud.gov/docs/help/) support to have any necessary user permissions and/or services (e.g. database) restored. 

### Notes

- Tools needed for this incident response strategy:
    - cloud.gov account with `user` and `manager` roles assigned at <org> and <space> levels.
    - [git bash](https://git-scm.com/downloads) - _this usually comes with the download package for Git for Windows. Can alternatively use Command Prompt._
    - [Curl for Windows 64 bit](https://curl.se/windows/) - _this usually comes with the download package for Git for Windows_
    - [cloud foundry binary for Windows 64 bit](https://github.com/cloudfoundry/cli/blob/master/doc/installation-instructions/installation-instructions-v7.md#installers-and-compressed-binaries)
    - [JQuery version 1.6 for Windows 64 bit](https://stedolan.github.io/jq/download/)
- Mitigation steps outlined above target `hhs-acf-prototyping` org, `tdp-staging` space and `tdp-backend-staging` app. `org`, `space`, and `app` targets will need to be modified in a production context. 
- Review the latest TDP Incidence Response Plan [here](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2Fcompliance&viewid=6ecbc5f1%2Dfa9c%2D4b0a%2Da454%2D35e222e8044e), and [see incidence response tips from cloud.gov](https://cloud.gov/docs/ops/security-ir/). 

### Q&A
- Should Sys owner and sys admins all have the same <org>  roles in [cloudgov](https://docs.cloudfoundry.org/concepts/roles.html#roles)? Is this an acceptable risk? 
  - Yes. System owner should reach out to cloud.gov support if a privileged user's cloud.gov account roles are compromised.  
- Compromised account will still appear as a user in TDP DAC. Should we delete this user account? 
  - No. This account will remained in a deactivated state. 
- The evil user's account should-- at a minimum-- be deactivated from TDP, but should we delete it? (presume this person will no longer be working for ACF) 
  - No. This account will remain in a deactivated state. Deleting the account would result in losing the history of activity associated with the user which should be kept for auditing purposes. Additionally, this prevents the evil user from attempting to re-request access to TDP. 
