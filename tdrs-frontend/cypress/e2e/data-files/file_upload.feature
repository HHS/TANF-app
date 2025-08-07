Feature: Approved Data Analysts can upload data files
    # TANF Data Analyst Tim scenarios

    Scenario: A data analyst can submit a TANF Section 1 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a TANF Section '1' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the TANF Section '1' submission in Submission History
        Then 'tim-cypress@teamraft.com' can download the TANF Section '1' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)
