Feature: Admin Feedback Reports
    Background:
        Given 'DIGIT Diana' logs in

    # Happy path tests

    Scenario: DIGIT Team member can navigate to the Feedback Reports page
        When the user navigates to Feedback Reports
        Then the user sees the Feedback Reports page with fiscal year selector
        And no upload form is visible

    Scenario: DIGIT Team member sees upload form after selecting fiscal year
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        Then the user sees the upload form for fiscal year '2025'
        And the user sees the upload history section

    Scenario: DIGIT Team member can upload a valid feedback report
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        And the user uploads 'FY2025_valid_single_stt.zip' with date '01/15/2025'
        Then the user sees the upload success message
        And the upload appears in the history table
        And the report is processed successfully

    # Validation error tests

    Scenario: Error when submitting without a file
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        And the user enters date '01/15/2025' but no file
        And the user clicks upload
        Then the user sees the error 'No file selected.'

    Scenario: Error when selecting a non-ZIP file
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        And the user selects a non-ZIP file
        Then the user sees the error 'Invalid file. Make sure to select a zip file.'

    Scenario: Error when ZIP fiscal year does not match
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2024'
        And the user selects 'FY2025_valid_single_stt.zip'
        Then the user sees the error about fiscal year mismatch

    Scenario: Error when submitting without a date
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        And the user selects 'FY2025_valid_single_stt.zip' but no date
        And the user clicks upload
        Then the user sees the error about missing date

    # Upload history and state management tests

    Scenario: Upload history filters by fiscal year
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        And the user uploads 'FY2025_valid_single_stt.zip' with date '01/15/2025'
        Then the user sees the upload success message
        When the user selects fiscal year '2024'
        Then the user sees no upload history for this year
        When the user selects fiscal year '2025'
        Then the upload appears in the history table

    Scenario: Form resets when fiscal year changes
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        And the user selects a file and enters a date
        And the user changes the fiscal year
        Then the form is reset

    # Permission tests - users who SHOULD have access

    Scenario: OFA System Admin can access admin feedback reports
        Given 'Admin Alex' logs in
        When the user navigates to Feedback Reports
        And the user selects fiscal year '2025'
        Then the user sees the upload form for fiscal year '2025'

    # Permission tests - users who should NOT have access

Scenario: OFA Regional Staff cannot see Feedback Reports nav item
        Given 'Regional Staff Cypress' logs in
        Then the user does not see Feedback Reports in the navigation
