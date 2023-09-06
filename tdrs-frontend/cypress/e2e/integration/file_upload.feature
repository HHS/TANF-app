Feature: Users can create and manage their accounts  
    Scenario: A user can upload a file
        Given The admin logs in
        And 'new-cypress@teamraft.com' is in approved state
        When 'new-cypress@teamraft.com' visits the home page
        And 'new-cypress@teamraft.com' logs in
        Then 'new-cypress@teamraft.com' can see Data Files page
        Then 'new-cypress@teamraft.com' can see search form
        Then 'new-cypress@teamraft.com' can browse upload file form
        When 'new-cypress@teamraft.com' uploads a file
        Then 'new-cypress@teamraft.com' can see the upload successful