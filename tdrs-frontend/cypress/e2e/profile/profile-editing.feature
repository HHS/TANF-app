Feature: User Profile Editing As a user of the TDP system I want to edit my profile information So that my account details are accurate and up-to-date

  # # ============================================================================
  # # Change Request Approval Workflow
  # # ============================================================================

  # TODO:

  # # ============================================================================
  # # Cancel Editing
  # # ============================================================================
  Scenario: Data Analyst Dana cancels editing
    Given "Data Analyst Dana" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they update their first name to "Should Not Save"
    And they click cancel
    Then they should be back on the profile view page
    And their profile should show name as "Data Analyst Dana"

  Scenario: Data Analyst Donna cancels editing in Approved state
    Given "Data Analyst Donna" logs in
    When they navigate to their profile page
    And they click the edit profile button
    And they update their first name to "Should Not Save"
    And they click cancel
    Then they should be back on the profile view page
    And their profile should show name as "Data Analyst Donna"

  # # ============================================================================
  # # STT Changes
  # # ============================================================================
  Scenario: Data Analyst Dana changes STT in Access Request state
    Given "Data Analyst Dana" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they select STT "Alabama"
    And they click update request
    And their profile should show State STT "Alabama"

  Scenario: Data Analyst Donna cannot change STT in Approved state
    Given "Data Analyst Donna" logs in
    When they navigate to their profile page
    And they click the edit profile button
    Then the STT field should not be editable

  # # ============================================================================
  # # Region Changes (Regional Staff)
  # # ============================================================================
  Scenario: FRA OFA Regional Staff Rachel changes regions in Access Request state
    Given "FRA OFA Regional Staff Rachel" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they deselect region "Chicago"
    And they select region "Seattle"
    And they click update request
    And their profile should show regions "Seattle, Philadelphia"

  Scenario: FRA OFA Regional Staff Robert changes regions in Approved state
    Given "FRA OFA Regional Staff Robert" logs in
    When they navigate to their profile page
    And they click the edit profile button
    And they deselect region "Chicago"
    And they select region "Seattle"
    And they click save
    And they should see a pending change request banner
    And their profile should show regions "Chicago, Philadelphia"

  # # ============================================================================
  # # Validation and Error Handling
  # # ============================================================================
  Scenario: Data Analyst Dana attempts to save with empty first name
    Given "Data Analyst Dana" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they clear the first name field
    And they click update request
    Then they should see an error message about required fields
    And they should still be on the edit page

  Scenario: Data Analyst Dana attempts to save with empty last name
    Given "Data Analyst Dana" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they clear the last name field
    And they click update request
    Then they should see an error message about required fields
    And they should still be on the edit page

  Scenario: Data Analyst Donna attempts to save without making changes
    Given "Data Analyst Donna" logs in
    When they navigate to their profile page
    And they click the edit profile button
    And they click save without making changes
    Then they should see an error message about no changes made
    And they should still be on the edit page

  # Warning: These tests need to always run last since they modify state that isn't cleaned between scenarios
  # ============================================================================
  # Access Request State - Immediate Updates
  # ============================================================================
  Scenario: Data Analyst Dana edits profile in Access Request state
    Given "Data Analyst Dana" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they update their first name to "Data Analyst Updated"
    And they update their last name to "Dana Updated"
    And they click update request
    And their profile should show name as "Data Analyst Updated Dana Updated"

  Scenario: FRA Data Analyst Derek edits profile and toggles FRA access in Access Request state
    Given "FRA Data Analyst Derek" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they update their first name to "FRA Data Analyst Updated"
    And they toggle FRA access off
    And they click update request
    And their profile should show name as "FRA Data Analyst Updated"
    And their profile should not show FRA access badge

  Scenario: FRA OFA Regional Staff Rachel edits profile in Access Request state
    Given "FRA OFA Regional Staff Rachel" logs in
    When they navigate to their profile page
    And they click the edit access request button
    And they update their first name to "FRA Regional Updated"
    And they update their last name to "Rachel Updated"
    And they click update request
    And their profile should show name as "FRA Regional Updated"

  # # ============================================================================
  # # Approved State - Change Requests
  # # ============================================================================
  Scenario: Data Analyst Donna edits profile in Approved state
    Given "Data Analyst Donna" logs in
    When they navigate to their profile page
    And they click the edit profile button
    And they update their first name to "Data Analyst Changed"
    And they update their last name to "Donna Changed"
    And they click save
    And they should see a pending change request banner
    And their profile should show name as "Data Analyst Donna"

  Scenario: FRA Data Analyst David edits profile and toggles FRA access in Approved state
    Given "FRA Data Analyst David" logs in
    When they navigate to their profile page
    And they click the edit profile button
    And they update their first name to "FRA Data Analyst Changed"
    And they toggle FRA access off
    And they click save
    And they should see a pending change request banner
    And their profile should show name as "FRA Data Analyst David"

  Scenario: FRA OFA Regional Staff Robert edits profile in Approved state
    Given "FRA OFA Regional Staff Robert" logs in
    When they navigate to their profile page
    And they click the edit profile button
    And they update their first name to "FRA Regional Changed"
    And they update their last name to "Robert Changed"
    And they click save
    And they should see a pending change request banner
    And their profile should show name as "FRA OFA Regional Staff Robert"

  # TODO: verify change requests exist in DB?
