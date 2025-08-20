Feature: Data file submission
    Scenario: Admin Alex can submit TANF reports
        Given Admin Alex logs in
        When Admin Alex submits the TANF Report
        Then Admin Alex sees the upload in TANF Submission History
        And Admin Alex can download the TANF error report
    Scenario: Admin Alex can submit SSP reports
        Given Admin Alex logs in
        When Admin Alex submits the SSP Report
        Then Admin Alex sees the upload in SSP Submission History
        And Admin Alex can download the SSP error report
    Scenario: Admin Alex can submit FRA reports
        Given Admin Alex logs in
        When Admin Alex submits the Work Outcomes Report
        Then Admin Alex sees the upload in FRA Submission History
        And Admin Alex can download the FRA error report
    Scenario: A FRA data analyst can submit a Work Outcomes of TANF Exiters data file
        Given FRA Data Analyst Fred logs in
        When FRA Data Analyst Fred submits the Work Outcomes Report
        Then FRA Data Analyst Fred sees the upload in Submission History
        And FRA Data Analyst Fred can download the FRA error report
        # And Regional Randy gets an email (determine exact)
    Scenario: A FRA data analyst sees incorrect file type error
        Given FRA Data Analyst Fred logs in
        When FRA Data Analyst Fred uploads incorrect file type
        Then FRA Data Analyst Fred sees the incorrect file type error
    Scenario: A FRA data analyst can submit a TANF data file
        Given FRA Data Analyst Fred logs in
        When FRA Data Analyst Fred submits the TANF Report
        Then FRA Data Analyst Fred sees the upload in TANF Submission History
        And FRA Data Analyst Fred can download the TANF error report
        # And Regional Randy gets an email (determine exact)
    Scenario: A FRA data analyst can submit a SSP data file
        Given FRA Data Analyst Fred logs in
        When FRA Data Analyst Fred submits the SSP Report
        Then FRA Data Analyst Fred sees the upload in SSP Submission History
        And FRA Data Analyst Fred can download the SSP error report
        # And Regional Randy gets an email (determine exact)

    Scenario Outline: <actor> can submit a <program> Section <section> data file
        Given '<actor>' logs in
        When '<actor>' uploads a '<program>' Section '<section>' data file
        Then '<actor>' sees the '<program>' Section '<section>' submission in Submission History
        And '<actor>' can download the '<program>' Section '<section>' error report
        # TODO: And Regional Randy gets an email (determine exact)

    Examples:
        | actor                 | program | section |
        | Data Analyst Tim      | TANF    | 1       |
        | Data Analyst Tim      | TANF    | 2       |
        | Data Analyst Tim      | TANF    | 3       |
        | Data Analyst Tim      | TANF    | 4       |
        | Data Analyst Stefani  | SSP     | 1       |
        | Data Analyst Stefani  | SSP     | 2       |
        | Data Analyst Stefani  | SSP     | 3       |
        | Data Analyst Stefani  | SSP     | 4       |
        | Data Analyst Tara     | TRIBAL  | 1       |
        | Data Analyst Tara     | TRIBAL  | 2       |
        | Data Analyst Tara     | TRIBAL  | 3       |

    # Edge / failure cases for TANF Data Analyst Tim

    Scenario: Data Analyst Tim cannot submit a file for the wrong fiscal year and quarter
        Given 'Data Analyst Tim' logs in
        When Data Analyst Tim selects a TANF data file for the wrong year
        Then 'Data Analyst Tim' sees the error message: 'File contains data from Oct 1 - Dec 31, which belongs to Fiscal Year 2021, Quarter 1.'

    Scenario: Data Analyst Tim cannot submit a file for the wrong program type
        Given 'Data Analyst Tim' logs in
        When Data Analyst Tim selects an SSP data file for the year 2025 and quarter Q1
        Then 'Data Analyst Tim' sees the error message: 'File may correspond to SSP instead of TANF'

    Scenario: Data Analyst Tim cannot submit a file for the wrong section
        Given 'Data Analyst Tim' logs in
        When 'Data Analyst Tim' selects a data file for the wrong section
        Then 'Data Analyst Tim' sees rejected status in submission history
