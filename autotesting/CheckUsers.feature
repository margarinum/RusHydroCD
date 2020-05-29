Feature: CheckUsers

  Scenario: Open module "Пользователи" and check table of results

    Given website localhost
    When wait element 'Войти'
    Then input login
    Then input password
    Then push button 'Войти'
    Then page include text 'ИСТО «РусГидро»'
    Then push button 'Пользователи'
    Then wait element 'Логин'
    Then end scenario