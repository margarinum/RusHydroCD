Feature: CheckStations

  Scenario: Open module "Станции" and check table of results

    Given website localhost
    When wait element 'Войти'
    Then input login
    Then input password
    Then push button 'Войти'
    Then page include text 'ИСТО «РусГидро»'
    Then push button 'Станции'
    Then wait element 'Станция'
    Then end scenario


