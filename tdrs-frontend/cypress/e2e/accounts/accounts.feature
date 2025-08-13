Feature: Users can create and manage their accounts
    Scenario: An OFA System Admin can log in and access the site
        Given 'Unapproved Alex' logs in
        When Unapproved Alex requests access
            And Admin Alex approves 'Unapproved Alex'
        Then 'Unapproved Alex' can access 'TANF Data Files, FRA Data Files, Admin, Grafana, Alerts'
            And 'Unapproved Alex' gets an approval email
            And Admin Alex gets an email

    Scenario: A DIGIT Team member can log in and access the site
        Given 'Unapproved Diana' logs in
        When Unapproved Diana requests access
            And Admin Alex approves 'Unapproved Diana'
        Then 'Unapproved Diana' can access 'TANF Data Files, Admin, Grafana'
            And 'Unapproved Diana' gets an approval email

    Scenario: An OCIO member can log in and access the site
        Given 'Unapproved Olivia' logs in
        When Unapproved Olivia requests access
            And Admin Alex approves 'Unapproved Olivia'
        Then 'Unapproved Olivia' can access 'Admin'
            And 'Unapproved Olivia' gets an approval email

    Scenario: A Data Analyst can log in and access the site
        Given 'Unapproved Dave' logs in
        When Unapproved Dave requests access
            And Admin Alex approves 'Unapproved Dave'
        Then 'Unapproved Dave' can access 'TANF Data Files'
            And 'Unapproved Dave' gets an approval email

    Scenario: A Data Analyst can log in and request FRA access
        Given 'Unapproved Fred' logs in
        When Unapproved Fred requests access with FRA
            And Admin Alex approves 'Unapproved Fred'
        Then 'Unapproved Fred' can access 'TANF Data Files, FRA Data Files'
            And 'Unapproved Fred' gets an approval email

    Scenario: A Regional user can log in and access the site
        Given 'Unapproved Randy' logs in
        When Unapproved Randy requests access
            And Admin Alex approves 'Unapproved Randy'
        Then 'Unapproved Randy' can access 'TANF Data Files, FRA Data Files'
            And 'Unapproved Randy' gets an approval email
