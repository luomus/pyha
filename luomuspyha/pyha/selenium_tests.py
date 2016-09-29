from selenium import webdriver
from selenium.webdriver.common.keys import Keys
driver = webdriver.Firefox()
driver.get("http://127.0.0.1:8000/index/")
driver.find_element_by_id("local-login").click()
driver.find_element_by_id("login-form").submit()