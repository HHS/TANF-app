Feature: User Feedback Submission

  Scenario: User attempts to submit invalid feedback
    Given user visits the home page
    When user clicks on Give Feedback button on home page
    Then the feedback modal and form should be displayed to the user
    When user attempts to submit invalid feedback
    Then an error message should be displayed indicating the issue
    
  Scenario: User submits valid feedback
    Given user visits the home page
    When user clicks on Give Feedback button on home page
    Then the feedback modal and form should be displayed to the user
    When user submits valid feedback
    Then the feedback is successfully submitted
    And a success confirmation is shown or modal closes