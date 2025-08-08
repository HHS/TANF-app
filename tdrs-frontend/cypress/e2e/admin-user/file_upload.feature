Feature: OFA System Admin users can manage data files
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
