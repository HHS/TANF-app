# 2021, Spring - Evil User Journeys & TANF Data Errors (Round 6)

Research Round 6
[Issue #993](https://github.com/raft-tech/TANF-app/issues/993)

---

**Table of Contents:**

- [Who we talked to](#who-we-talked-to)
- [What we did](#what-we-wanted-to-learn)
- [What we learned](#what-we-learned)
- [What's next](#whats-next)

---

## Who we talked to

Round 6 research included participants representing:

- The OFA DIGIT Team and other OFA stakeholders (across all workshops)
- Raft-side stakeholders
- Raft project development team (in Evil User workshops)

---

## What we did

### Evil User Workshops (2)

**Objectives / Insight Areas**

- Align the project team around secondary research concerning bad-faith and improper usage of digital systems. 
- Prioritize the cases that represent the greatest risk to TDP and its related or supporting systems. 
- Identify any risks that require future research. 
- Brainstorm tactics that Evil Users could utilize.
- Brainstorm controls that could guard against Evil User tactics. 

### Error Data Workshops (2)

**Objectives / Insight Areas**

- Renew focus on current TDRS errors.
- Align DIGIT and Design teams on the impacts, severities, and meanings of current errors. 
- Prioritize high-impact / prerequisite errors to integrate in early TDP releases. 
- Align around proto journey maps concerning Regional Program Managers. 

### Synthesis Workshop

**Objectives / Insight Areas:**

- Share research insights with a broader cross-functional slice of the team.
- Affinity map insights and create themes.
- Identify actionable next steps and vote on their priority.

**Supporting Documentation:**

[We need a couple more OFA boards to wrap up linking]

- [Evil User Workshop #1]() :lock:
- [Evil User Workshop #2]() :lock:
- [Error Data Workshops Board](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1620936409266/794efb109e473ee761b988b692dd8572e159a14e) :lock:
- [Synthesis Workshop Mural Board]() :lock:

---

## What we learned

**Jump to**:

- [We identified two categories of errors more useful than Fatal/Warning to help structure our thinking and ideation]()
- [A segment of errors (including both errors of entry and errors of conversion) can block other errors from being able to be validated by the system.](#)
- [We aligned around six Evil User personas, brainstormed a list of tactics they could use, and identified security controls that might mitigate those tactics. ]()
- [We brainstormed a variety of potential system-compromising tactics and security controls or strategies that might mitigate them.](#)

---

### We identified two categories of errors more useful than Fatal/Warning to help structure our thinking and ideation.

Warning and Fatal errors are a differentiation made by the current TDRS system and fTANF validation tools, but during the course of the first Error Data Workshop we determined that they aren't a useful way to weigh the relative priority of errors that the new TDP system will be able to identify and provide guidance for. Instead, the team aligned around two new categories: Errors of Conversion and Errors of Entry. 

Errors of Conversion are largely due to system factors and high in volume. They refer to errors that crop up when a technology system in use by a grantee processes case data. They often stem from greenfield systems or system migrations that are not yet fully set up to process grantee data correctly. 

Errors of Entry refer to errors that occur at the case management level and are due to human factors rather than system factors. They can include data that's simply missing, data that was entered incorrectly, or data that was manually coded (either incorrectly or in a correct way that simply happens to conflict with federal coding requirements). 

> "Get rid of [the] concept of fatal and warning because they both should be prioritized"

Also noted was that the same errors can have significantly different impact depending on the grantee running into them. For instance, a single error in one case can make a larger difference for a Tribe using sampled data than for a grantee (particularly a populous one) reporting universe data. 

> "One case being thrown out for tribes is very critical because of their size"
>
> "Sample states pay more attention to fatal error records...One case being thrown out for a sample STT is more critical than one case for a universe STT"

**Project Impact(s)**

- The distinction between errors of conversion and errors of entry is the first step toward creating the taxonomies that will help grantees more easily navigate errors and act upon them. It will also play a role in identifying what types of errors a given round of research will focus on. 

---

### A segment of errors (including both errors of entry and errors of conversion) can block other errors from being able to be validated by the system.

Having distinguished the new error categories (Entry and Conversion) the focus shifted to the segment of errors that make most sense to prioritize for integration into TDP. The team aligned around that first slice being errors that "block" other errors. This can range from simple layout issues in the header or the trailer of a file to errors of conversion such as the T1-501 error which might prevent a given file from being fully parsed. The core rationale of this slice is that that until data in a file is complete and able to be fully parsed by the system (either the older TDRS system or TDP) it's not possible to validate and correct all the data in it. 

> "[It's important to get] a file into a format that we can accept and then do the analysis within TDP"

Our Error Data workshops also identified linking element errors (which are related to the completeness of a given TANF record) and program participation data errors (particularly those which relate to WPR reports) as being compelling future error slices. 

**Project Impact(s)**

- Research Round 7 will focus on this slice of errors. See [What's next](#whats-next) for more detail. 

---

### We aligned around six Evil User personas, brainstormed a list of tactics they could use, and identified security controls that might mitigate those tactics. 

| Persona Name | Description                                                  |
| :----------- | :----------------------------------------------------------- |
| Malcolm      | Motivated by personal gain and/or politics. He sets out from the start to use his system privileges for his own benefit. |
| Lilah        | Motivated by political or otherwise ideological factors. She uses a combination of her existing (and legitimate) privileges and social capital (e.g. befriending other employees) to gain higher privileges than she's cleared to have. |
| John Doe     | Motivated primarily out of a desire to disrupt the system. Acts from outside the system and its organizations, obtaining access either by accident or an intentional hack. |
| Dan          | Unlike other primary evil user personas Dan is not acting in bad faith, but rather unintentionally causing problems either due to mistakenly receiving privileges he shouldn't have and using them improperly as a result of lack of training, or by creating problems by misusing privileges he's cleared to have. Dan can increase the likelihood of misuse and attacks from the other three personas. |
| Reggie       | A grantee program employee who mistakenly receives access he shouldn't have; potentially access to admin functions or access to a grantee he's not associated to. Reggie is most likely to fall underneath the top level Dan persona, but could potentially be a subtype of any of them. |
| Gabbie       | An employee at any level who either intentionally or accidentally spreads privileged information to the public. Her motivations range from a desire for validation by peers to negligence concerning what information is cleared for public consumption. |

[Insert here tactics/controls list if we want it in the public repo] 

**Project Impact(s)**

- We prioritized Dan and Malcolm for use in short term follow-on workshops; these could potentially include stakeholders from outside the project team so as to better identify risks and collaborate on controls.  
- The [evil user journey maps]() :lock: synthesized from both workshops can be used to generate acceptance criteria for continued work on TDP. 

---

## What's next

**Next Steps & Validations**

- [Issue #993](https://github.com/raft-tech/TANF-app/issues/993) will deliver a research plan for Round 7 focused on modeling the first slice of errors identified in Error Data Workshops to support releases 2 and 3. Related tickets include creation of a Round 7 Epic ([#1017](https://github.com/raft-tech/TANF-app/issues/1017)) and sprint-specific ticketing for sprints 24-26 ([#1018](https://github.com/raft-tech/TANF-app/issues/1018), [#1019](https://github.com/raft-tech/TANF-app/issues/1019), [#1020](https://github.com/raft-tech/TANF-app/issues/1020)). The following next steps & validations (as voted on in the Synthesis Workshop) will be encompassed in this round:

  - Inventory all errors that can block parsing & any associated guidance. 
  - Gather dev resources to support the coding parsing blocker errors into TDP.
  - Validate error messaging & error related guidance for understanding with grantees.
  - Ideate on parsing blocker error guidance. 
  - Validate Regional Program Manager journey maps with Regional Managers. 
  - Inventory what is needed to enable regional staff to confirm the identities of grantee users.

---
