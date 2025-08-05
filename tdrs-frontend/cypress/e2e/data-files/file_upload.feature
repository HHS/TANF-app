Feature: Approved Data Analysts can upload data files
    # TANF Data Analyst Tim scenarios

    Scenario: A data analyst can submit a TANF Section 1 data file
        Given The admin logs in
        And 'tim-cypress@teamraft.com' is in approved state
        When 'tim-cypress@teamraft.com' visits the home page
        And 'tim-cypress@teamraft.com' logs in
        Then 'tim-cypress@teamraft.com' can see Data Files page
        Then 'tim-cypress@teamraft.com' can see search form
        Then 'tim-cypress@teamraft.com' submits the search form for year '2021' and quarter 'Q1'
        When 'tim-cypress@teamraft.com' uploads a TANF Section 1 data file
        Then 'tim-cypress@teamraft.com' can see the upload successful
        Then 'tim-cypress@teamraft.com' sees the TANF Section '1' submission in Submission History
        # TODO: And Regional Randy gets an email (determine exact)
