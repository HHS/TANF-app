Feature: Approved Data Analysts can upload data files
    
    @focus
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
        # We're only checking that non Data Analysts can submit a file
        # No need to test all programs and sections since they were tested above
        | DIGIT Diana           | TANF    | 1       |

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
