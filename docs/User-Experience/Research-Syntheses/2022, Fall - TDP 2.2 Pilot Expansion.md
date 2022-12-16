# 2022, Fall - TDP 2.2 Pilot Expansion

Last Updated for [#2191](https://github.com/raft-tech/TANF-app/issues/2191)

___

**Table of Contents:**

* [Who we talked to](#Who-we-talked-to) 
* [What we did](#What-we-did)
* [What we tested](#What-we-tested)
* [What we learned](#What-we-learned)
* [What's next](#What&#39;s-next)

___

### Who we talked to

We recruited grantees based primarily on the following criteria: 
* Interest in participating in the pilot
* Current reliance on email transmission (Tribes)
* Recent submission of partial data
* Submitting SSP-MOE data

Aligned to the above criteria the pilot expansion includes both returning participants from v2.0 as well as newly onboarded participants representing the following STTs: 

v2.0 Returning Participants
* 6 States (Unmoderated sessions)
* 5 Tribes (Unmoderated sessions)

v2.2 New Participants
* 4 States 
    * 1 of whom participated in a moderated session
    * 1 of whom onboarded to use TDP to address existing issues with mft/cyberfusion transfers

* 4 Tribes 
    * 2 of whom participated in a moderated session
    * 2 of whom signed-up, but did not participate in the pilot program
* 2 Territories 
    * 1 of whom participated in a moderated session
    * 1 of whom signed-up, but did not participate in the pilot program
___

### What we did

The pilot expansion program was conducted in order to:

* **Evaluate** the success rate from Grantees (STTs) on their experience with the TANF Data Portal based on existing features and onboarding materials with data submission Q4 2022 that is due on November 14, 2022
* **Identify** and document pain points, if any, that Grantees have with email notifications, search between TANF or SSP-MOE data files, and upload/download data files
* **Observe** and document accessibility, browser and general IT compatibility concerns/issues
* **Allocate** and conduct high level research to help inform decisions for future iterations 
* **Build** a rapport with grantees for future expansion and utilization of the TANF Data Portal

**Supporting Documentation**
* [Pilot Workshop v2.2 :lock:](https://app.mural.co/t/raft2792/m/raft2792/1664205610518/2b3edb3a6f413ac420cffdc2461c9d5ecd1433e9?sender=u3ca60168b5ac4eb17bf92804)

___

### What we tested

Each participant was tasked with the following:

* **opening** TDP in a compatible browser (i.e. not choosing Internet Explorer)
* **viewing** the home page
* **signing-in** using Login.gov
* **requesting** access to the TANF Data Portal
* **receiving** inline email notifications from TANF Data Portal
* **uploading** data files for FYQ4 2022 (July - September)
* **submitting** data files for FYQ4 2022 (July - September)
* **viewing** the submission notification (or submission error)

Overall, the pilot expansion program was a success in which data was successfully transmitted for each grantee that participated. In addition, TDP has been utilized to help solve for instances where data file transfers have been a challenge due to existing file transfer protocols. 

___

### What we learned

Jump to: 
* [What went well](#What-went-well)
* [Retest observed gaps from August 2022 pilot program](#Retest-observed-gaps-from-August-2022-pilot-program) 
* [Some participants overlooked the Search functionality which may result in incorrectly categorized data file submissions](#Some-participants-overlooked-the-Search-functionality-which-may-result-in-incorrectly-categorized-data-file-submissions)
* [Observed minor bugs during moderated sessions](#Observed-minor-bugs-during-moderated-sessions)
* [Some participants expressed interest in being able to upload previous years data files](#Some-participants-expressed-interest-in-being-able-to-upload-previous-years-data-files)

___

### What went well

Based on the task scenarios defined for v2.2 the pilot expansion program was a success. Grantees that participated were able to complete all task scenarios measured in v2.0 in addition to new released features for inline email notifications and being able to submit TANF and/or SSP-MOE data files. In addition, for those in our moderated sessions we were able to observe and record the efficiencies and perceived shortcomings of the current platform to help inform future iterations. While our top level findings focus on observed gaps to improve TDP, we continue to receive positive feedback on TDP’s impact from participating grantees.

### Retest observed gaps from August 2022 pilot program 

In addition to reviewing new functionality, we wanted to revisit and retest the areas noted from the August 2022 pilot program. Please reference [August 2022](https://tdp-project-updates.app.cloud.gov/august-2022-update.html) for full details 
- Tribal programs listed in the STT selection combobox may pose a discoverability issue
    - To aide with locating the correct STT for tribal programs, we added content within the Knowledge Center as a short term resolution. We did *still* observe this occurrence during our moderated session with one of two tribal STTs. 
    -  OFA staff held a tribal division staff meeting and together propose changing the request access form such that users must select the STT type (tribe, state, territory), first. Based on this selection, the relevant STT combo-box options would appear.
    - The enhancement details can be found here [#2133](https://github.com/raft-tech/TANF-app/issues/2133)
- Terminology used to identify sections and certain UI elements lead to friction among some participants
    - *Closed vs. Negative*
        - OFA staff held a tribal division staff meeting and together concluded that the term "Negative" does indeed originate from fTANF. However, the fTANF replacement is at least still 1 year or more away and some course of action is suggested to clarify the label name as an interim. 
        - The enhancement details can be found here [#2131](https://github.com/raft-tech/TANF-app/issues/2131)
  - The Stratum data file picker being available to all grantees was confusing for those who submit universe data
    - Both of the moderated STTs did inquire about the Stratum data file section  
    - The enhancement details can be found here [#2217](https://github.com/raft-tech/TANF-app/issues/2217)
- Most participants used TDP at resolutions that obscured submission status from view
    - In observation during the v2.2 moderated sessions, the STTs are now able to view the submission status message once it has loaded 
    - This enhancement was implemented in November 2022 and details can be found here [#2140](https://github.com/raft-tech/TANF-app/issues/2140)

### Some participants overlooked the Search functionality which may result in incorrectly categorized data file submissions

In order to correctly submit data files, the participants would need to make a File Type, Fiscal Year and Quarter selections in the combobox and then click “Search”. However, there is evidence that once the File Type, Quarter/Year has been selected and set within the combobox, the participant assumes the selections are changed. The additional click of the “Search” button again to initiate the adjustment may not be consistently happening.  
> "Other than the one dislike about the search function, I like this new system." ~Tribe

If left unaddressed this issue could lead to:
- Downstream data integrity issues
- Misaligned attribution of funding
- Inconsistent display of data files over time
- Confusion for auditors when reviewing back dated submitted date files
- Increased work for OFA Admins to reallocate the data files

**Suggested Action(s)**
- Propose and test various levels of course of action in order to increase the visibility and need to “Search” after the File Type and Quarter/Year combobox selection

### Observed bugs during moderated sessions
- There were a few instances where STTs were experiencing data submission latency (i.e. network errors) that resulted in multiple data submission as well as potentially not receiving the submitted data files email [#2268](https://github.com/raft-tech/TANF-app/issues/2268). Future manual testing during `raft/qasp` review will need to accommodate for large file sizes. 
> "I sent an email that I received the 'Network error' message.  You already followed up on that.  I didn't see the banner that let me know it was successfully uploaded this time (probably due to the error).  I look for that banner - it's important for me to know I've completed the process successfully.  You can reach out anytime if you have questions or want feedback." ~State

- Some participating STTs reported that previously submitted data files from Q3 2022 were appearing in the most recent quarterly search results
- This bug can tracked here [#2256](https://github.com/raft-tech/TANF-app/issues/2256)
> "It was odd that the last quarter's reports were in the spaces for the current quarter. I wasn't sure what to do, so I click on the change reports. I think the new quarter spaces should be empty. ~ Tribe

### Some participants expressed interest in being able to upload previous years data files
- The combobox for Years only has selections for 2021, 2022, and 2023. Some participants expressed interest to be able to see historical data submissions up to 3-5 years back to allow for those data files to be available for review by auditors 
- This research effort can be tracked with [#1972](https://github.com/raft-tech/TANF-app/issues/1972) and the development effort [#2267](https://github.com/raft-tech/TANF-app/issues/2267)
___

### What's next 

* **[December 2022]** Where applicable, new tickets will be created to document suggested actions based on the feedback and prioritized accordingly into the development backlog
* **[December 2022]** Extract certain key aspects of the pilot workshop to help facilitate the next pilot expansion
* **[January 2023]** Prepare and present these findings to the larger product team and regional stakeholders
* **[January 2023]** Revise participant onboarding strategy to address participant retention challenges
* **[February 2023]** Identify and onboard v3.0 pilot expansion participants in order to continue to align with ATO decommissioning deadline 

___





