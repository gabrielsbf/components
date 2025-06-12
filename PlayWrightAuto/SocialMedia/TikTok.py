from components.PlayWrightAuto.essencial import PlayEssencial
from requests import Response
from typing import Union, Generator
import json
import requests
import datetime

class Tiktok_Automation(PlayEssencial):
	def __init__(self, account, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
		super().__init__("https://tiktok.com/@" + account, playwright, browser_data_path, chrome_executable_path, browser, page)
		self.headers = {
			"authority": "www.tiktok.com",
			"method": "GET",
			# "path": "/@niteroipref/video/7485850635112385847",
			"scheme": "https",
			"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
			"accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
			"cache-control": "max-age=0",
			"priority": "u=0, i",
			"sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
			"sec-ch-ua-mobile": "?0",
			"sec-ch-ua-platform": '"Windows"',
			"sec-fetch-dest": "document",
			"sec-fetch-mode": "navigate",
			"sec-fetch-site": "same-origin",
			"sec-fetch-user": "?1",
			"upgrade-insecure-requests": "1",
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
	}

	def iterate_video_links(self, result_info: dict)-> Generator[str, None, None]:
		"""
			Yields each key from the result_info dictionary one by one.

			Args:
				result_info (dict): Dictionary containing video information.

			Yields:
				str: Each key from the dictionary, representing a video link or identifier.
		"""
		for key in list(result_info.keys()):
			yield key

	def extract_text_between(self, response : Response, start_maker : str, end_maker : str)-> dict:
		"""
			Extracts the contents of the 'statsV2' field from the JSON response.
			Returns:
			- A dictionary with the statistics (likes, comments, etc.).
		"""
		start_index = response.text.find(start_maker)
		end_index = response.text[start_index:].find(end_maker) + start_index
		snippet = response.text[start_index:end_index]
		print("Snippet is >>>", snippet)
		if not snippet:
			print("Snippet is empty")
			return {}
		else:
			snippet = "{" + snippet + "}"
			json_data = json.loads(snippet)
		return json_data

	def get_request_createdTime(self, response : Response, result_info: dict, start_date : datetime, end_date : datetime) -> Union[int, str]:
		"""
				Processes the response to extract the video's creation timestamp and basic statistics.

				This function performs the following:
				- Locates and parses the "createTime" timestamp from the response.
				- Converts the timestamp into a datetime object.
				- Compares the date to a given range (start_date and end_date).
					- If it's before the range, returns 0.
					- If it's after the range, returns 1.
				- If the date is within the range:
					- Extracts statistics from the "statsV2" field (likes, shares, comments, etc.).
					- Updates the result_info dictionary at the key `self.current_url` with:
						- "digg_count"
						- "share_count"
						- "comment_count"
						- "play_count"
						- "collect_count"
						- "repost_count"

				Args:
					response (Response): The HTTP response object containing video data.
					result_info (dict): A dictionary to store results, organized by URL.
					start_date (datetime): The lower bound of the date filter.
					end_date (datetime): The upper bound of the date filter.

				Returns:
					Union[int, str]:
						- 0 if the creation date is before the start_date.
						- 1 if the creation date is after the end_date.
						- The current URL (self.current_url) if the date is within the range.
		"""
		print(f"Status Code: {response.status_code}")
		findResp = response.text.find("webapp.video-detail") - 1
		if findResp <= -1:
			print("not found")
			result_info[self.current_url]["date_created"] = "notFound"
		else:
			start_index = response.text[findResp:].find("createTime") + findResp - 1
			end = response.text[start_index:].find(",") + start_index
			result = response.text[start_index:end]
			result = int(str(result.replace('"', '')).removeprefix("createTime:"))
			processed_date = datetime.datetime.fromtimestamp(result)
			print(processed_date)
			if processed_date < start_date:
				return (0)
			if processed_date > end_date:
				return (1)
			response_data = self.extract_text_between(response, '"statsV2":', ',"warnInfo"')
			stats = response_data.get('statsV2', {})
			result_info[self.current_url].update({
				"digg_count": int(stats.get("diggCount", "0")),
				"share_count": int(stats.get("shareCount", "0")),
				"comment_count": int(stats.get("commentCount", "0")),
				"play_count": int(stats.get("playCount", "0")),
				"collect_count": int(stats.get("collectCount", "0")),
				"repost_count": int(stats.get("repostCount", "0"))
				})		
		return(self.current_url)
		

	def access_videos(self, result_info: dict, start_date :  datetime, end_date :  datetime) -> dict:
		"""
			Accesses TikTok videos and filters them based on the provided date range.
			Args:
				result_info (dict): Dictionary containing video links and their descriptions.
				start_date (datetime): Start date for filtering videos.
				end_date (datetime): End date for filtering videos.
			Returns:
				dict: Filtered dictionary containing video links and their associated data.
		"""
		all_videos = []
		counter = 0
		for link in self.iterate_video_links(result_info):
			self.set_url(link)
			
			print('entrei')
			response = requests.get(self.current_url, headers=self.headers)
			element_vid = self.get_request_createdTime(response, result_info, start_date, end_date)
			if (element_vid != 0 and element_vid != 1):
				all_videos.append(element_vid)
			if (element_vid == 0 and counter > 3):
					break
			counter += 1
		filtered_result_info = {k: v for k, v in result_info.items() if k in all_videos}
		return filtered_result_info
	
	def get_feed_info(self)-> dict:
		"""
			Gets the feed information from TikTok.
			Returns:
				dict: Dictionary containing video links and their descriptions.
		"""
		result_info = {}
		if not self.page:
			raise Exception("Browser or page not initialized. Call start_browser() first.")
		self.page.goto(self.current_url, timeout=30000)
		input("VERIFY IF THE PAGE HAS A PROBLEM OF CAPTCHA OR ERROR. THEN, PRESS ENTER TO CONTINUE")
		self.page.wait_for_load_state("domcontentloaded",timeout=30000)
		self.page.wait_for_selector("//div[@id='main-content-others_homepage']")
		feed = self.page.locator("//div[@id='main-content-others_homepage']")
		items = feed.locator('//div[@class="css-1uqux2o-DivItemContainerV2 e19c29qe7"]')
		count = items.count()
		for i in range(count):
			item = items.nth(i)
			result_info[item.locator("a").get_attribute("href")] = {"description": item.locator("img").get_attribute("alt")}
			print(result_info)
		return result_info

	def standard_procedure(self, dates: list[datetime:datetime])-> dict:
		"""
			Standard procedure to access TikTok videos within a specified date range.
			Args:
				dates (list[datetime:datetime]): List containing two datetime objects representing the start and end dates.
			Returns:
				dict: Dictionary containing video links and their associated data.
		"""
		if self.browser == None: 
			self.start_browser_user()
		data = self.get_feed_info()
		print("FEED DATA -> ", data)
		value = self.access_videos(data, dates[0], dates[1])
		print(value)
		return value