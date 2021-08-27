# 18. Tabletop Pull Request Meetings
Date: 2021-08-27

## Status

Accepted

## Context

Development team wanted greater throughput and knowledge transfer on the code review process.

## Decision

The purpose of these meetings is to get real-time feedback on the issue in question and have any technical discussion needed. This will facilitate knowledge transfer as the author explains their code and subsequent discussion, if needed.  Async review of the pull request is encouraged beforehand just as we have been doing and the meeting will serve as a gate keeper before the PR can transition from Raft Review to QASP review.

## Consequences

While this will require more scheduling and adds process, ultimately, we have seen greater knowledge transfer for each review and found issues that would have gone missed without this face-to-face feedback that discussions create.

## Q&A
### Who do I invite? 

As the author of the pull request, schedule a 15-minute meeting and invite the full dev team, including Alex. If there is a specific stakeholder not typically included, bring them in as well. We want to keep these meetings, small, focused, and technical. If someone of the dev team has a conflict or would prefer to stay focused on their current tasking, their attendance can be optional.

## When should I schedule them? 

At a minimum, I'd prefer to wait 2 business days after the PR has been opened to give the reviewers adequate async time to "do their homework". If there is a lot of activity in the PR or changes are needed, it is advised to delay that time table. These "tabletop" reviews should be scheduled when you feel the pull request is ready for the transition to QASP review OR if async Raft review has brought up either an important issue or a multitude you'd like to address in real-time. These are one-off ad hoc meetings so they should be scheduled as is convenient and while the code is fresh in everyone's minds. 

### What happens during these meetings?

The author will be the main presenter during the meeting and cover the issue context briefly, give a summary of the PR, and address any comments that have been made. After this, the floor will be opened for Q&A and potentially demo if author desires. Upon conclusion, if we have deemed it reasonable, we can switch to the QASP review label.


### How long are these?

While this does vary on the length and complexity of the pull request, I'd say this should take no longer than 15 minutes, typically. If we run over that time allotment, it might be best to do further work asynchronously; that being said, there's not a strict rule that should inhibit important and productive discussion of an issue. 


### Why are we doing these?

I'd like to promote knowledge sharing amongst the team broadly and we feel that this context and discussion could shorten the time needed for both Raft and QASP review.
