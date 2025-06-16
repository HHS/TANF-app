Feature: User Feedback Submission
  Scenario: User submits feedback through the feedback modal
    When user visits the home page
    Given user clicks on Give Feedback button on home page
    Then feed back modal and form should display to user
    Then user attempts to submit invalid feedback
    Then user submits valid feedback (rating is selected)
