Feature: Authorisation

  Scenario: Authorisation into system with login and password

    Given website localhost
    When wait element 'Войти'
    Then input login
    Then input password
    Then push button 'Войти'
    Then page include text 'ИСТО «РусГидро»'