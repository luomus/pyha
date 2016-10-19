# coding=utf-8
import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Requestlist_TestCase(unittest.TestCase):
	
	def setUp(self):			
		chromedriver = "/home/ad/fshome5/u5/r/rivorivo/Linux/Python/envi3/lib/python3.4/site-packages/chromedriver/bin/chromedriver"
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

	def test_request_link_visible(self):	
		driver = self.driver
		teksti = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[1]')
		self.assertEqual('kuvaus',teksti.text)
	
	def test_status_sana_ei_numero(self):
		driver = self.driver
		teksti = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[4]')
		self.assertEqual('Käsittelyssä',teksti.text)
	
	#on amerikkalaisittain
	#def test_paivaus_fiksusti(self):
	#	driver = self.driver
	#	teksti = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[2]')
	#	self.assertEqual('10. lokakuuta 2016 kello 16.22',teksti.text)
		
	def tearDown(self):
		self.driver.close()

class Requestpage_TestCase(unittest.TestCase):
	
	def setUp(self):			
		chromedriver = "/home/ad/fshome5/u5/r/rivorivo/Linux/Python/envi3/lib/python3.4/site-packages/chromedriver/bin/chromedriver"
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
		driver.get("http://127.0.0.1:8000/request/1")

	def test_rajauksetNapista(self):
		driver = self.driver
		nappi = driver.find_element_by_xpath('/html/body/div[1]/div[1]/button[1]')
		nappi.click()
		kohde = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/table[1]')
	
		self.assertEqual('Rajaus Arvot\ntarget linnut',kohde.text)

	def tearDown(self):
		self.driver.close()

if __name__ == "__main__":
    unittest.main()




