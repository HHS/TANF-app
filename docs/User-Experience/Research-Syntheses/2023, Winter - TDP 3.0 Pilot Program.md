#2023, Winter - TDP 3.0 Pilot Program
===

Following the [January 2023 research session]([https://github.com/raft-tech/TANF-app/blob/develop/docs/User-Experience/Research-Syntheses/2022%2C%20Winter%20-%20Understanding%20How%20STTs%20Use%20the%20Transmission%20Report.md) on error message handling and resolution, the team transitioned into supporting the February 2023 pilot expansion cohort. We learned the following key insights from participating states, tribes, and territories (STT) and TDP system admin:

**Insight 1: The shift from fiscal (FY) to calendar year (CY) time frame selections can be confusing for those who may not be familiar with this structure.**

Although the distinction between FY and CY was mentioned in the pilot emails, user trainings, and within the Knowledge Center, the message was missed and some STT selected the wrong year/quarter, which would cause downstream data impacts if not corrected.

**Recommendation**: Include validation upon data submission to check for the Fiscal Year and Quarter selection based on the data set. Until that feature is developed, the home page has a FY-CY cross-reference table to alleviate confusion.

**Insight 2: It’s not easy for System Admins to onboard, and manage users and logs at scale.**

The System Admin role is integral to the success of user management within TDP, however the current steps to identify, review, and approve  users can be tedious, which may result in delayed responses and potential errors, especially as the TDP user base grows.

**Recommendation**: Product team to add System Admin retros to help document inefficiencies within the admin tool (Django) during the various phases of user onboarding. See below for a list of system admin specific tickets already in development.
___

### Below are the  details to the February 2023 pilot expansion:

* [Who we talked to](#Who-we-talked-to)
* [What we did](#What-we-did)
* [What we tested](#What-we-tested)
* [What we learned](#What-we-learned)
* [What's next](#What&#39;s-next)
___

### Who we talked to

We recruited grantees based primarily on the following criteria:
* Interest in participating in the pilot
* Tribal to State ratio to insure we can continue to provide a concierge level of support
* 5 or more tribal programs within a region
* Regional staff availability

TDP's user base is now made up of:
* 17 States
* 17 Tribes
* Two Territories

As of February 2023 these STTs represent the following regions:

|  |  R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | Total  |
|-|-|-|-|-|-|-|-|-|-|-|-|
| States | 2 |  | 2 | 3 | 4 | 2 |  | 3 |  | 1 | 17  |
| Tribes |  |  |  |  | 7 |  | 1 | 2 | 5 | 2 | 17  |
| Territories |  | 1 |  |  |  |  |  |  | 1 |  | 2  |
| Onboarded | 33.33% | 25.00% | 33.33% | 33.33% | 64.71% | 20.00% | 12.50% | 38.46% | 20.69% | 11.11% |   |

___

### What we did

The pilot program v3.0 was conducted in order to:

* **Provide** grantees the opportunity to perform the necessary tasks to complete their FY2023 Q1 data file submissions on their own
* **Identify** and document pain points, if any with TANF Data Portal
* **Observe** and document accessibility, browser and general IT compatibility concerns/issues
* **Allocate** and conduct high level research to help inform decisions for future releases
* **Build** a rapport with grantees for future expansion and utilization of the TANF Data Portal
___

### What we tested

Each participant was tasked with the following:

* **opening** TDP in a compatible browser (i.e. not choosing Internet Explorer)
* **viewing** the home page
* **signing-in** using Login.gov
* **requesting access** to the TANF Data Portal
* **uploading** data files for FY2023 Q1 (October - December)
* **submitting** data files for FY2023 Q1 (October - December)
* **viewing** the submission notification (or submission error)
* **accessing** data files submitted historically through TANF Data Portal

___

### What we learned

Jump to:

* [We observed confusion concerning which calendar quarters map to which fiscal quarters and prioritized an enhancement to the homepage to help address it](#We-observed-confusion-concerning-which-calendar-quarters-map-to-which-fiscal-quarters-and-prioritized-an-enhancement-to-the-homepage-to-help-address-it)
* [Some programs who submitted data files were not able to correct their files based on the generic error message](#Some-programs-who-submitted-data-files-were-not-able-to-correct-their-files-based-on-the-generic-error-message)
* [System Admin observations and feedback that occurred during onboarding of users and validating user submission success rate](#System-Admin-observations-and-feedback-that-occurred-during-onboarding-of-users-and-validating-user-submission-success-rate)

#### We observed confusion concerning which calendar quarters map to which fiscal quarters and prioritized an enhancement to the homepage to help address it

- The problem stems from the data files themselves organizing data in a calendar quarter schema rather than one that deals with fiscal quarters (beyond the header of each file). When users are only used to operating in that calendar quarter context it can result in incorrect selections when submitting in TDP which in turn causes downstream data misalignment.

    ![Data files page with a drop down selection for Fiscal Year and Quarter](https://i.imgur.com/YeCqdjk.png)
    - To aide users in selecting the correct Fiscal Year and Quarter we have designed a cross-reference table to be added to the TDP homepage as an interim solution to address their confusion until we have parsing (which will be able to identify the issue as part of the error report).

    ![Welcome to TDP with a table of the data reporting deadline schedule](https://i.imgur.com/VYqgAjx.png)

    - The enhancement details can be found here [#1965](https://github.com/raft-tech/TANF-app/issues/1965)

#### Some programs who submitted data files were not able to correct their files based on the generic error message
- Specific copy and proper error messaging is recommended.
![Request failed with status code 400 error message](https://i.imgur.com/ERzi8Nq.png)
The details can be found here [#430](https://github.com/raft-tech/TANF-app/issues/430)


#### System Admin observations and feedback that occurred during onboarding of users and validating user submission success rate
In order to properly support additional users, the following should be taken into consideration for development.
- [Defect] VersionID missing for S3 submission history [#1007](https://github.com/raft-tech/TANF-app/issues/1007)
- [Feature] Being able to filter by STT and User Name so that system admin can view who is requesting access [#2415](https://github.com/raft-tech/TANF-app/issues/2415)
- [Feature] Reduce the number of unnecessary steps to approve a new user [#1641](https://github.com/raft-tech/TANF-app/issues/1641)

### What's next
- [**March 2023**] Continue recruiting for onboarding STTs into TDP with regional team alignment so that we are able to stay on schedule for full onboarding
- [**April 2023**] Planning transmission report .csv file research in order to explore how Grantees may interact with the content for error resolution
- [**May 2023**] Support onboarding and data file submission efforts for the next data submission deadline
