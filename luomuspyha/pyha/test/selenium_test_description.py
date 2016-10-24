import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Change_description_TestCase(unittest.TestCase):
	
	def setUp(self):
		# vaihda oma chromedriverin osoite ennen ajamista
		chromedriver = "/home/ad/fshome1/u1/a/aesalmin/Linux/venv3/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		self.driver = webdriver.Chrome(chromedriver)
		driver = self.driver
		driver.get("http://127.0.0.1:8000/mock/jsonmock")
		driver.find_element_by_xpath("/html/body/form[1]").submit()
		driver.get("http://127.0.0.1:8000/pyha/")
		driver.find_element_by_id("local-login").click()
		elem = driver.find_element_by_id("login-form")
		email = driver.find_element_by_name("email")
		password = driver.find_element_by_name("password")
		email.send_keys("pyhatestaaja@gmail.com")
		password.send_keys("L4ausesuomeksi")
		elem.submit()		
		
	def test_empty_description(self):
		driver = self.driver
		date = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[2]').text		
		driver.get("http://127.0.0.1:8000/pyha/request/1")
		elem = driver.find_element_by_id("description-form")		
		desc = driver.find_element_by_id("description")
		desc.clear()
		elem.submit()
		header= driver.find_element_by_tag_name('h1')
		self.assertEqual('Pyyntö:' + date, header.text) #korjaus odottaa lopullista muotoa
	
	def test_changing_description(self):
		driver = self.driver
		driver.get("http://127.0.0.1:8000/pyha/request/1")
		elem = driver.find_element_by_id("description-form")		
		desc = driver.find_element_by_id("description")
		desc.clear()
		desc.send_keys("kokeiluotsikko")
		elem.submit()
		header= driver.find_element_by_tag_name('h1')
		self.assertEqual('Pyyntö: kokeiluotsikko', header.text)		
	
	def tearDown(self):
		self.driver.close()

if __name__ == "__main__":
    unittest.main()
