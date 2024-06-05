
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
import re

class Selenium_Manager:

	def __init__(self, url_post_3w, chrome_data_path, user_agent):
		self.url = "https://" + url_post_3w
		self.options = webdriver.ChromeOptions()
		self.s = Service(ChromeDriverManager().install())
		self.options.add_argument(chrome_data_path)
		self.options.add_argument('--headless')
		self.options.add_argument('--disable-gpu')
		self.options.add_argument('log-level=2')
		self.options.add_argument(user_agent)
		self.driver = self.open_driver()

	def open_driver(self):
		driver = webdriver.Chrome(options=self.options,
									   service=self.s)
		return driver
	def access_url(self):
		self.driver.get(self.url)
		print(f"a url {self.url} foi acessada!")

	def access_field(self, type : By, elem, time_to_wait) -> WebElement:
		# print(f"Acessando o elemento: {elem}")
		self.driver.implicitly_wait(time_to_wait)
		elem = self.driver.find_element(type, elem)
		return elem

	def do_action(self, target, action, message=None, press_return=False):

		if action == "click":
			target.click()
		elif action == "send_keys":
			target.send_keys(message)
			if (press_return == True):
				target.send_keys(Keys.RETURN)

	def do_presskeys(self, first_key, second_key):
		action = ActionChains(self.driver)
		action.key_down(first_key).send_keys(second_key).key_up(first_key).perform()

class Automate_Process(Selenium_Manager):
	def __init__(self, url_post_3w, chrome_data_path, user_agent):
		super().__init__(url_post_3w, chrome_data_path, user_agent)

	def webElement_to_html(self, elem: WebElement) -> BeautifulSoup:
		"""
		Get the outerHTML of a field accessed, processes a soup with the BeautifulSoup class
		and returning the soup.
		
		Params:
			:param elem: WebElement class that is accessed by selenium.
		
		Return:
			returns the BeautifulSoup class with the html parser of the OuterHTML by selenium WebElement
		"""
		value = elem.get_attribute("outerHTML")
		soup = BeautifulSoup(value, "html.parser")
		return soup
	
	def handle_texts(self, splited_text: list, text_object: dict) -> dict:

		for elem in splited_text:
			if not re.search(r"http[:s][^ ]|[^ ]+(?:[.]com)|[^ ]+(?:[.]br)|[^ ]+(?:[.]gov)", elem) == None:
				text_object["links"].append(elem)
			elif not(elem.find("PM") == -1 and elem.find("AM") == -1) and (len(elem) >= 6 and len(elem) <= 8):
				text_object["date"].append(elem)
			else:
				text_object["texts"].append(elem)
	
	def get_all_elem_by_filter(self, soup: BeautifulSoup, html_tag: str, attrs:dict)->list:
		arr_list = []
		list_elem = soup.find_all(html_tag, attrs)
		for father in list_elem:
			# minnor_arr = []
			text_object = {'texts':[],'links':[], 'date':[], 'check': True}
			i = 0
			for elem in father:
				if not elem == '\n':
					try:
						texts = elem.get_text("|").split("|")
						self.handle_texts(texts, text_object)
					except Exception as err:
						print(f"Couldn't get the attributes of the below html element:\n{elem}\nError:{err}")
				# else :
				# 	print("O elemento é uma quebra de linha")
			arr_list.append(text_object)	
		return arr_list