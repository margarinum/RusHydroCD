# Created by dima at 13.05.20
Feature: CheckStations

  Scenario: Open module station

    Given website localhost
    #Given website "http://localhost/"
    When wait element 'Войти'
    #Then input 'admin' to placeholder 'Логин'
    Then input login
    Then input password
    Then push button 'Войти'
    Then page include text 'ИСТО «РусГидро»'
    Then push button 'Станции'
    Then wait element 'Станция'
    Then end scenario


