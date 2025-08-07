Feature: Approved Data Analysts can upload data files
    # TANF Data Analyst Tim scenarios

    Scenario: A data analyst can submit a TANF Section 1 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a TANF Section '1' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the TANF Section '1' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the TANF Section '1' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a TANF Section 2 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a TANF Section '2' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the TANF Section '2' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the TANF Section '2' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a TANF Section 3 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a TANF Section '3' data file for year '2021' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the TANF Section '3' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the TANF Section '3' error report for year '2021' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    Scenario: A data analyst can submit a TANF Section 4 data file
        Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
        When 'tim-cypress@teamraft.com' uploads a TANF Section '4' data file for year '2022' and quarter 'Q1'
        Then 'tim-cypress@teamraft.com' sees the TANF Section '4' submission in Submission History
        And 'tim-cypress@teamraft.com' can download the TANF Section '4' error report for year '2022' and quarter 'Q1'
        # TODO: And Regional Randy gets an email (determine exact)

    # SSP Data Analyst Stefani scenarios

    # Scenario: A data analyst can submit an SSP Section 1 data file
    #     Given SSP Data Analyst Stefani logs in
    #     When SSP Data Analyst Stefani submits an SSP Section 1 data file
    #     Then SSP Data Analyst Stefani sees the Section 1 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And SSP Data Analyst Stefani can download the error report -> file match contents?
    #     # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)
    #
    # Scenario: A data analyst can submit an SSP Section 2 data file
    #     Given SSP Data Analyst Stefani logs in
    #     When SSP Data Analyst Stefani submits an SSP Section 2 data file
    #     Then SSP Data Analyst Stefani sees the Section 2 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And SSP Data Analyst Stefani can download the error report -> file match contents?
    #     # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)
    #
    # Scenario: A data analyst can submit an SSP Section 3 data file
    #     Given SSP Data Analyst Stefani logs in
    #     When SSP Data Analyst Stefani submits an SSP Section 3 data file
    #     Then SSP Data Analyst Stefani sees the Section 3 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And SSP Data Analyst Stefani can download the error report -> file match contents?
    #     # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)
    #
    # Scenario: A data analyst can submit an SSP Section 4 data file
    #     Given SSP Data Analyst Stefani logs in
    #     When SSP Data Analyst Stefani submits an SSP Section 4 data file
    #     Then SSP Data Analyst Stefani sees the Section 4 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And SSP Data Analyst Stefani can download the error report -> file match contents?
    #     # TODO: And Regional Randy (or Rebecca) gets an email (determine exact)
    #
    #   # Tribal Data Analyst Tara scenarios
    #
    # Scenario: A data analyst can submit a Tribal Section 1 data file
    #     Given Tribal Data Analyst Tara logs in
    #     When Tribal Data Analyst Tara submits a Tribal Section 1 data file
    #     Then Tribal Data Analyst Tara sees the Section 1 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And Tribal Data Analyst Tara can download the error report -> file match contents?
    #     # TODO: And Regional Randy gets an email (determine exact)
    #
    # Scenario: A data analyst can submit a Tribal Section 2 data file
    #     Given Tribal Data Analyst Tara logs in
    #     When Tribal Data Analyst Tara submits a Tribal Section 2 data file
    #     Then Tribal Data Analyst Tara sees the Section 2 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And Tribal Data Analyst Tara can download the error report -> file match contents?
    #     # TODO: And Regional Randy gets an email (determine exact)
    #
    # Scenario: A data analyst can submit a Tribal Section 3 data file
    #     Given Tribal Data Analyst Tara logs in
    #     When Tribal Data Analyst Tara submits a Tribal Section 3 data file
    #     Then Tribal Data Analyst Tara sees the Section 3 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And Tribal Data Analyst Tara can download the error report -> file match contents?
    #     # TODO: And Regional Randy gets an email (determine exact)
    #
    # Scenario: A data analyst can submit a Tribal Section 4 data file
    #     Given Tribal Data Analyst Tara logs in
    #     When Tribal Data Analyst Tara submits a Tribal Section 4 data file
    #     Then Tribal Data Analyst Tara sees the Section 4 submission in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And Tribal Data Analyst Tara can download the error report -> file match contents?
    #     # TODO: And Regional Randy gets an email (determine exact)
    #
    #     # Edge / failure cases for TANF Data Analyst Tim
    #
    # Scenario: a data analyst cannot submit a file for the wrong fiscal year and quarter
    #     Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
    #     When TANF Data Analyst Tim selects a file for the wrong year and quarter
    #     Then TANF Data Analyst Tim sees an error message -> should include error msg contents in impl.
    #
    # Scenario: a data analyst cannot submit a file for the wrong program type
    #     Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
    #     When TANF Data Analyst Tim selects an SSP data file
    #     Then TANF Data Analyst Tim sees an error message -> should include error msg contents in impl.
    #
    # Scenario: a data analyst cannot submit a file without a valid encoding
    #     Given 'Data Analyst', 'tim-cypress@teamraft.com', logs in
    #     When TANF Data Analyst Tim selects a wrongly encoded data file
    #     Then TANF Data Analyst Tim sees an error message -> should include error msg contents in impl.
    #
    # Scenario: a data analyst cannot submit a file for the wrong section
    #     Given Data Analyst Dillon logs in
    #     When Data Analyst Dillon selects a file for the wrong section
    #     Then Data Analyst Dillon sees the Rejected status in Submission History -> "Rejected" status should be displayed
    #
    #     Multi-file upload scenario for SSP Data Analyst Stefani
    #
    # Scenario: a data analyst can submit multiple files at once
    #     Given SSP Data Analyst Stefani logs in
    #     When SSP Data Analyst Stefani submits all TANF sections
    #     Then SSP Data Analyst Stefani sees all the files in Submission History -> implementation includes status, err report filename, original filename, etc
    #     And SSP Data Analyst Stefani can download each of the error reports -> file match contents?
    #     TODO: And Regional Randy (or Rebecca) gets an email for each section
