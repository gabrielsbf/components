from components.Automate_Process.module.automation_process import *
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from datetime import datetime

class Twitter_Manager(Automate_Process):
	def __init__(self, account, user_data_path, user_agent, graphics_disable=True):
		self.account = account
		super().__init__(f'x.com/{self.account}', user_data_path, user_agent, graphics_disable)

	def get_post_href(self, data: list):
		for link in data:
			if 'status' in link:
				if 'analytics' not in link:
					return link
			
	def get_obj_date(self, soup: BeautifulSoup, html_tag = None, attrs = None):
		target = soup.find('time')
		return target.get('datetime')

	def return_brute_data(self, since: datetime, until: datetime):
		i = 1
		value = self.driver.execute_script("return window.innerWidth")
		list_values = []
		last_date = datetime.now()
		# 2024-06-14T20:00:52.000Z
		while last_date > since :
			dropdown = value * i
			self.driver.execute_script(f"window.scrollTo(0, {dropdown});")
			sleep(2)
			data = self.access_field(By.XPATH, '//section[@class="css-175oi2r"]',6)
			soup = self.webElement_to_html(data)
			post = self.get_all_elem_by_filter(soup, "article",{'role': 'article'}, self.get_obj_date)
			list_values.extend(post)
			last_date = datetime.strptime(list_values[-1].get('extra'), "%Y-%m-%dT%H:%M:%S.%fZ")
			print("last date is: ", last_date)
			i+=1
		sleep(2)
		result = []
		urls = []
		for x in list_values:
			if urls.count(x['hrefs']) == 0:
				result.append(x)
				urls.append(x['hrefs'])
		return list(filter(lambda x: datetime.strptime(x['extra'],"%Y-%m-%dT%H:%M:%S.%fZ") >= since 
			and datetime.strptime(x['extra'],"%Y-%m-%dT%H:%M:%S.%fZ") <= until, result))

	def clean_data(self, brute_data: list):
		for data in brute_data:
			has_tlink = ["links:"] + data["text_links"] if not data["text_links"] == [] else ''
			data["texts"] = ' '.join(data["texts"]) + '\n'.join(has_tlink)
			data['effective_link'] = 'https://x.com' + self.get_post_href((data['hrefs']))
			del data['date']
			del data["text_links"]
			del data['hrefs']
		
	def standard_procedure(self, outfile_name, since, until):
		
		data = self.return_brute_data(since, until)
		self.clean_data(data)
		print(data)
		table = pd.DataFrame(data)
		table.to_excel(outfile_name)