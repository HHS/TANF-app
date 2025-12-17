Feature: User Profile Editing
    As a user of the TDP system
    I want to edit my profile information
    So that my account details are accurate and up-to-date

    # TODO: Change Request Approval Workflow

    # ============================================================================
    # Cancel Editing
    # ============================================================================
    Scenario: Data Analyst Dana cancels editing in Access Request state
        Given 'Data Analyst Dana' logs in
        When 'Data Analyst Dana' cancels profile editing with unsaved changes
        Then 'Data Analyst Dana' profile shows name 'Data Analyst Dana'

    Scenario: Data Analyst Donna cancels editing in Approved state
        Given 'Data Analyst Donna' logs in
        When 'Data Analyst Donna' cancels profile editing with unsaved changes
        Then 'Data Analyst Donna' profile shows name 'Data Analyst Donna'

    # ============================================================================
    # STT Changes
    # ============================================================================
    Scenario: Data Analyst Dana changes STT in Access Request state
        Given 'Data Analyst Dana' logs in
        When 'Data Analyst Dana' updates their STT to 'Alabama'
        Then 'Data Analyst Dana' profile shows STT 'Alabama'

    Scenario: Data Analyst Donna cannot change STT in Approved state
        Given 'Data Analyst Donna' logs in
        When 'Data Analyst Donna' opens profile editing
        Then the STT field is not editable

    # ============================================================================
    # Region Changes (Regional Staff)
    # ============================================================================
    Scenario: FRA OFA Regional Staff Rachel changes regions in Access Request state
        Given 'FRA OFA Regional Staff Rachel' logs in
        When 'FRA OFA Regional Staff Rachel' updates their regions to add 'Seattle' and remove 'Chicago'
        Then 'FRA OFA Regional Staff Rachel' profile shows regions 'Seattle, Philadelphia'

    Scenario: FRA OFA Regional Staff Robert changes regions in Approved state
        Given 'FRA OFA Regional Staff Robert' logs in
        When 'FRA OFA Regional Staff Robert' updates their regions to add 'Seattle' and remove 'Chicago'
        Then 'FRA OFA Regional Staff Robert' sees a pending change request
        And 'FRA OFA Regional Staff Robert' profile shows regions 'Chicago, Philadelphia'

    # ============================================================================
    # Validation and Error Handling
    # ============================================================================
    Scenario: Data Analyst Dana attempts to save with empty first name
        Given 'Data Analyst Dana' logs in
        When 'Data Analyst Dana' submits profile with empty first name
        Then 'Data Analyst Dana' sees a required field error
        And 'Data Analyst Dana' remains on the edit page

    Scenario: Data Analyst Dana attempts to save with empty last name
        Given 'Data Analyst Dana' logs in
        When 'Data Analyst Dana' submits profile with empty last name
        Then 'Data Analyst Dana' sees a required field error
        And 'Data Analyst Dana' remains on the edit page

    Scenario: Data Analyst Donna attempts to save without making changes
        Given 'Data Analyst Donna' logs in
        When 'Data Analyst Donna' submits profile without changes
        Then 'Data Analyst Donna' sees a no changes error
        And 'Data Analyst Donna' remains on the edit page

    # Warning: These tests need to always run last since they modify state that isn't cleaned between scenarios
    # ============================================================================
    # Access Request State - Immediate Updates
    # ============================================================================
    Scenario: Data Analyst Dana edits profile in Access Request state
        Given 'Data Analyst Dana' logs in
        When 'Data Analyst Dana' updates their name to 'Data Analyst Updated' 'Dana Updated'
        Then 'Data Analyst Dana' profile shows name 'Data Analyst Updated Dana Updated'

    Scenario: FRA Data Analyst Derek edits profile and disables FRA access in Access Request state
        Given 'FRA Data Analyst Derek' logs in
        When 'FRA Data Analyst Derek' updates their name to 'FRA Data Analyst Updated' and disables FRA access
        Then 'FRA Data Analyst Derek' profile shows name 'FRA Data Analyst Updated'
        And 'FRA Data Analyst Derek' profile does not show FRA access

    Scenario: FRA OFA Regional Staff Rachel edits profile in Access Request state
        Given 'FRA OFA Regional Staff Rachel' logs in
        When 'FRA OFA Regional Staff Rachel' updates their name to 'FRA Regional Updated' 'Rachel Updated'
        Then 'FRA OFA Regional Staff Rachel' profile shows name 'FRA Regional Updated'

    # ============================================================================
    # Approved State - Change Requests
    # ============================================================================
    Scenario: Data Analyst Donna edits profile in Approved state
        Given 'Data Analyst Donna' logs in
        When 'Data Analyst Donna' updates their name to 'Data Analyst Changed' 'Donna Changed'
        Then 'Data Analyst Donna' sees a pending change request
        And 'Data Analyst Donna' profile shows name 'Data Analyst Donna'

    Scenario: FRA Data Analyst David edits profile and disables FRA access in Approved state
        Given 'FRA Data Analyst David' logs in
        When 'FRA Data Analyst David' updates their name to 'FRA Data Analyst Changed' and disables FRA access
        Then 'FRA Data Analyst David' sees a pending change request
        And 'FRA Data Analyst David' profile shows name 'FRA Data Analyst David'

    Scenario: FRA OFA Regional Staff Robert edits profile in Approved state
        Given 'FRA OFA Regional Staff Robert' logs in
        When 'FRA OFA Regional Staff Robert' updates their name to 'FRA Regional Changed' 'Robert Changed'
        Then 'FRA OFA Regional Staff Robert' sees a pending change request
        And 'FRA OFA Regional Staff Robert' profile shows name 'FRA OFA Regional Staff Robert'

    # TODO: verify change requests exist in DB?
