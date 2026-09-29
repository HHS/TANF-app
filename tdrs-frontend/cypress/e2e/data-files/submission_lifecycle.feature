Feature: Submission lifecycle through the user interface
    A data analyst should be able to submit a real file and follow its
    processing result without the test reading or changing backend state.

    Scenario: A data analyst submits a file that is accepted
        Given 'Data Analyst Tim' logs in
        When Data Analyst Tim submits a valid TANF aggregate file through the UI
        Then Data Analyst Tim sees the TANF aggregate submission finish as Accepted

    Scenario: A data analyst submits a file that is accepted with errors
        Given 'Data Analyst Stefani' logs in
        When Data Analyst Stefani submits an SSP active case file through the UI
        Then Data Analyst Stefani sees the SSP submission finish as Accepted with Errors

    Scenario: A FRA data analyst submits a file that is partially accepted
        Given 'FRA Data Analyst Fred' logs in
        When FRA Data Analyst Fred submits an FRA file through the UI
        Then FRA Data Analyst Fred sees the FRA submission finish as Partially Accepted with Errors

    Scenario: A data analyst submits a file that is rejected
        Given 'Data Analyst Tim' logs in
        When Data Analyst Tim submits an invalid TANF active case file through the UI
        Then Data Analyst Tim sees the TANF active case submission finish as Rejected

    @local-admin-reparse
    Scenario: An administrator reparses a completed submission
        Given 'Data Analyst Tim' logs in
        When Data Analyst Tim submits a TANF aggregate file for administrator reprocessing
        Then Data Analyst Tim sees the reprocessing candidate finish as Accepted
        And 'Admin Alex' logs in
        When Admin Alex reparses the completed submission in the admin UI
        Then Admin Alex eventually sees the reparse finish in the admin UI
        And 'Data Analyst Tim' logs in
        Then Data Analyst Tim sees the submission marked as Reprocessed and Accepted

    Scenario: A data analyst submits a file that fails security inspection
        Given 'FRA Data Analyst Fred' logs in
        When FRA Data Analyst Fred submits an infected file through the UI
        Then FRA Data Analyst Fred sees that the submission failed security inspection

    @local-stuck-timeout
    Scenario: A slow submission becomes stuck and is visible to an administrator
        Given 'Data Analyst Tim' logs in
        When Data Analyst Tim submits a long-running TANF file through the UI
        And 'Admin Alex' logs in
        Then Admin Alex eventually sees the submission in Stuck state in the admin UI
