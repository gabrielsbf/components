from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
import re
from components.Date_Utils.module.date_time_utils import Date_Utils

class Selenium_Manager(Date_Utils):

	def __init__(self, url_post_3w, chrome_data_path, user_agent, disable_graphics=True):
		"""
        Initialize Selenium_Manager class.

        Parameters:
            url_post_3w (str): The URL to be accessed.
            chrome_data_path (str): The path to Chrome data.
            user_agent (str): User agent string.
        """
		super().__init__()
		self.url = "https://" + url_post_3w
		self.options = webdriver.ChromeOptions()
		self.s = Service(ChromeDriverManager().install())
		self.options.add_argument(f"--user-data-dir={chrome_data_path}")
		if disable_graphics == True:
			self.options.add_argument('--headless')
			self.options.add_argument('--disable-gpu')
		self.options.add_argument('log-level=2')
		self.options.add_argument(f"user-agent={user_agent}")
		self.driver = self.open_driver()

	def open_driver(self):
		"""
        Open Chrome WebDriver.

        Returns:
            WebDriver: Chrome WebDriver.
        """
		driver = webdriver.Chrome(options=self.options,
									   service=self.s)
		return driver
	
	def access_url(self):
		self.driver.get(self.url)
		print(f"a url {self.url} foi acessada!")

	def access_field(self, type : By, elem, time_to_wait) -> WebElement:
		"""
    	Access a specific field on the webpage.

    	Parameters:
        	type (By): The type of locator (e.g., By.ID, By.CLASS_NAME).
        	elem (str): The element to be accessed (e.g., "some_id", "some_class").
        	time_to_wait (int): Time to wait for the element to be found, in seconds.

    	Returns:
        	WebElement: The accessed element.
    """
		# print(f"Acessando o elemento: {elem}")
		self.driver.implicitly_wait(time_to_wait)
		elem = self.driver.find_element(type, elem)
		return elem

	def do_action(self, target, action, message=None, press_return=False):
		"""
        Perform an action on a target WebElement.

        Parameters:
            target (WebElement): The target element to perform action on.
            action (str): The action to perform ('click' or 'send_keys').
            message (str): The message to send (for 'send_keys' action).
            press_return (bool): Whether to press return key after sending keys.
        """
		if action == "click":
			target.click()
		elif action == "send_keys":
			target.send_keys(message)
			if (press_return == True):
				target.send_keys(Keys.RETURN)

	def do_presskeys(self, first_key, second_key):
		"""
        Perform key press action.

        Parameters:
            first_key (str): The first key to press.
            second_key (str): The second key to press.
        """
		action = ActionChains(self.driver)
		action.key_down(first_key).send_keys(second_key).key_up(first_key).perform()

class Automate_Process(Selenium_Manager):
	def __init__(self, url_post_3w, chrome_data_path, user_agent, disable_graphics=True):
		super().__init__(url_post_3w, chrome_data_path, user_agent, disable_graphics)

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

	def get_hrefs(self, a_tags, text_object: dict):
		for a_tag in a_tags:
			text_object['hrefs'].append(a_tag.get('href'))


	def handle_texts(self, splited_text: list, text_object: dict)-> None:
		"""
        Handle text processing.

        Parameters:
            splited_text (list): List of splitted text.
            text_object (dict): Dictionary to store processed text.

        """

		for elem in splited_text:
			if not re.search(r"http[:s][^ ]|[^ ]+(?:[.]com)|[^ ]+(?:[.]br)|[^ ]+(?:[.]gov)", elem) == None:
				text_object["text_links"].append(elem)
			elif self.validate_time(elem) :
				text_object["date"].append(elem)
			else:
				text_object["texts"].append(elem)
	
	def get_all_elem_by_filter(self, soup: BeautifulSoup, html_tag: str, attrs:dict, custom_fun = None)->list:
		"""
        Get all elements by filter.

        Parameters:
            soup (BeautifulSoup): BeautifulSoup object.
            html_tag (str): HTML tag to filter.
            attrs (dict): Attributes to filter.

        Returns:
            list: List of filtered elements.
        """
		arr_list = []
		list_elem = soup.find_all(html_tag, attrs)
		for father in list_elem:
			# minnor_arr = []
			text_object = {'texts':[],'text_links':[], 'date':[], 'hrefs': [], 'check': True}
			i = 0

			for elem in father:
				try:self.get_hrefs(elem.find_all('a'), text_object)
				except:print("element don't have hrefs")
				if not custom_fun == None:
					nb = 1
					for i in custom_fun:
						text_object['extra_' + str(nb)] = i(elem, html_tag, attrs)
						nb+=1
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
