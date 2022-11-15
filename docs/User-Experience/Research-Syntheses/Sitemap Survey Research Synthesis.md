# Research Synthesis - Tree-testing (Sitemap Survey)

# TDP Information Architecture (IA) - Tree-testing Study


The TANF Data Portal (TDP), developed by OFA in partnership with Raft will replace the legacy TANF Data Reporting System (TDRS) and will ease the data transmission and quality check process for OFA and STT users. TDP is a web-based platform that will in its pilot release, allow users to securely upload and download quarterly TANF files. Future releases will introduce a host of other functionality that enhances the data transmission experience for our users (e.g. transmission reports or questionable case reports in TDP), but also new functionality that will improve quality of data prepping and analysis of data (e.g. new human-readable error-guidance and data analytics).

## The importance of evaluating Information Architecture (IA)

The way pages are organized in a website, often called its Information Architecture, is an important aspect of the user experience of an application, which has the potential to make navigation of its features a frustrating or enjoyable experience. Easy-to-understand labels, clear call-to-action buttons (e.g., log in) and logical nesting of menu categories contribute towards a friction-less navigation experience for the user. There are two core methods used to test IA of a website with users:
- a card sorting exercise where users group menu labels into headers that make sense to them
- a tree testing exercise where users are asked to find specific functions within a list of nested labels


Through this current study, we wanted to understand whether different pages of the new TDP website are easily identifiable and reachable. In other words, we want to know if the navigation patterns of the new website made sense to user and supported their ability to quickly find what they’re looking for on the portal.




## Current IA for TDP website

![](https://i.imgur.com/xEVpx0V.jpg)




### TDP Page labels
* Privacy Policy
* Resources
    * TANF Transmission File Layouts
    * TANF File Instructions
* Create Account
    * Home
        * Welcome
        * Request Access to Portal
* Log In
    * Home
        * Welcome
        * Request Access to Portal
    * Data Files
        * Upload Files by Section
            * Current Submission
            * Submission History
            * Error Reports
    * Profile
        * Profile information
        * Manage my notifications
    * Admin
        * Manage Users
    * Reports
        * Feedback Report by section and quarter (Example Content)
    * Analytics
        * Data Dashboard (Example Content)
    * Help
        * FAQs
        * Tutorials




## How the test was set up
To understand the usability and legibility of labels associated with current and future pages of the TDP platform, we used a modified version of a tree-test to evaluate the IA. Using Google Forms, we created a survey that replicated the questions and answers of a typical tree-test and administered the first round to our users in the Office of Family Assistance (OFA).



### **How the form worked**
Through a carefully prepared Google Form, we asked questions about where users could find something on the website and asked them to choose from a list of options. Each of these options represented a page or tab within a page on the portal. Each question in the survey had two parts - the first part introduced a set of menu labels one tier above the intended answer in the page hierarchy (e.g., Sign up, Log in). The second part introduced the sections of a page where the user could actually find information they were seeking (e.g. Profile information, Request Access to Portal).

### Respondents of the survey

The first phase of this survey had **15 respondents from the Office of Family Assistance (OFA)**. Tasks for this round included questions on functions that OFA users would need to successfully perform on the new TANF Data Portal (TDP). 

The second phase was administered to **10 users from States, Tribes and Territories (STTs**) from three regions in the country, with tasks and questions modified accordingly. 

### **Results of the survey**

Most respondents could correctly identify menu labels, and successfully find relevant information by choosing the right answers that led to intended destinations and aligned with existing plans for TDP's Information Architecture.

One of the key metrics used to evaluate a tree-test is its success rate, which is the percentage of respondents reaching the intended destination for a particular task. Devoid of any visual cues like search bars or hyperlinks, tree-tests by nature are stripped down to bare menu labels that users are asked to make sense of. According to the UX pioneer [Nielsen Norman Group](https://www.nngroup.com/articles/interpreting-tree-test-results/), success rates in tree-tests are often multiplied in the final design that point users to specific destinations using more than one design element. 

We derived the success rate by calculating the total number of respondents who arrived at the correct answer to each question. Statistically, this meant calculating the number of correct answers for Part 2 of each question and dividing those by the total number of participants. Results were interpreted based on the importance and relevance of tasks based on essential TDP functionality for different personas. For example, for an OFA analyst, seeing the Submission History or Managing Users were key use cases, but these would be different for an STT analyst user.   

Below is a table that details the success rate for our current study.
Full results of the survey can be found [on Figma](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=6542%3A48856)



 
---

| Categories (OFA & STT) | Correct Option                                   | Success Rate (N=25;OFA-15, STT -10) | No. of participants (n) who arrived at  Question Part 2 | Pathways |
|------------------------|--------------------------------------------------|---------------------|---------------------------------------------------------|----------|
| TANF Information       | Resources-> TANF Transmission File Layout        | 68%                 | 21                                                      | ![](https://i.imgur.com/Xdfl185.jpg)|
| Submission History     | Log in->Data files->Submission History           | 76%                 | 19                                                      | ![](https://i.imgur.com/xBv9t3e.jpg)|
| Reports                | Log in -> Reports -> Feedback Report             | 68%                 | 20                                                      | ![](https://i.imgur.com/vbr9axH.jpg)|
| Onboarding             | Log in -> Help-> Tutorials                       | 40%                 | 13                                                      | ![](https://i.imgur.com/yEDqGve.jpg) |
| Data Dashboard         | Log In -> Analytics -> Data Dashboard            | 76%                 | 19                                                      |![](https://i.imgur.com/Lktn7jq.jpg)|
| OFA User Access        | Log in->Admin Profile->Manage Users              | 87%                 | 13                                                      |![](https://i.imgur.com/EPHjux6.jpg)|
| STT User Access        | Log in->Home-> Request Access to Portal          | 20%                 | 2                                                      | ![](https://i.imgur.com/6qgnyHw.jpg)|
| STT File Upload        | Log In -> Data Files -> Upload File by Quarter   | 70%                 | 8                                                       |![](https://i.imgur.com/Sb60Gju.jpg)|

**Success Rate (%) = Correct answers in Part 2 / total number of respondents**

---
The success rate is depicted in the table above along with other relevant choices for some questions. These choices are useful for further onboarding research and helping users familiarize with the platform.

### **Interpreting the results**
The proposed hierarchy of pages and nested labels for TDP were found to work for both OFA and STT users. Many our users were able to correctly find TANF information, Manage Users and Access Submission History, Feedback Reports and Analytics according to this survey. 

However, finding onboarding material like in-app tutorials were confusing for many users, with only 40% of participants arriving at the correct choices. 



### Project Impacts
A significant insight from the first phase of tree-testing is that the proposed Information Architecture is usable and navigable. However, to create a friction-free navigation experience, it is critical to address and control for incorrect pathways and gaps in success rates. 
In the following sections, we map project impact by analyzing the level of risk associated with a user not arriving at an intended destination. In other words, if a user cannot perform critical functions within the app because of confusing navigation patterns, it would require significant changes to the TDP Sitemap. 


High Risk - Critical function, low success rate (less than 50%)
Moderate Risk - Non-critical function, low success rate (less than 50%)
Low risk - Critical & non-critical function, medium success rate (between 50-80%)
Minimal risk - Critical & non-critical function, high success rate (greater than 80%)

[Figma link to Project Impact Risk Assessment](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=6673%3A49768)



**Onboarding experience for risk mitigation**
Most menu labels and categories have medium to high success rates, and gaps in knowledge can be addressed by creating optimal onboarding experiences. The low success rate for Grantee user access - a critical function - is a cause for concern, but still can be addressed by product documentation and through onboarding (e.g. with an FAQ). 

**Proposed sitemap changes for risk mitigation**
The 'Help' label leading to Tutorials and FAQs is one of the areas with a low success rate. Though it is an area that can be addressed by onboarding, as a future page, its position in the hierarchy can be further explored and is a potential area for future research. Future research could also explore whether a different name for the page would be more successful. 







