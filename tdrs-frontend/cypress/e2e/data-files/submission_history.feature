Feature: Approved Regional Staff can view submission history
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