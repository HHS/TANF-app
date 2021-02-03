# Business Need

OFA, in partnership with 18F, has contracted with Raft LLC to develop a TANF Data Portal (TDP) to replace the TANF Data Reporting System (TDRS), which is currently maintained and operated by OCIO. States, tribes, and territories (STT) that are TANF grantees, distribute TANF cash assistance in various ways and collect information about recipients in a variety of different systems. Some of this data is currently passed to OFA through TDRS as part of federally-mandated reporting.

Issues with the current system prevent states from meeting their goals and prevent the federal team from being able to accurately gauge TANF’s impact.  OFA is seeking to build the new TANF Data Portal to correct the issues of the current system and provide a user-friendly and secure interface for STTs. OFA hopes to work closely with OCIO throughout the development process to ensure that security measures are inherent in the system and to pave the way for an Authority to Operate (ATO). As part of this, OFA is interested in de-risking the project by implementing continuous security practices.

# Business Impact

OFA will build a new, secure, web-based data reporting system to improve the federal reporting experience for TANF grantees and federal staff. The new system will allow grantees to directly and easily upload their data and be confident that they have fulfilled their reporting requirements. This will reduce the burden on all users, free up staff time, improve data quality, and ultimately help low-income families. Better data is critical for OFA’s operations and monitoring of grantees, as it provides information about how grantees are meeting their work participation rate targets and complying with time limits, as well as demographic information about families receiving TANF cash assistance. OFA relies on this information to make policy recommendations and STTs may face penalties of up to four percent of their total grant award each quarter if their reported TANF data is not timely, complete, and accurate.

Additionally, a more secure system with an Authority-to-Operate will ensure that personally-identifiable information from grantees and TANF recipients is protected, which is fundamental to our legal obligations as stewards of this data.

# Assumptions

- The research we have done to date will inform the MVP and allow the vendor to meet the constraints mentioned below.
- Every user story follows our documented [workflow](https://github.com/HHS/TANF-app/blob/main/docs/How-We-Work/team-charter/our-workflow.md#workflow) which ensures everyone is clear on what it means for the story to be finished and acceptable to the government.
- User research with real end users results in both better usability (when testing features already built) and is a powerful source of new user stories that reflect real user needs to be added to the product backlog.
- Close collaboration with the ISSO and wider IPT through participation in sprint ceremonies will ensure that security controls are accurately and completely implemented from the beginning alongside our user-facing features.
- An empowered Government Product Owner can select the highest value work to be completed by the team at the beginning of each Sprint, to ensure we're always working on the most important things.

# Constraints

It is possible that legislative mandates for required data elements will change in the coming year, as TANF reauthorization is currently under discussion.  While this may impact the specific data elements that STT grantees are required to submit, we do not anticipate it would affect broader architecture decisions concerning security.
