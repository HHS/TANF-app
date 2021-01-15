# Evaluating accessibility

The [QASP](https://github.com/18F/tdrs-app-rfq/blob/main/Final-RFQ/FINAL-TDRS-software-development-RFQ.md) for this project includes the following accessibility standards and method of assessment:

| **Deliverable 4**        | **Accessible**                                                                                                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Performance Standard(s)  | Web Content Accessibility Guidelines 2.1 AA standards                                                                                                                                                               |
| Acceptable Quality Level | 0 errors reported using an automated scanner and 0 errors reported in manual testing                                                                                                                                |
| Method of Assessment     | Combined approach using automated and manual testing with tools equivalent to [Accessibility Insights](https://accessibilityinsights.io/) and/or the [DHS Trusted Tester process](https://www.dhs.gov/508-testing). |
| Due Date                 | Every sprint                                                                                                                                                                                                        |

## How does government plan to carry out the Method of Assessment?

Our web testing tool will be [Accessibility Insights](https://accessibilityinsights.io/).

Accessibility Insights includes both a [Fast Pass](https://accessibilityinsights.io/docs/en/web/getstarted/fastpass/) tool and a comprehensive [Assessment](https://accessibilityinsights.io/docs/en/web/getstarted/assessment/) tool.

We will check new pages, features, and interactions added during the course of each sprint using:

- Accessibility Insights Fast Pass tool
- Accessibility Insights Assessment tool
- Manual screen reader testing using one or more of the following combinations:
  - JAWS on Windows
  - VoiceOver on Safari, Mac OS
  - VoiceOver on iOS

We won't re-rest pages or elements that have previously been tested and haven't changed since, such as header or footer elements.

We will invite in ACF's 508 Coordinator to review the accessibility of the site at strategic points in the process.

The ultimate goal of this evaluation plan is to ensure that the site is accessible to its users, meets WCAG 2.1 AA standards as per contract, and meets Section 508 legal requirements.

If we find that this evaluation plan isn't helping us meet those goals, we may adjust the plan after consulting with subject matter experts and the development team.
