Feature: Users can create and manage their accounts
    Scenario: A user can log in
        When I visit the home page
        And I click the login button
        Then I get logged in