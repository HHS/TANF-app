# ACF OFA Skill area heuristics  

## Goal of this document:  

This document was created  to help OFA staff assess whether the product development team performs satisfactorily and identify areas for improvement. We built this from 18F's evaluation practices for our own internal and external work.  

It is not meant to replace the [Quality Assurance Surveillance Plan (QASP)](https://github.com/18F/tdrs-app-rfq/blob/main/Final-RFQ/FINAL-TDRS-software-development-RFQ.md#32-quality-assurance-surveillance-plan-qasp), acceptance criteria, or to be an exhaustive checklist for all work. These heuristics should compliment contractual evaluative measures and be used to identify feedback opportunities within the team.
* [Code maintainability](#code-maintainability)
* [Design](#design)
  * [Universal Design (Accessibility)](#accessibility)
  * [User Research/Usability Testing ](#research)
  * [Content](#content)
* [Product team](#product)

<a name="code-maintainability"></a>
## Code Maintainability

Understanding code quality and maintainability requires examining the code itself and comprehending it at least at a high level. The indicators below are generally intended for someone who already has the knowledge to do that, but each one includes steps that a non-coder can take to help determine if things are going well or not.  

<div class="table-wrapper">
  <table>
    <thead>
      <tr valign="top">
        <th class="col-indicator">Indicator</th>
        <th class="col-good-sign">Good sign</th>
        <th class="col-bad-sign">Bad sign</th>
      </tr>
    </thead>
    <tbody>
    <tr valign="top">
        <td class="col-indicator">Code actually does what the stories intend </td>
        <td class="col-good-sign">Incremental code delivery can be traced back to user story value or user story tasks. 
        <br><br>Occasionally, there will be concerted efforts to remediate technical debt but this should not be the norm.</td>
        <td class="col-bad-sign">Code does not address users stories or user story acceptance criteria. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code uses Do Not Repeat Yourself (DRY) principles </td>
        <td class="col-good-sign">Common functionality uses open source libraries when possible.
        <br><br>When new code is developed repeat code is centralized into a module.
        <br><br>Developers leverage USWDS code and guidance as much as possible, rather than creating custom components.
        <br><br><b>Non dev:</b> The dev team will not have similar code throughout the code base, but will design it so that central modules can be reused. </td>
        <td class="col-bad-sign">Common functionality uses custom code.
        <br><br>The same methods are repeated throughout different files.
        <br><br>Custom components that deviate from USWDS guidance are common. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code methods are short and simple, and maintainable </td>
        <td class="col-good-sign">Methods are generally shorter than 25 lines of code. The methods generally have few conditionals to minimize cyclomatic complexity. The team may include automated tests like <a href="https://www.flake8rules.com/rules/C901.html">flake8</a> to check for code readability and complexity. 
        <br><br>Methods are easy to test. Method function can outputs can be reasoned out by review of the method and the accompanying tests.  
        <br><br><b>Non dev:</b> Coded methods are short. At the individual-method level, there are only a few pieces of logic. We favor coding styles that allow for testing and clarity.</td>
        <td class="col-bad-sign">Methods are very long and cram a lot of different iterations or conditionals into a single method. Methods are hard to test.
        <br><br>Methods are hard to reason about and thus  also difficult to test, difficult to maintain, and prone to bugs.  </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code has logical organization.</td>
        <td class="col-good-sign">When files become large they are broken out into a folder, and folder structure could be reasonably understood by a developer less-familiar with the project.
        <br><br><b>Non dev:</b> The code is well organized by file and folder. </td>
        <td class="col-bad-sign"></td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code variables and methods have human readable names </td>
        <td class="col-good-sign">Method names should accurately reflect what the method does, and variable names should clearly indicate the data they’re holding and for what purpose. Don’t be afraid of long names. Good naming practices contribute to self-documenting code and reduce the manual documentation burden.
        <br><br><b>Non dev:</b> Naming conventions within the code favor comprehension.</td>
        <td class="col-bad-sign">Variable names and method names are shortened, concatenations, or single letters or very generic and do not give much insight into the function of code. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code is well-tested to prevent regressions </td>
        <td class="col-good-sign">All tests pass on every pull request. When new features are added or bugs are fixed, tests are updated or added as appropriate. Tests meaningfully hit most if not all of the logic of the additional code.
        <br><br><b>Non dev:</b> Have the dev team create an integration with Github that includes test results with each code change. Make sure the tests pass before approving, and also ask the developers to show you any new or modified tests to give you confidence that tests have been updated as needed. </td>
        <td class="col-bad-sign">Tests are removed, or new tests are not added. Tests are written such that they pass without actually testing anything. The percentage of code tested drops substantially. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code conforms to a single style standard</td>
        <td class="col-good-sign">A linter and/or code formatter are applied to the code to identify and fix inconsistencies before code is accepted. Linting styles are separate for the frontend and the backend.
        <br><br><b>Non dev:</b> Have the dev team create an integration with Github that includes a linter report with each code change. If the linter report shows no errors, the code is satisfying the style standards. </td>
        <td class="col-bad-sign">Linter errors are ignored and/or linting ignore statements are frequently added to pieces of code. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code is free of known vulnerabilities </td>
        <td class="col-good-sign">Third-party dependencies are routinely checked for known-vulnerable versions. The app as a whole is analyzed by an automated security tool (e.g., snyk and OWASP) for common kinds of vulnerabilities.
        <br><br>When vulnerabilities are found, the developer team takes time to investigate the impact and remediate or mitigate the vulnerability. <br><br><b>Non dev:</b> Have the dev team create an integration with Github or MSTeams that reports whenever there are vulnerabilities. The developers should be able to discuss with you what those are and how they are being mitigated. </td>
        <td class="col-bad-sign">Vulnerable dependencies are ignored without good reason (e.g., ignoring a vulnerability in a development-only dependency may be fine). Ignoring reports from security scanning tools. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code for deployment is checked in</td>
        <td class="col-good-sign">Any configuration changes are included and support a continuous delivery pipeline to our development environment.</td>
        <td class="col-bad-sign">Configurations that were manually added are not documented. </td>
      </tr>
      <tr valign="top">
        <td class="col-indicator">Code is well-documented </td>
        <td class="col-good-sign">In places where the code is complex or not sufficiently self-documenting, inline comments are provided to explain it to future developers.  
        <br><br>Methods use a standard notation in-line notation that can be parsed. For this project (JSDoc on the frontend) and  (Python Docstring on the Backend)
        <br><br>External APIs are documented. A wiki or other documentation captures larger system documentation, such as system diagrams, etc. <br><br>Documentation on how to run the application locally is up to date and can be run through.
        <br><br><b>Non dev:</b> Ask the developers to explain the code’s behavior. If they cannot give a coherent, layperson’s explanation of the behavior of the code, that suggests that they don’t have a deep understanding of it which might further indicate that the code is unnecessarily complex. </td>
        <td class="col-bad-sign">No inline comments because code is “completely self-documenting.”
        <br><br>Documentation is not updated as code changes.
        <br><br>Code is commented out instead of removed. </td>
      </tr>
    </tbody>
  </table>
</div>

<a name="design"></a>
## Design

Design touches every area of the product, and can mean different things to different teams at different times. The work you'll evaluate may vary from sprint-to-sprint; you may review research plans on week and user interface mockups the next. No matter the work, these design heuristics are the specific markers to look for to ensure design decisions are user centered, ethical, and maintainable.  

These indicators are meant to help evaluate the practices and work of a design team. In addition to general design heuristics, there are also specific indicators for evaluating accessibility, usability tests and research, and content.

<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th class="col-indicator">Indicator</th>
        <th class="col-good-sign">Good sign</th>
        <th class="col-bad-sign">Bad sign</th>
      </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan="3"><b>Design process</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Needs are clear</td>
      <td class="col-good-sign">The design team can clearly state what problem a design is trying to solve and what users need from that design.
      <br><br>Understanding of those needs is clearly tied to research. </td>
      <td class="col-bad-sign">It’s not clear what problem a design is trying to solve or how it relates to user needs.
      <br><br>Design choices are based on personal preferences rather than research.  </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Open about uncertainties</td>
      <td class="col-good-sign">The design team is open about where questions exist and actively tries to answer them. They regularly initiate conversations and ask questions. </td>
      <td class="col-bad-sign">The design team doesn’t note where uncertainties exist. They passively accept information rather than actively pursue it.</td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Design with, rather than for</td>
      <td class="col-good-sign">The design team involves others in the design process (users, stakeholders, other team members) and uses others’ expertise to shape the design.  
      <br><br>The process for how a design was created is clear to the team.
      <br><br>Feedback is solicited regularly to check for assumptions and alignment. Time for feedback is built into the design process and adjustments are made to designs after feedback is discussed. </td>
      <td class="col-bad-sign">Design exercises involve only designers. The designer is seen as someone who can make magic in a vacuum and deliver on their own.  
      <br><br>Designs come from a “black box” or unclear process.
      <br><br>There are limited or no feedback opportunities, and designs feel misaligned with product goals or user needs.
      <br><br>Feedback is only requested at the end of the design process or not considered when iterating on the design.  </td>
    </tr>
    <tr>
      <td colspan="3"><b>Implementation</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Uses reusable design patterns  </td>
      <td class="col-good-sign">The design team creates and leverages reusable UI patterns to create consistent designs. They follow <a href="https://designsystem.digital.gov/">USWDS</a> usability and accessibility best practices.  
      <br><br>If a deviation is made from an established pattern, the reason is clearly stated, and deviations still feel consistent with the team's prior design choices.</td>
      <td class="col-bad-sign">Designers deviate frequently from past design patterns and create new ones that are not consistent with prior design choices.  
      <br><br>Design prioritizes novelty and bespoke solutions over established patterns.</td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Designers and developers collaborate </td>
      <td class="col-good-sign">Designers and developers pair regularly. They work together to identify design approaches that are technically feasible to implement that meet user needs.
      <br><br>Designers and developers give each other feedback frequently, without prompting from other team members, and in a productive, collaborative manner.</td>
      <td class="col-bad-sign">There is frequently misalignment between what is designed and what is implemented.
      <br><br>Designers and developers are isolated from each other, and don’t provide feedback to one another.  </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Integrates content, accessibility, and usability testing heuristics in work </td>
     <td class="col-good-sign">Reference back to <a href="#content">content</a>, <a href="#accessibility">accessibility</a>, and <a href="#research">usability testing</a> heuristics. </td>
      <td class="col-bad-sign">Does not follow <a href="#content">content</a>, <a href="#accessibility">accessibility</a>, and <a href="#research">usability testing</a> heuristics</td>
    </tr>
    </tbody>
  </table>
</div>

<a name="accessibility"></a>
### Universal Design (Accessibility)

The following indicators support design of barrier-free digital products that can be used by everyone. The "good signs" and "bad signs" are merely examples; they are in no way comprehensive.  

The [Principles of Universal Design](https://projects.ncsu.edu/ncsu/design/cud/about_ud/udprinciplestext.htm) were initially developed in 1997 at the Center for Universal Design at North Carolina State University, funded by the U.S. Department of Education's National Institute on Disability and Rehabilitation Research.

<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th class="col-indicator">Indicator</th>
        <th class="col-good-sign">Good sign</th>
        <th class="col-bad-sign">Bad sign</th>
      </tr>
    </thead>
    <tbody>
    <tr valign="top">
      <td class="col-indicator">Equitable use</td>
      <td class="col-good-sign">Everyone uses the same website.</td>
      <td class="col-bad-sign">People with disabilities use a separate “accessible” site or an “accessibility mode.”</td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Flexibility in use </td>
      <td class="col-good-sign">People can operate the website even when it is zoomed in many times. </td>
      <td class="col-bad-sign">People can’t use a screen reader to identify the headings on the page. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Simple and intuitive use </td>
      <td class="col-good-sign">The website is straightforward, with clean layout, consistent interaction, and clear information. </td>
      <td class="col-bad-sign">The website is arranged based on the agency’s organizational structure rather than on visitors’ goals, making information difficult to find. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Tolerance for error </td>
      <td class="col-good-sign">Interactions are designed to promote success and minimize risks, for example, by providing confirmations and feedback. </td>
      <td class="col-bad-sign">People can’t change a response on a previous step, such as when they cancelling or deleting action  </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Low physical effort </td>
      <td class="col-good-sign">Each feature is manually tested for accessibility to ensure that people can efficiently operate websites using their preferred input device (such as a keyboard). </td>
      <td class="col-bad-sign">The team does not demonstrate a process for manual accessibility testing.
      <br><br>Website uses insufficient color contrast and small text sizes, causing eye strain. </td>
    </tr>
    </tbody>
  </table>
</div>

<a name="research"></a>
### User Research/Usability Testing  

The following indicators can help determine if a usability test will produce useful results. This is not an exhaustive list, but it should be helpful in planning and assessing usability tests.  

<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th class="col-indicator">Indicator</th>
        <th class="col-good-sign">Good sign</th>
        <th class="col-bad-sign">Bad sign</th>
      </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan="3"><b>Study design</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Study purpose</td>
      <td class="col-good-sign">Researcher clearly articulates the purpose of the study (for example, as a specific question to answer, an area of inquiry, etc.). </td>
      <td class="col-bad-sign">Researcher does not specify a purpose for the study , or the purpose specified is very broad, like “testing the app” or “finding problems.” </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Number of participants </td>
      <td class="col-good-sign">Studies include a sufficient number of participants necessary to see patterns, and there’s only one participant per session. </td>
      <td class="col-bad-sign">Study includes only one participant, or includes multiple participants tested simultaneously where participants can influence one another (like a focus group ).</td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Sampling bias </td>
      <td class="col-good-sign">Participants are a diverse group of people who actually use the application or do tasks that are being investigated.  </td>
      <td class="col-bad-sign">Participants are experts (vs. average users), friends, family, or close colleagues of the product team. Participants are homogenous with regard to abilities, background, and demographics, and as a result do not represent the user population. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Privacy awareness </td>
      <td class="col-good-sign">Researchers get informed consent from each participant before starting research activities so that participants know what the study entails, how their feedback will be used, and their right to opt out.  
      <br><br>The research team is aligned on how to hold up their end of  informed consent agreements in their research work. (e.g. where records are stored, anonymizing notes) </td>
      <td class="col-bad-sign">Informed consent is not collected and participants are unclear how their data will be used.  
      <br><br>The team isn’t clear or does not respect how the informed consent agreement impacts their research work.  </td>
    </tr>
    <tr>
      <td colspan="3"><b>Moderator style</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Participant comfort </td>
      <td class="col-good-sign">Participants feel comfortable taking some time to give an answer. </td>
      <td class="col-bad-sign">Researcher fills any “awkward pauses” with rephrasing or leading questions. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Question style  </td>
      <td class="col-good-sign">Researcher asks follow up questions that are open-ended and non-leading.
      <br><br>Researchers give participants opportunities to question design decisions and give participants space to share their thoughts and experiences.  </td>
      <td class="col-bad-sign">Questions are leading or subtly suggest potential solutions or hypotheses.
      <br><br>Researcher asks participants to confirm design decisions. For example, “This content makes sense, right?” </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Task variability</td>
      <td class="col-good-sign">Researcher asks participants to complete similar tasks related to the study’s purpose. </td>
      <td class="col-bad-sign">Researcher asks participants to complete different tasks, or tasks unrelated to the study’s purpose. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Framing</td>
      <td class="col-good-sign">Researcher asks participants to complete tasks with the product or service that align with the participant’s work-related goals. </td>
      <td class="col-bad-sign">Researcher asks participants to complete tasks unrelated to their work-related goals. For example, asking a participant how they might send a fax when their job doesn’t call for that. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Priming </td>
      <td class="col-good-sign">Researcher asks participants to complete tasks without indicating how that might be done. For example, “How would you view the status of your application?”
      <br><br>Questions allow for multiple answers. For example, “Walk me through what happens when you get a ticket.” </td>
      <td class="col-bad-sign">Researcher guides participants in completing tasks or two a particular answer. For example, “Which of the links in the header would you click to log in?” </td>
    </tr>
    <tr>
      <td colspan="3"><b>Team participation</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Number of teammates </td>
      <td class="col-good-sign">The team designates a single moderator for the test, and at least one member of the product team observes the usability test.
      <br><br> researcher is mindful of who’s participating in a research session and limits observers so that participants feel comfortable sharing </td>
      <td class="col-bad-sign">A single person from the product team participates in and leads the study.
      <br><br> include a large number of observers that make participants uncomfortable (e.g. more than four non participants).  </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Observer role </td>
      <td class="col-good-sign">Observers do not moderate. They are generally quiet, and ask open-ended questions after the session has concluded. </td>
      <td class="col-bad-sign">Observers interrupt the participant, or attempt to sell or explain the product. Observers debate the participant’s actions in their presence. </td>
    </tr>
    <tr>
      <td colspan="3"><b>Sensemaking</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Notetaking </td>
      <td class="col-good-sign">Studies are recorded or notes are taken for sharing with absent stakeholders. </td>
      <td class="col-bad-sign">Studies are not recorded or notes are not taken or available to the team. Test results are not documented. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Synthesis </td>
      <td class="col-good-sign">Moderator debriefs with teammates immediately after each interview. Researcher looks for patterns across multiple participants and surfaces problems that affected several people. </td>
      <td class="col-bad-sign">Moderator reports the most memorable problems without conducting affinity mapping or some other analysis technique. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Presentation of findings </td>
      <td class="col-good-sign">Researcher reports findings to team and stakeholders in an easy to follow, well prioritized way. They cite actual observations and voices where possible. </td>
      <td class="col-bad-sign">Researcher presents team a “basket of issues” or an unprioritized laundry list of potential changes. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Incorporation of findings </td>
      <td class="col-good-sign">Product team translates findings into future user stories or product refinements. </td>
      <td class="col-bad-sign"Researcher reports do not affect the product backlog or ongoing development work. </td>
    </tr>
    </tbody>
  </table>
</div>

<a name="content"></a>
### Content  

A content heuristic is the specific, identifiable, and measurable qualities that content should have in order to achieve positive user experiences.  

It is not enough to say that content should be ‘clear;’ instead it is more helpful to describe what clear content means for the user experience and how it should be demonstrated. Content heuristics are used to evaluate how well we are producing clear content and can be used during a content audit and user testing. With this in mind, here’s how we are defining clear, actionable, and accurate content.

<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th class="col-indicator">Indicator</th>
        <th class="col-good-sign">Good sign</th>
        <th class="col-bad-sign">Bad sign</th>
      </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan="3"><b>Clear content</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Helpful, contextual titles </td>
      <td class="col-good-sign">Use topic headings and subheadings to organize information and one main idea at a time.
      <br><br>Write specific navigation and page titles, headings, and labels that indicate what information users can expect to find and make it easier for them to pinpoint an answer </td>
      <td class="col-bad-sign">Headings and sections have no hierarchy; navigation titles are general or repeated throughout the page (e.g. “read more”) </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Concise, meaningful paragraphs </td>
      <td class="col-good-sign">Page summary paragraph at the top of each web page that tells you exactly what information can be found on the page.
      <br><br>Simple paragraphs, no more than 3-5 sentences long, that describe the main idea and most important points of a process or task.
      <br><br>Shorter sentences that communicate one idea or step at a time.
      </td>
      <td class="col-bad-sign">No page summary or a summary that’s more than half as long as the rest of the page.
      <br><br>Complex paragraphs longer than 5 sentences long that digress or include information that does not support the main idea.
      <br><br>Long sentences that include multiple sub-clauses or communicate too many steps or ideas at a time. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Consistent formatting and styling </td>
      <td class="col-good-sign">Numbered or bulleted lists when describing step-by-step instructions.
      <br><br>More white space on the page and visually less text-heavy.
      <br><br>Consistent standards for the application of text bolding, underlining, and italicizing. </td>
      <td class="col-bad-sign">Instructions not broken down by step. More text than white space on a page.
      <br><br>Inconsistent use of bolding, underlining, or italicizing. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Use of plain language techniques </td>
      <td class="col-good-sign">Break up dense and lengthy text by creating new topic pages.
      <br><br>Target a readability grade level and score under 12.
      <br><br>Avoid using acronyms. When an acronym is necessary, define and spell it out the first time you use it. </td>
      <td class="col-bad-sign">Pages that cover multiple topics.
      <br><br>Reading the page requires a readability grade level and score above 12.
      <br><br>Content uses jargon or acronyms that are not spelled out. </td>
    </tr>
    <tr>
      <td colspan="3"><b>Actionable content</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Specific call-to-action </td>
      <td class="col-good-sign">Direct users to a person or point of contact to get help if they need help completing a task.
      <br><br>Direct users to the tools, documents, or materials they need to complete a task. </td>
      <td class="col-bad-sign">Users don’t have a clear path to help when they are likely to need it.
      <br><br>Access to tools, documents, or materials needed to complete a task are not included. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Instructive sentences </td>
      <td class="col-good-sign">Provide information that tells users how to complete a task.
      <br><br>Indicate what the next steps are once a task is complete.
      <br><br>Explain who is responsible for completing a task or managing a process, and what the user is required to do compared to other stakeholders involved in the process. </td>
      <td class="col-bad-sign">Information about how to complete tasks is not provided.
      <br><br>Next steps after the task are not provided.
      <br><br>Responsibility for completing a task or managing a process is not explained, and what the user is required to do compared to other stakeholders involved is not differentiated. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Illustrate and/or outline the timeline </td>
      <td class="col-good-sign">Communicate about a task or process’ overall timeline, including deadlines, dependencies, duration, and any other time-sensitive activities.  
      <br><br>Inform users where they are in the process.  
      <br><br>Inform users what done or successful task completion looks like. </td>
      <td class="col-bad-sign">Description of tasks or processes include no or not enough information about timelines, deadlines, dependencies, duration, or other time-sensitivity.
      <br><br>No information about what successful task completion looks like is provided. </td>
    </tr>
    <tr>
      <td colspan="3"><b>Accurate content</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Consistency across channels </td>
      <td class="col-good-sign">The information we provide is consistent with policies at all levels  </td>
      <td class="col-bad-sign">Information is provided that conflicts with or is inconsistent with policies at all levels  </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Verifiable information </td>
      <td class="col-good-sign">The correct point of contact information (e.g., name of person, phone, email, etc) is listed to answer questions and learn more. </td>
      <td class="col-bad-sign">Incorrect contact information is provided, or no contact information is provided. </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Timely and trustworthy information </td>
      <td class="col-good-sign">The user can trust and identify that the information is up-to-date. </td>
      <td class="col-bad-sign">The user cannot be sure that the information is up-to-date. </td>
    </tr>
    </tbody>
  </table>
</div>

<a name="product"></a>
## Product Team

The following indicators are intended to help stakeholders understand whether the product team has the leadership it needs in order to be successful.  

“Product personnel” for the TDRS project include the OFA’s Product Owner and the vendor’s Facilitator.  Between these two, responsibly for the items below may be shared. Ultimately, both should understand a problem space and articulate a vision for the product. The Product Owner should serve as a proxy for end users, provide day-to-day prioritization, and be the ultimate decision maker. The Facilitator on the other hand, should prioritize making sure the team is always focused on the right priorities and removing blockers for the team.  

<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th class="col-indicator">Indicator</th>
        <th class="col-good-sign">Good sign</th>
        <th class="col-bad-sign">Bad sign</th>
      </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan="3"><b>People operations</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Availability </td>
      <td class="col-good-sign">Product personnel are allocated to work on the project (<b>at least</b> 50% time) for the duration of the engagement</td>
      <td class="col-bad-sign">Have other full time roles; are expected to treat the product role as “other duties as assigned” </td>
    </tr>
    <tr>
      <td colspan="3"><b>Foundational knowledge and skills</b> </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Product basics </td>
      <td class="col-good-sign">Is trained in core product management practices most valuable to them (e.g. roadmapping and strategic product thinking, scrum, cross-functional team management) </td>
      <td class="col-bad-sign">Participate only as a subject matter expert; do not lead the team </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator"Bias toward action </td>
      <td class="col-good-sign">Demonstrate a bias toward action over philosophy, testing hypotheses, learning from failure, embrace experimentation, iteration, and uncertainty, etc. </td>
      <td class="col-bad-sign">Issues are frequently blocked because product can’t make a decision; they prioritize leadership consensus over experimentation and hypothesis testing </td>
    </tr>
    <tr>
      <td colspan="3"><b>Leadership</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Feedback culture </td>
      <td class="col-good-sign">Facilitate a culture where team members feel comfortable sharing feedback about all aspects of the project </td>
      <td class="col-bad-sign">Team members do not offer feedback; retros produce no useful insights </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Cross-functional teams </td>
      <td class="col-good-sign">Facilitate discussions around tradeoffs to design and engineering decisions, and seek team’s consensus on the best path forward </td>
      <td class="col-bad-sign">Team functions are siloed; how product decisions may impact dependencies among design, development, and architecture are not surfaced in time to inform decisions </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Decision making </td>
      <td class="col-good-sign">Make decisions about the product </td>
      <td class="col-bad-sign">Defer major product decisions to others on the team </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Communication and collaboration </td>
      <td class="col-good-sign">The team has a shared understanding of where, when, and how to communicate with each other; Key stakeholders know how they can contribute to the project as well as how to effectively give feedback to the project team </td>
      <td class="col-bad-sign">Team communication is not happening; people don’t know where to look or who to turn to with questions about the work or the product </td>
    </tr>
    <tr>
      <td colspan="3"><b>Self care</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Learning goals </td>
      <td class="col-good-sign">Attend professional development trainings, conferences and other activities that support professional development goals; read professional journals and articles related to product practice and attends professional development trainings </td>
      <td class="col-bad-sign">Do not attend or engage in coaching sessions; are not aware of the current practices, developments, or debates in the field </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Work-life balance </td>
      <td class="col-good-sign">Set clear boundaries with their time; only works 40 hours week </td>
      <td class="col-bad-sign"></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator"></td>
      <td class="col-good-sign"></td>
      <td class="col-bad-sign"></td>
    </tr>
    <tr>
      <td colspan="3"><b>Delivery</b></td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Situational awareness </td>
      <td class="col-good-sign">Product personnel understand and can explain: the state of the product, major implementation decisions made during product development, technologies used to build the product, work needed to further develop the product. </td>
      <td class="col-bad-sign">Are not aware of major implementation decisions, cannot articulate the product’s trajectory </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Scoping </td>
      <td class="col-good-sign">Can identify the Minimally Viable Product (MVP) from the roadmap with a focus on “must haves,” or non-negotiable functionality that will deliver a high value to end users </td>
      <td class="col-bad-sign">Are reactive to feature requests from stakeholders and users; scope an MVP that is overly complicated; MVP scope significantly expands, delaying release </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Security- and privacy-minded </td>
      <td class="col-good-sign">Use authorized tools/platforms (via FedRAMP, when possible) to support desired build methodology and get an ATO if necessary </td>
      <td class="col-bad-sign">Does not ask or assess whether ATOs are needed; uses and/or allows the use of unauthorized tools; is not aware of how ATO, SORN and/or other compliance processes may impact the product roadmap; </td>
    </tr>
    <tr valign="top">
      <td class="col-indicator">Measures success </td>
      <td class="col-good-sign">Goals, outcomes, and targets have appropriate, realistic measures indicating how we’ll know when they’re met; Uses these metrics to forecast and adjust the trajectory of the project </td>
      <td class="col-bad-sign">Goals and metrics are not identified or adhered to; goals and metrics are not achievable or specific and/or are not directly tied to measures of user value </td>
    </tr>
    </tbody>
  </table>
</div>  
