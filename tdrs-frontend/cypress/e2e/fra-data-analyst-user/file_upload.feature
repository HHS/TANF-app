Feature: FRA Data Analysts can upload data files
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
