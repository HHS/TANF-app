Feature: Regional Staff can view submission history
    Scenario: A regional user only has view access to submission history for assigned locations
        Given Regional Randy logs in
        When Regional Randy searches FRA Data Files
        Then Regional Randy has read-only access to submission history
