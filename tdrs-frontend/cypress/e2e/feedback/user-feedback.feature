Feature: User Feedback Submission

  Scenario: Logged-out visitors cannot open feedback
    Given user visits the home page
    Then feedback controls should not be displayed

  Scenario: Users awaiting approval cannot open feedback
    Given 'Unapproved Dave' logs in
    Then feedback controls should not be displayed

  Scenario: User attempts to submit invalid feedback
    Given 'Data Analyst Tim' logs in
    When user clicks on Give Feedback button
    Then the feedback modal and form should be displayed to the user
    When user attempts to submit invalid feedback
    Then an error message should be displayed indicating the issue

  Scenario Outline: Approved users submit anonymous feedback
    Given '<actor>' logs in
    When user clicks on Give Feedback button
    Then the feedback modal and form should be displayed to the user
    When user chooses to send feedback anonymously
    And user submits valid feedback
    Then the feedback is successfully submitted
    And a success confirmation is shown or modal closes

    Examples:
      | actor            |
      | Data Analyst Tim |
      | Admin Alex       |
