# Design guide

**Table of Contents:**

- [Content Guide](#content-guide)
- [Accessibility](#accessibility)
- [Visual styling](#visual-styling)
- [Figma artifacts](#figma-artifacts)
- [Code docs](#code-docs)

---

# Content guide

We're continuing to learn about the content needs of the new TDRS. Future teams should plan to write in plain language and continually test site navigation and comprehension. Documentation in code docs should ensure that usage of TANF-related terms remains consistent with the definitions found in the Project Glossary.

**Resources:**

* [ACF content guide](https://www.acf.hhs.gov/digital-toolbox/content)
* [plainlanguage.gov](https://plainlanguage.gov/)
* [18F content guide](https://content-guide.18f.gov/)
* [Project Glossary](https://github.com/HHS/TANF-app/blob/main/docs/Background/Project-Glossary.md)

---

# Accessibility

Everyone who works on government websites has a role to play in making federal resources accessible and inclusive. The new TDRS should meet 508 accessibility standards and use accessible design and development best practices.

**Resources:**

* [Accessibility for teams](https://accessibility.digital.gov/)
* [18F Accessibility guide](https://accessibility.18f.gov/)
* [Section508.gov](https://www.section508.gov/)

---

# Visual styling

## ACF styles

Information on existing ACF styles can be found in the [ACF Digital Toolbox](https://www.acf.hhs.gov/digital-toolbox)

* [ACF Colors](https://www.acf.hhs.gov/digital-toolbox/visuals/visual-style-guide)

* [ACF Typography](https://www.acf.hhs.gov/digital-toolbox/visuals/typography-and-fonts)

  

## U.S. Web Design System (USWDS)

We'll be using  [USWDS](https://designsystem.digital.gov/), a design system for the federal government, for the new TANF Data Portal (TDP). USWDS provides us with UX guidance and code for [common UI components](https://designsystem.digital.gov/components/) as well as [guidance on how to comply with the 21st Century Integrated Digital Experiences Act (IDEA)](https://designsystem.digital.gov/website-standards/?dg).

---

# Figma artifacts

## User flows

To improve our workflow in ideating and supporting development, we created a [user flows page](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=1277%3A8087>) in Figma to map and explore user actions and outcomes in a modular environment that can be easily changed and extended. 

This living document covers actions a user would take, system actions that happen on the backend, and destinations that are reached after actions are executed. To communicate how these actions and outcomes intertwine, we included primary and secondary paths that a user can take within the flow. These flows have also proven useful for certain security/compliance workflow documentation needs.

## Mockups & prototypes

[Full Site](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=0%3A1>) - A visual site map page encompassing all reviewed dev-ready mockups that responsible parties deliver.

**Reviewed**

-  [Upload and Download Data Reports](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=2933%3A0>) associated with issues [#427](https://github.com/raft-tech/TANF-app/issues/427) and [#415](https://github.com/raft-tech/TANF-app/issues/415)
-  [User Management (Admin tools)](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=2441%3A12231>) associated with issues [#404](https://github.com/raft-tech/TANF-app/issues/404), [#327](https://github.com/raft-tech/TANF-app/issues/327), and [#164](https://github.com/raft-tech/TANF-app/issues/164)
-  [Reset Password](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=2933%3A0>) associated with issue [#318](https://github.com/raft-tech/TANF-app/issues/318)
-  [Concept Prototype (For round 3 research)](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=1381%3A0>) associated with issues [#275](https://github.com/raft-tech/TANF-app/issues/275) and [#115](https://github.com/raft-tech/TANF-app/issues/115)
-  [Responsive Mobile Designs (Admin pages)](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=618%3A14>) associated with issue [#178](https://github.com/raft-tech/TANF-app/issues/178)
-  [Request Access (New user)](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=628%3A468>) associated with issue [#166](https://github.com/raft-tech/TANF-app/issues/166)

**In Backlog**

- [Ideas on Validation](<https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=1412%3A9795>) associated with issue [#295](https://github.com/raft-tech/TANF-app/issues/295)

---

# Code docs

## Markdown practices

**Linking to Teams**

Certain documents—particularly some shared out of Teams—may include spaces in their URLs. When this is the case, the URL needs to be book-ended by angle brackets to get GitHub to honor the link. 

Ex.

`[Link Name](<www.example-url.com/contains a space>)`



**Image alt-text**

To ensure that documentation maintains a high degree of accessibility it's important to include descriptive alt-text if and whenever non-decorative images are embedded within markdown documents. The 'alt' attribute can be used in GitHub Markdown much like it is in a normal HTML webpage. 

Ex. 

`<img src="https://goraft.tech/assets/logo.png" width="15%" height="auto" alt="Raft LLC Logo">`



**Anchor Linking**

Headings in markdown provide not only a way to organize content, but a way to link directly to different parts of it. Keep in mind that GitHub's markdown syntax differs from that of other markdown tools. To make sure your header links work consistently, ensure that you reference the header text in all lowercase and with any spaces in the header replaced with hyphens. 

Note: You can link to any header on the page using the format below regardless of whether it's an H1, H2, etc... In other words, an H2 header rendered in markdown as `##Heading 2` can still be linked to using a single number sign.

Ex. 

`[Figma artifacts](#figma-artifacts)`



## Patterns

**Headings**

At least one top-level (H1) heading that provides an accurate description of the content should be present on all documents. When there's a need to group content into subsections, heading tags should be used in ascending order, e.g. If a sub-heading is needed beneath an H1 heading, it should always be an H2 rather than skipping right to a higher numbered heading. 



**Table of contents**

Any document organized into different sections by heading should include a table of contents that utilizes anchor links and provides a descriptive overview of the content the reader can expect to find. 

Ex. 

```markdown
**Table of Contents:**

- [Content Guide](#content-guide)
- [Accessibility](#accessibility)
- [Visual styling](#visual-styling)
- [Figma artifacts](#figma-artifacts)
- [Code docs](#code-docs)
```



**Secured links**

Any link to secured content—whether password protected or otherwise restricted—should be labeled with a ​":lock:'' to signal that it's secured before somebody who may not have access clicks it. This labeling should rely on markdown, not embedded images. 

Ex. 

`[Secured Content](www.secured-link-example.com) :lock:`