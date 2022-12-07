Feature: Users can create and manage their accounts
    Scenario: A user can log in and request access
        When I visit the home page
        And I log in as a new user
        Then I see a Request Access form