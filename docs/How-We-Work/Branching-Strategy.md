## Dev Workflow and Branching Strategy

Moving forward, the dev team will be shifting our branching strategy to help alleviate some of our dependency issues. It won't solve the problem completely, but it should make the working environment considerably easier to manage for all of us.

### Part I

Frontend and backend work will start working on separate issues
* This is a major source of our issues as the frontend frequently has to pull in backend code to build the frontend off of. However, the frontend has the option of creating mock data so it isn't initially dependent on the backend. So, if the backend is working on one issue while the frontend works on a completely different issue, both can move forward without holding each other up.
* Once either the frontend or backend finishes an issue we will check to see if the other end has an issue finished. If so, that will be the issue the developer works on next, so we can still push through working full stack code at a good pace.
* Once the frontend and backend of an issue have both been completed we will pair to remove the frontend mocks and tie it to the backend. They will go in together as a PR.
* OFA and 18F will be kept up to date on progress through stand-up and frequent informal reviews.

### Part II

All work for an issue will be done on an issue branch, branched from `raft-tdp-main`
* When work on an issue is started a main issue branch will be created, which both the frontend and backend will branch from.
* Once tasks are completed they will go into Raft review and won't be merged back into the main issue branch until they pass raft review.
* Epics will work the same way, except it will work from a main Epic branch.
* If the issue is part of an Epic, after passing Raft review it will be merged into the main Epic branch and a PR will be created in HHS.
* If the issue is not part of an epic, a PR will be created into HHS only after the entire issue has passed Raft review. 

### Part III
For review purposes, we have also created the protected branch `raft-review`. We will issue Pull Requests to this branch once a working branch is ready for review. Merging to `raft-review` will kick off our automated deployment to our test environment. Approvals are required to merge to `raft-review` but code is not reviewed at this stage as we are deploying for testing purposes. It is required that all CI/CD checks are green before a merge will be accepted.

### Part IV
**Merging to HHS**
Once a branch has is in review we will place it in `Raft Review` status in the Raft repository, where we will perform code reviews and check against the QASP checklist. After passing this phase, the `Raft Review` label will be removed and the `QASP Review` label will be added. Once it passes `QASP Review` it will be merged to `raft-tdp-main` and a PR will be issued from `raft-tech:raft-tdp-main` to `HHS:main`. As it has already gone through approval, assuming the automated
deploy works correctly, it can be merged immediately.

Once all of these reviews are passing and approved, the Product Owner or Government Tech Lead will merge the branch into the `main` branch in the HHS repository.
