from components.Automate_Process.module.automation_process import *
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

class Tiktok_Manager(Automate_Process):
	def __init__(self, 
	      			account,
				user_data_path="", 
				user_agent="",
				profile="Default",
				other_options=False, 
				disable_graphics=True,
				remote_connection=False):
		self.account = account
		super().__init__(f'www.tiktok.com/@{self.account}',
		    		 user_data_path,
				 user_agent,
				 profile,
				 other_options,
				 disable_graphics,
				 remote_connection)
		self.driver.timeouts.implicit_wait = 60

	def get_feed(self):
		feed_videos = list()
		feed_el = self.webElement_to_soup(self.access_field(By.XPATH, "//div[@id='main-content-others_homepage']"))
		posts = feed_el.find_all("div", {"class":"css-1uqux2o-DivItemContainerV2 e19c29qe7"})
		# print("POSTS ARE? ", posts)
		for post in posts:
			post_data = {"link": post.find("a").get("href"),
					"desc": post.find("picture").img.get("alt")}
			feed_videos.append(post_data)
		return feed_videos
		# print("FEED VÍDEOS ARE:\n", feed_videos)
		
	def access_posts(self, videos_dict):
		self.driver.get(videos_dict[0]["link"])
		print("video indexed: ", videos_dict[0])
		# frame_tree = self.driver.execute_cdp_cmd("Page.getResourceTree", {})
		print("FRAME TREE\n", frame_tree)

		# for video in videos_dict:
			# self.driver.get(video["link"])
	def standard_procedure(self):
		self.access_url()
		sleep(60)
		videos = self.get_feed()
		self.access_posts(videos)
		