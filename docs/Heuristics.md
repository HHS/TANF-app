# ACF OFA Skill area heuristics  

## Goal of this document:  

This document was created  to help OFA staff assess whether the product development team performs satisfactorily and identify areas for improvement. We built this from 18F's evaluation practices for our own internal and external work.  

It is not meant to replace the [Quality Assurance Surveillance Plan (QASP)](https://github.com/18F/tdrs-app-rfq/blob/main/Final-RFQ/FINAL-TDRS-software-development-RFQ.md#32-quality-assurance-surveillance-plan-qasp), acceptance criteria, or to be an exhaustive checklist for all work. These heuristics should compliment contractual evaluative measures and be used to identify feedback opportunities within the team.

## Code Maintainability Heuristics  

Understanding code quality and maintainability requires examining the code itself and comprehending it at least at a high level. The indicators below are generally intended for someone who already has the knowledge to do that, but each one includes steps that a non-coder can take to help determine if things are going well or not.  

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
        <td class="col-indicator"></td>
        <td class="col-good-sign"></td>
        <td class="col-bad-sign"></td>
      </tr>
    </tbody>
  </table>
</div>


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
        <br><br> **Non dev:** The dev team will not have similar code throughout the code base, but will design it so that central modules can be reused. </td>
        <td class="col-bad-sign">Common functionality uses custom code.
        <br><br>The same methods are repeated throughout different files.
        <br><br>Custom components that deviate from USWDS guidance are common. </td>
      </tr>


    </tbody>
  </table>
</div>

## Design heuristics  - fix links

Design touches every area of the product, and can mean different things to different teams at different times. The work you'll evaluate may vary from sprint-to-sprint; you may review research plans on week and user interface mockups the next. No matter the work, these design heuristics are the specific markers to look for to ensure design decisions are user centered, ethical, and maintainable.  

These indicators are meant to help evaluate the practices and work of a design team. In addition to general design heuristics, there are also specific indicators for evaluating accessibility, usability tests and research, and content.

### Universal Design (Accessibility) Heuristics  

The following indicators support design of barrier-free digital products that can be used by everyone. The "good signs" and "bad signs" are merely examples; they are in no way comprehensive.  

The [Principles of Universal Design](https://projects.ncsu.edu/ncsu/design/cud/about_ud/udprinciplestext.htm) were initially developed in 1997 at the Center for Universal Design at North Carolina State University, funded by the U.S. Department of Education's National Institute on Disability and Rehabilitation Research.

### User Research/Usability Test Heuristics  

The following indicators can help determine if a usability test will produce useful results. This is not an exhaustive list, but it should be helpful in planning and assessing usability tests.  

### Content Heuristics  

A content heuristic is the specific, identifiable, and measurable qualities that content should have in order to achieve positive user experiences.  

It is not enough to say that content should be ‘clear;’ instead it is more helpful to describe what clear content means for the user experience and how it should be demonstrated. Content heuristics are used to evaluate how well we are producing clear content and can be used during a content audit and user testing. With this in mind, here’s how we are defining clear, actionable, and accurate content.  

## Product Team Heuristics  

The following indicators are intended to help stakeholders understand whether the product team has the leadership it needs in order to be successful.  

“Product personnel” for the TDRS project include the OFA’s Product Owner and the vendor’s Facilitator.  Between these two, responsibly for the items below may be shared. Ultimately, both should understand a problem space and articulate a vision for the product. The Product Owner should serve as a proxy for end users, provide day-to-day prioritization, and be the ultimate decision maker. The Facilitator on the other hand, should prioritize making sure the team is always focused on the right priorities and removing blockers for the team.  
