Feature: Data file submission history
    Scenario: A user can upload a file
        Given The admin logs in
            And A file exists in submission history
        When 'cypress-regional-staff@teamraft.com' visits the home page
            And 'cypress-regional-staff@teamraft.com' logs in
        Then 'cypress-regional-staff@teamraft.com' can see Data Files page
            And 'cypress-regional-staff@teamraft.com' can see search form
        When 'cypress-regional-staff@teamraft.com' selects an STT
            And 'cypress-regional-staff@teamraft.com' submits the search form
        Then 'cypress-regional-staff@teamraft.com' can see submission history
            And 'cypress-regional-staff@teamraft.com' cannot see the upload form
            And 'cypress-regional-staff@teamraft.com' sees the file in submission history
    Scenario: Admin Alex can view TANF submissions
        Given Admin Alex logs in
        Then Admin Alex can view the Illinois TANF Submission History
        And Admin Alex can verify the Illinois TANF submission
    Scenario: Admin Alex can view SSP submissions
        Given Admin Alex logs in
        Then Admin Alex can view the Missouri SSP Submission History
        And Admin Alex can verify the Missouri SSP submission
    Scenario: Admin Alex can view FRA submissions
        Given Admin Alex logs in
        Then Admin Alex can view the Arizona FRA Submission History
        And Admin Alex can verify the Arizona FRA submission
    Scenario: Regional Randy only has view access to submission historys for assigned locations
        Given Regional Randy logs in
        When Regional Randy searches FRA Data Files
        Then Regional Randy has read-only access to submission history
