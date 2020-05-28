#!/usr/bin/python3.6

# -*- coding: utf-8 -*-

from behave import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os


def waitElem(context, text):
    WebDriverWait(context.browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "%s")]' % text)))


def waitPlaceholder(context, text):
    WebDriverWait(context.browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='{placeholder}']".format(placeholder=text))))


@given('website "{url}"')
def step(context, url):
    # Измените строку, для выполнения теста в другом браузере
    options = Options()
    # options.headless = True
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    print(os.path.join(os.getcwd(), 'chromedriver'))
    context.browser = webdriver.Chrome(os.path.join(os.getcwd(), 'autotesting', 'steps', 'chromedriver'),
                                       chrome_options=options,
                                       service_log_path=os.path.join(os.getcwd(), 'chromedriver.log'))
    context.browser.maximize_window()
    context.browser.get(url)


@given('website localhost')
def step(context):
    # Измените строку, для выполнения теста в другом браузере
    options = Options()
    # options.headless = True
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    print(os.path.join(os.getcwd(), 'chromedriver'))

    context.browser = webdriver.Chrome(
        executable_path=os.path.join(os.getcwd(), 'autotesting', 'steps', 'chromedriver'),
        chrome_options=options,
        service_log_path=os.path.join(os.getcwd(), 'chromedriver.log'))
    context.browser.maximize_window()
    context.browser.get('http://localhost/')


@when("wait element '{text}'")
def step(context, text):
    waitElem(context, text)


@then("wait element '{text}'")
def step(context, text):
    waitElem(context, text)


@then("input login")
def step(context):
    login = context.browser.find_element_by_xpath('//*[@id="app"]/div/div/div[5]/div/input')
    login.click()
    login.send_keys(context.config.userdata['LOGIN'])
    # login.send_keys('admin')


@then("input password")
def step(context):
    password = context.browser.find_element_by_xpath('//*[@id="app"]/div/div/div[6]/div/input')
    password.click()
    password.send_keys(context.config.userdata['PASSWORD'])


@then("push button '{text}'")
def step(context, text):
    waitElem(context, text)
    # buttonAuth = context.browser.find_element_by_xpath('//*[@id="app"]/div/div/div[7]/button')
    button = context.browser.find_element_by_xpath("//*[contains(text(), '{buttonText}')]".format(buttonText=text))
    button.click()


@then("open module '{text}'")
def step(context, text):
    waitElem(context, text)
    button = context.browser.find_element_by_xpath('//*[contains(text(), "%s")]' % text)
    # buttonAuth = context.browser.find_element_by_xpath('//*[@id="app"]/div/div/div[7]/button')
    button.click()


# Проверим, что мы на странице с результатами поиска, есть некоторый искомый текст
@then("page include text '{text}'")
def step(context, text):
    WebDriverWait(context.browser, 120).until(
        EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "%s")]' % text))
    )
    assert context.browser.find_element_by_xpath('//*[contains(text(), "%s")]' % text)
    # context.browser.quit()


@then("input '{text}' to placeholder '{field}'")
def step(context, text, field):
    waitPlaceholder(context, field)
    inp = context.browser.find_element_by_xpath("//input[@placeholder='{placeholder}']".format(placeholder=field))
    inp.click()
    inp.send_keys(text)


@then("set element from '{selector}'")
def step(context, selector):
    field = context.browser.find_element_by_xpath(
        ("//input[@placeholder='{placeholder}']".format(placeholder=selector)))
    field.click()
    dropdown = context.browser.find_element_by_xpath('/html/body/div[2]/div[3]/div/div/div/div[1]')
    dropdown.click()


@then('end scenario')
def step(context):
    context.browser.quit()
