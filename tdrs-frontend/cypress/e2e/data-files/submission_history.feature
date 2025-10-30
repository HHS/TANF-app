Feature: Data file submission history
    Scenario: Admin Alex can view TANF submissions
        Given 'Admin Alex' logs in
        Then Admin Alex can view the Illinois TANF Submission History
        And Admin Alex can verify the Illinois TANF submission
    Scenario: Admin Alex can view SSP submissions
        Given 'Admin Alex' logs in
        Then Admin Alex can view the Missouri SSP Submission History
        And Admin Alex can verify the Missouri SSP submission
    Scenario: Admin Alex can view FRA submissions
        Given 'Admin Alex' logs in
        Then Admin Alex can view the Arizona FRA Submission History
        And Admin Alex can verify the Arizona FRA submission
    Scenario: Regional Randy only has view access to submission historys for assigned locations
        Given FRA Data Analyst Fred submits a file
        Then 'Regional Randy' logs in
        When Regional Randy searches TANF Data Files
        Then Regional Randy has read-only access to submission history
