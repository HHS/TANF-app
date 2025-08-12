Feature: Approved Data Analysts can upload data files
    # TANF Data Analyst Tim scenarios

    Scenario: A data analyst can submit a TANF Section 1 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a 'TANF' Section '1' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the 'TANF' Section '1' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the 'TANF' Section '1' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a TANF Section 2 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a 'TANF' Section '2' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the 'TANF' Section '2' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the 'TANF' Section '2' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a TANF Section 3 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a 'TANF' Section '3' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the 'TANF' Section '3' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the 'TANF' Section '3' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a TANF Section 4 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a 'TANF' Section '4' data file for year '2022' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the 'TANF' Section '4' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the 'TANF' Section '4' error report for year '2022' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    # SSP Data Analyst Stefani scenarios

    Scenario: A data analyst can submit an SSP Section 1 data file
        Given 'Data Analyst', 'stefani-cypress@teamraft.com', logs in
        When 'stafani-cypress@teamraft.com' uploads a 'SSP' Section '1' data file for year '2024' and quarter 'Q1'
        Then 'stafani-cypress@teamraft.com' sees the 'SSP' Section '1' submission in Submission History
        And 'stafani-cypress@teamraft.com' can download the 'SSP' Section '1' error report for year '2024' and quarter 'Q1'
        # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)

    Scenario: A data analyst can submit an SSP Section 2 data file
        Given 'Data Analyst', 'stefani-cypress@teamraft.com', logs in
        When 'stafani-cypress@teamraft.com' uploads a 'SSP' Section '2' data file for year '2024' and quarter 'Q1'
        Then 'stafani-cypress@teamraft.com' sees the 'SSP' Section '2' submission in Submission History
        And 'stafani-cypress@teamraft.com' can download the 'SSP' Section '2' error report for year '2024' and quarter 'Q1'
        # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)

    Scenario: A data analyst can submit an SSP Section 3 data file
        Given 'Data Analyst', 'stefani-cypress@teamraft.com', logs in
        When 'stafani-cypress@teamraft.com' uploads a 'SSP' Section '3' data file for year '2024' and quarter 'Q1'
        Then 'stafani-cypress@teamraft.com' sees the 'SSP' Section '3' submission in Submission History
        And 'stafani-cypress@teamraft.com' can download the 'SSP' Section '3' error report for year '2024' and quarter 'Q1'
        # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)

    Scenario: A data analyst can submit an SSP Section 4 data file
        Given 'Data Analyst', 'stefani-cypress@teamraft.com', logs in
        When 'stafani-cypress@teamraft.com' uploads a 'SSP' Section '4' data file for year '2024' and quarter 'Q1'
        Then 'stafani-cypress@teamraft.com' sees the 'SSP' Section '4' submission in Submission History
        And 'stafani-cypress@teamraft.com' can download the 'SSP' Section '4' error report for year '2024' and quarter 'Q1'
        # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)

    # Tribal Data Analyst Tara scenarios

    Scenario: A data analyst can submit a Tribal Section 1 data file
        Given 'Data Analyst', 'tara-cypress@teamraft.com', logs in
        When 'tara-cypress@teamraft.com' uploads a 'TRIBAL' Section '1' data file for year '2021' and quarter 'Q1'
        Then 'tara-cypress@teamraft.com' sees the 'TRIBAL' Section '1' submission in Submission History
        And 'tara-cypress@teamraft.com' can download the 'TRIBAL' Section '1' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a Tribal Section 2 data file
        Given 'Data Analyst', 'tara-cypress@teamraft.com', logs in
        When 'tara-cypress@teamraft.com' uploads a 'TRIBAL' Section '2' data file for year '2021' and quarter 'Q1'
        Then 'tara-cypress@teamraft.com' sees the 'TRIBAL' Section '2' submission in Submission History
        And 'tara-cypress@teamraft.com' can download the 'TRIBAL' Section '2' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a Tribal Section 3 data file
        Given 'Data Analyst', 'tara-cypress@teamraft.com', logs in
        When 'tara-cypress@teamraft.com' uploads a 'TRIBAL' Section '3' data file for year '2021' and quarter 'Q1'
        Then 'tara-cypress@teamraft.com' sees the 'TRIBAL' Section '3' submission in Submission History
        And 'tara-cypress@teamraft.com' can download the 'TRIBAL' Section '3' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    # Edge / failure cases for TANF Data Analyst Tim

    Scenario: a data analyst cannot submit a file for the wrong fiscal year and quarter
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' selects a 'TANF' data file for the year '2025' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the error message: 'File contains data from Oct 1 - Dec 31, which belongs to Fiscal Year 2021, Quarter 1.'

    Scenario: a data analyst cannot submit a file for the wrong program type
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' selects a 'SSP' data file for the year '2025' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the error message: 'File may correspond to SSP instead of TANF'

    Scenario: a data analyst cannot submit a file for the wrong section
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' selects a data file for the wrong section
        Then 'tim-cypress@teamraft.com' sees rejected status in submission history
