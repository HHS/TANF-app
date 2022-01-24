# Markdown practices

**Table of Contents:**
- [Code docs](#Code-docs)
- [Patterns](#Patterns)

---

## Code docs

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