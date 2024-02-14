# Accessibility Guide

**Table of Contents:**
- [Background](#Background)
- [Relevant standards](#Relevant-standards)
- [State of a11y in TDP](#State-of-a11y-in-TDP)
- [What to keep in mind when testing](#What-to-keep-in-mind-when-testing)
- [Testing tools](#Testing-tools)
- [Screen reader use and setup](#Screen-reader-use-and-setup)
- [Do's and don'ts when designing](#Dos-and-donts-when-designing)
- [References](#References)

---

## Background
This document has evolved from its initial state of "Helpful a11y stuff" to one intended to serve more as a guided tour of Raft's accessibility (a11y) practice aimed at enabling more testing and broadly more *consideration* of a11y to be shifted left. 

Additionally, this resource will also aim to document the current state of a11y in TDP to track outstanding enhancements or a11y fixes and to help commentate some issues that may be encountered when testing TDP pages for accessibility conformance. While TDP remains highly accessible as a whole there are certain issues we've identified that demand follow-on work to research or correct. There are also a number of false positives that certain a11y testing tools can identify as problematic. 

---

## Relevant standards
There are numerous areas of accessibility law that apply to our work ranging from the ADA (Americans with Disabilities Act) which lays out the broad requirement of accessibility in public spaces and systems to Section 508 of the Rehabilitation Act which mandates a specific standard that Federal systems & resources need to adhere to—specifically WCAG (Web Content Accessibility Standards) 2.0 AA. [See more on US accessibility law](https://www.ada.gov/resources/disability-rights-guide/#top).

WCAG 2.x standards have four categories with which to evaluate accessibility; Perceivable, Operable, Understandable, and Robust. Within all four categories are three levels of conformance, A, AA, AAA; respectively these correspond to the most barebones standards, good baseline standards, and the most specific standards.

---

## State of a11y in TDP
The [errors audit](https://hackmd.io/79rAOVzISbOvaTNv8nSpeA) tracks all outstanding accessibility issues in the TANF Data Portal, its knowledge center, and Django Admin console. 

---

## What to keep in mind when testing
The full picture of what makes for *complete* accessibility testing involves every check in Accessibility Insight's Full Assessment tool, thoughtfulness around what makes for a good experience through the lens of various assistive technologies, and real-world usability testing with people experiencing disabilities. This guide isn't going to be able to deliver all that—but it will seek to lay out some illustrative examples and frequently useful questions to pose of an experience when you're testing it for conformance. 

The following checklist is organized via WCAG 2.x's categories. While a few items explicitly involve screen-readers or other assistive technologies, most items should be able to be checked "yes" regardless of your mode of interaction with the webpage (vision & mouse, keyboard only, screenreader, etc...). 


### Is it Perceivable? 
The user must be able to *perceive* all the information being presented. 

- [ ] If there are non-decorative images on the page, do they have alt-text?
   - [ ] Does the alt text convey all the relevant information a sighted user would get from the image?
- [ ] Is there a visible focus indicator for every element of the interface as you tab through it? 
- [ ] Do all interface items have sufficient contrast against their backgrounds?
    - [ ] If information is communicated by color are there also alternatives beyond color for folks who can't see or distinguish the colors?
- [ ] Do related areas of the interface have visual proximity to each other?
- [ ] Are all interface items read correctly by screenreaders?

### Is it Operable?
The user must be able to *use* all interactive portions of the experience—and navigate to all areas of it. 

- [ ] When navigating the page with the keyboard can you tab to every interactive element?
   - [ ] Is the order in which items are focused logical?
   - [ ] If there's a disabled element is it correctly marked up with ARIA and read to screen readers? 
- [ ] Is there sufficient (read as: generous) time to read and interact with transient elements of the page (e.g. the timeout modal dialog)?
- [ ] Does the navigable experience "shrink" when pop-over content is open? (e.g. Modal dialogs & the opened side navigation)
    - [ ] Is content behind the pop-over content shaded out?
    - [ ] Is keyboard focus constrained to the pop-over content alone?

### Is it Understandable?
The user must be able to understand the information being presented by the experience and *how* to operate it. 

- [ ] Is the language used on the page [plain](https://www.plainlanguage.gov/guidelines/) rather than technical or overcomplicated? 
   - [ ] Are abbreviations defined alongside their first usage?
   - [ ] Are unusual words explained?
- [ ] Do interface elements used for navigation appear and behave consistently throughout the experience?
- [ ] Does the experience make it clear when elements or page contexts change? (e.g. When you navigate to a new page or a new piece of content appears)
- [ ] Are there labels and instructions on the page to help prevent errors?
   - [ ] When errors appear is it clear what action or form item they relate to? 
   - [ ] When errors appear do they suggest something for the user to try next to correct or move past them?

### Is it Robust?
The experience and the content within it need to be *reliable* and play nicely with a range of assistive technologies. 

- [ ] Does this experience work as intended when navigated via Safari and Voiceover?
   - [ ] Does it work as intended when tested in other browsers and via other screen readers? 
- [ ] Is the page parsed correctly by testing tools? 


---

## Testing tools




### In-browser tools

| Extension                  | Description                                                  | Link                                                         |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Alt-text tester**        | Flags images on a page that are missing alt text, provides an easy way to view alt text for any image that has it. | [Chrome](https://chrome.google.com/webstore/detail/alt-text-tester/koldhcllpbdfcdpfpbldbicbgddglodk?hl=en) |
| **Accessibility Insights** | Great for getting familiar with WCAG. It has both fast-pass assessments and a guided way to do manual testing. Plus—when doing manual testing—deep dive explainers on each test (see the info buttons next to the headings of any given test). | [Chrome](https://chrome.google.com/webstore/detail/accessibility-insights-fo/pbjjkligggfmakdaogkfomddhfmpjeni), [Edge](https://microsoftedge.microsoft.com/addons/detail/ghbhpcookfemncgoinjblecnilppimih) |
| **Axe DevTools**           | Great fast-pass scanner, will identify best practice issues as well as WCAG compliance violations. | [Chrome](https://chrome.google.com/webstore/detail/axe-devtools-web-accessib/lhdoppojpmngadmnindnejefpokejbdd?hl=en-US), [Firefox](https://addons.mozilla.org/en-US/firefox/addon/axe-devtools/), [Edge](https://microsoftedge.microsoft.com/addons/detail/axe-devtools-web-access/kcenlimkmjjkdfcaleembgmldmnnlfkn) |
| **Accessible Colors**      | Web tool tool that will tell you whether two hex codes have sufficient contrast with each other, show you what they look like, and suggests the closest alternative color if they don't have sufficient contrast. Note that the default values for font size, weight, and compliance can be left alone for most purposes. | [Site](https://accessible-colors.com/)                       |


If you go through all the manual tests in the full Accessibility Insights assessment having these scripts bookmarked will be useful! Running them is as simple as opening the bookmark while viewing the page you're testing.

**Tests whether page text can be spaced out and comply with requirements without breaking layout**

````
javascript:(function(){ var style = document.createElement(%27style%27), styleContent = document.createTextNode(%27* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; } p{ margin-bottom: 2em !important; } %27); style.appendChild(styleContent ); document.getElementsByTagName(%27head%27)[0].appendChild(style); var iframes = document.querySelectorAll(%27iframe%27);for (var i=0; i<iframes.length; i++) {try{iframes[i].contentWindow.document.getElementsByTagName(%27head%27)[0].appendChild(style); } catch(error) { console.log(%27Bookmarklet error: %27+error)}}})();
````

**Checks serialized DOM of current page**

````
javascript:(function(){function c(a,b){var c=document.createElement("textarea");c.name=a;c.value=b;d.appendChild(c)}var e=function(a){for(var b="",a=a.firstChild;a;){switch(a.nodeType){case Node.ELEMENT_NODE:b+=a.outerHTML;break;case Node.TEXT_NODE:b+=a.nodeValue;break;case Node.CDATA_SECTION_NODE:b+="<![CDATA["+a.nodeValue+"]]\>";break;case Node.COMMENT_NODE:b+="<\!--"+a.nodeValue+"--\>";break;case Node.DOCUMENT_TYPE_NODE:b+="<!DOCTYPE "+a.name+">\n"}a=a.nextSibling}return b}(document),d=document.createElement("form");d.method="POST";d.action="https://validator.w3.org/nu/";d.enctype="multipart/form-data";d.target="_blank";d.acceptCharset="utf-8";c("showsource","yes");c("content",e);document.body.appendChild(d);d.submit()})();
````

**Filters results of the above to only WCAG 2.0 violations**

````
javascript:(function(){var removeNg=true;var filterStrings=["tag seen","Stray end tag","Bad start tag","violates nesting rules","Duplicate ID","first occurrence of ID","Unclosed element","not allowed as child of element","unclosed elements","not allowed on element","unquoted attribute value","Duplicate attribute"];var filterRE,root,results,result,resultText,i,cnt=0;filterRE=filterStrings.join("|");root=document.getElementById("results");if(!root){alert("No results container found.");return}results=root.getElementsByTagName("li");for(i=0;i<results.length;i++){result=results[i];if(result.className!==""){resultText=(result.innerText!==undefined?result.innerText:result.textContent)+"";if(resultText.match(filterRE)===null){result.style.display="none";result.className=result.className+" steveNoLike";cnt++}else if(removeNg==true){if(resultText.indexOf("not allowed on element")!==-1&&resultText.indexOf("ng-")!==-1){result.style.display="none";result.className=result.className+" steveNoLike";cnt++}}}}alert("Complete. "+cnt+" items removed.")})();
````

*Note that the serialized DOM check will sometimes flag things from Chrome extensions if you have any that inject javascript anywhere on the page* 

---

## Screen reader use and setup
Screen readers allow blind or visually impaired users to read and navigate the content of an experience via speech synthesis or output to other assistive technologies like braille displays. Screen readers allow for multiple modes of browsing information. Some of the most key methods allow users to navigate via skip-links, landmarks, and page headings, tab among focusable elements like links, buttons, and form fields, and simply reading *all* page content.

While there are a ton of keyboard shortcuts for screen readers, your core navigation for testing purposes will generally be the following: 



| Action                                                       | Command                                              |
| ------------------------------------------------------------ | ---------------------------------------------------- |
| Next focusable element                                       | Tab                                                  |
| Previous focusable element                                   | Shift-Tab                                            |
| Activate a link                                              | Enter                                                |
| Activate a button                                            | Enter or Space                                       |
| Navigate certain form elements, tables, or general page content in reading modes | Arrow keys (sometimes modified with Control/Command) |



### Setting up Voiceover on MacOS
If you're on MacOS you'll need to [tweak some settings](https://dequeuniversity.com/mac/keyboard-access-mac) that Apple disables by default. Once you've done that you'll get the correct accessibility behavior when manual testing with VoiceOver in Safari. 

See also: [Deque University — VoiceOver Keyboard Shortcuts](https://media.dequeuniversity.com/courses/generic/testing-screen-readers/2.0/en/docs/voiceover-macos-guide.pdf).

### Setting up NVDA on Windows
*Note: While current TDP functionality should behave similarly across browsers, NVDA is most directly developed for stability on Firefox.* 
[NVDA Download](https://www.nvaccess.org/download/)

See also: [Deque University — NVDA Keyboard Shortcuts](https://dequeuniversity.com/screenreaders/nvda-keyboard-shortcuts).


### Narrator Scan Mode on Windows

If you're on Windows the built in screenreader (Narrator) has something called Scan Mode that tries to auto read through pages instead of relying entirely on the user to tab and arrow through. It breaks a lot of stuff, including the combobox (not just ours, but a lot of other components out there), so [knowing how to turn that off](https://www.tenforums.com/tutorials/134464-turn-off-use-narrator-scan-mode-windows-10-a.html) for testing is useful!

### Mobile screen readers
iOS/iPadOS both use VoiceOver and you'll get a similar experience to that of VoiceOver on MacOS. Android's built in reader is called Talkback. While they support physical keyboards and normal focus when devices have them, mobile screenreaders also use interesting pseudo-states aimed at enabling touch-screen-only use. Due to those pseudo states, normal touches/swipes/drags will tend to focus & read screen elements and double-taps will activate them.


---

## Do's and don'ts when designing

### Do's
- Use simple colors, good contrast, and readable font size  
- Make sure the contrast between the text and background is greater than or equal to 4.5:1 for small text and 3:1 for large text.  
- Write in plain English  
- Use simple sentences and bullets  
- Make buttons descriptive - for example, Attach files  
- Build simple and consistent layouts  
- Create a clear hierarchy of importance by placing items on the screen according to their relative level of importance. For example, place important actions at the top or bottom of the screen (reachable with shortcuts).  
- Follow a linear, logical layout -and ensure text flows and is visible when text is magnified to 200%   
- Align text to the left   
- Write descriptive links and headings - for example, Contact us  
- Avoid underline words, use italics or write capitals unless necessary  

### Don'ts
- Use bright contrasting colors, low color contrasts, and small font size  
- Only use color to convey meaning  
- Give form fields space  
- Design with mobile and touch screen in mind  
- Use figures of speech and idioms  
- Create a wall of text  
- Make buttons vague and unpredictable - for example, Click here  
- Build complex and cluttered layouts  
- Only show information in an image or video  
- Spread content all over a page  
- Rely on text size and placement for structure  
- Force mouse or screen use  
- Write uninformative links and heading - for example, Click here  
- Bury information in downloads  
- Spread content all over a page -and force user to scroll horizontally when text is magnified to 200%  
- Separate actions from their context  
- Demand precision  
- Bunch interactions together  
- Make dynamic content that requires a lot of mouse movement  
- Have short time out windows  
- Tire users with lots of typing and scrolling  
- Use subtitles or provide transcripts for video  
- Use a linear, logical layout  
- Break up content with sub-headings, images and videos  
- Let users ask for their preferred communication support when booking appointments  
- Force users to remember things from previous pages - give reminders and prompts  
- Rely on accurate spelling - use autocorrect or provide suggestions  
- Put too much information in one place  



---

## References

### Miscellaneous Resources
- [Introduction to ARIA](https://www.lullabot.com/articles/what-heck-aria-beginners-guide-aria-accessibility)
- [Broad a11y introduction](https://www.deque.com/web-accessibility-101/)
- [Disability Statistics](https://www.cdc.gov/ncbddd/disabilityandhealth/infographic-disability-impacts-all.html)
- [Current standards for compliance](https://www.w3.org/TR/WCAG21/)
- [Beyond Compliance: Improving USWDS Accessibility](https://goraft.tech/2021/07/07/Beyond-Compliance-Improving-USWDS-Accessibility.html)
- [Designing for inclusion](https://inclusivedesignprinciples.org/)  
- [18F’s Accessibility Guide](https://accessibility.18f.gov/index.html)
- [Making your service accessible (Service Manual (UK))](https://www.gov.uk/service-manual/helping-people-to-use-your-service/making-your-service-accessible-an-introduction)


### A11y & React
- [Accessible Routing in React](https://timwright.org/blog/2019/03/23/accessible-routing-in-react/)

- [ReactJS Focus Control](https://reactjs.org/docs/accessibility.html#focus-control)

- [Simply Accessible — React Accessibility](https://simplyaccessible.com/article/react-a11y/)


### HTML component a11y reference

There are a surprising number of components or component elements that aren't very accessible even when you're dealing with pure HTML. This site breaks down how well a number of HTML elements do across a variety of devices and software. It can be particularly useful for identifying areas where some custom work will be needed to make something accessible. e.g. the USWDS file picker is a styled HTML file input meaning that it won't convey information on the selected file in most browsers/screen readers.

See also: [A11y Support](https://a11ysupport.io/) and [HTML5 Accessibility](https://www.html5accessibility.com) for higher level breakdowns of browser support for various HTML 5 elements
