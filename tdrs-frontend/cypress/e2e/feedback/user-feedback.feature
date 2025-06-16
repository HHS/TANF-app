Feature: User Feedback Submission

  Scenario: User submits feedback through the feedback modal
    Given user visits the home page
    When user clicks on Give Feedback button on home page
    Then the feedback modal and form should be displayed to the user
    When user attempts to submit invalid feedback
    And user submits valid feedback
    

