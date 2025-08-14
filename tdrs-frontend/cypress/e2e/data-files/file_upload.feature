Feature: Approved Data Analysts can upload data files
    
    Scenario Outline: A data analyst can submit a data file
        Given '<role>', '<username>', logs in
        When '<username>' uploads a '<program>' Section '<section>' data file for year '<year>' and quarter '<quarter>'
        Then '<username>' sees the '<program>' Section '<section>' submission in Submission History
        And '<username>' can download the '<program>' Section '<section>' error report for year '<year>' and quarter '<quarter>'
        # TODO: And Regional Randy gets an email (determine exact)

    Examples:
        | role         | username                     | program | section | year | quarter |
        | Data Analyst | tim-cypress@teamraft.com     | TANF    | 1       | 2021 | Q1      |
        | Data Analyst | tim-cypress@teamraft.com     | TANF    | 2       | 2021 | Q1      |
        | Data Analyst | tim-cypress@teamraft.com     | TANF    | 3       | 2021 | Q1      |
        | Data Analyst | tim-cypress@teamraft.com     | TANF    | 4       | 2022 | Q1      |
        | Data Analyst | stefani-cypress@teamraft.com | SSP     | 1       | 2024 | Q1      |
        | Data Analyst | stefani-cypress@teamraft.com | SSP     | 2       | 2024 | Q1      |
        | Data Analyst | stefani-cypress@teamraft.com | SSP     | 3       | 2024 | Q1      |
        | Data Analyst | stefani-cypress@teamraft.com | SSP     | 4       | 2024 | Q1      |
        | Data Analyst | tara-cypress@teamraft.com    | TRIBAL  | 1       | 2021 | Q1      |
        | Data Analyst | tara-cypress@teamraft.com    | TRIBAL  | 2       | 2021 | Q1      |
        | Data Analyst | tara-cypress@teamraft.com    | TRIBAL  | 3       | 2021 | Q1      |

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
