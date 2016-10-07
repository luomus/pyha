import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Mockrequest_TestCase(unittest.TestCase):
	
	def setUp(self):
		chromedriver = "/home/ad/fshome5/u5/r/rivorivo/Linux/Python/envi3/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		self.driver = webdriver.Chrome(chromedriver)

	def test_request_link_visible(self):	
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
		teksti = driver.find_element_by_xpath('/html/body/div[1]/div[1]/ul[1]/li[1]/a[1]')
		self.assertEqual('HBF.C60AB314-43E9-41F8-BB7D-0775773B16BD',teksti.text)
	
	def tearDown(self):
		self.driver.close()

if __name__ == "__main__":
    unittest.main()




