Feature: Admin Feedback Reports
    Background:
        Given 'DIGIT Diana' logs in

    # Happy path tests

    Scenario: DIGIT Team member can navigate to the Feedback Reports page
        When 'DIGIT Diana' navigates to Feedback Reports
        Then 'DIGIT Diana' sees the Feedback Reports page with fiscal year selector
        And no upload form is visible

    Scenario: DIGIT Team member sees upload form after selecting fiscal year
        When 'DIGIT Diana' navigates to Feedback Reports
        And 'DIGIT Diana' selects fiscal year '2025'
        Then 'DIGIT Diana' sees the upload form for fiscal year '2025'
        And 'DIGIT Diana' sees the upload history section

    Scenario: DIGIT Team member can upload a valid feedback report
        When 'DIGIT Diana' navigates to Feedback Reports
        And 'DIGIT Diana' selects fiscal year '2025'
        And 'DIGIT Diana' uploads 'FY2025_valid_single_stt.zip' with date '01/15/2025'
        Then 'DIGIT Diana' sees the upload success message
        And the upload appears in the history table
        And the report is processed successfully

    # Validation error tests

    Scenario: Error when submitting without a file
        When 'DIGIT Diana' navigates to Feedback Reports
        And 'DIGIT Diana' selects fiscal year '2025'
        And 'DIGIT Diana' enters date '01/15/2025' but no file
        And 'DIGIT Diana' clicks upload
        Then 'DIGIT Diana' sees the error 'No file selected.'

    Scenario: Error when selecting a non-ZIP file
        When 'DIGIT Diana' navigates to Feedback Reports
        And 'DIGIT Diana' selects fiscal year '2025'
        And 'DIGIT Diana' selects a non-ZIP file
        Then 'DIGIT Diana' sees the error 'Invalid file. Make sure to select a zip file.'

    Scenario: Error when ZIP fiscal year does not match
        When 'DIGIT Diana' navigates to Feedback Reports
        And 'DIGIT Diana' selects fiscal year '2024'
        And 'DIGIT Diana' selects 'FY2025_valid_single_stt.zip'
        Then 'DIGIT Diana' sees the error about fiscal year mismatch

    Scenario: Error when submitting without a date
        When 'DIGIT Diana' navigates to Feedback Reports
        And 'DIGIT Diana' selects fiscal year '2025'
        And 'DIGIT Diana' selects 'FY2025_valid_single_stt.zip' but no date
        And 'DIGIT Diana' clicks upload
        Then 'DIGIT Diana' sees the error about missing date

    # Permission tests - users who SHOULD have access

    Scenario: OFA System Admin can access admin feedback reports
        Given 'Admin Alex' logs in
        When 'Admin Alex' navigates to Feedback Reports
        And 'Admin Alex' selects fiscal year '2025'
        Then 'Admin Alex' sees the upload form for fiscal year '2025'

