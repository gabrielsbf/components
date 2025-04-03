from components.PlayWrightAuto.essencial import PlayEssencial
import requests
import datetime

class Tiktok_Automation(PlayEssencial):
	def __init__(self, account, browser=None, page=None):
		super().__init__("https://tiktok.com/@" + account, browser)
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
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
	}

	def iterate_video_links(self, result_info: dict):
		for key, _ in result_info.items():
			yield key

	def get_request_createdTime(self, response, result_info: dict, start_date, end_date):
		print(f"Status Code: {response.status_code}")
		# print(f"Response is: {response.text}")
		findResp = response.text.find("webapp.video-detail") - 1
		if findResp <= -1:
			print("not found")
			result_info[self.current_url]["date_created"] = "notFound"
		else:
			begin = response.text[findResp:].find("createTime") + findResp - 1
			end = response.text[begin:].find(",") + begin
			result = response.text[begin:end]
			result = int(str(result.replace('"', '')).removeprefix("createTime:"))
			print(result)
			processed_date = datetime.datetime.fromtimestamp(result)
			print(processed_date)
			if processed_date < start_date:
				return (0)
			if processed_date > end_date:
				return (1)
			else:
				result_info[self.current_url]["date_created"] = datetime.datetime.fromtimestamp(int(result)).strftime("%d/%m/%Y %H:%M:%S")
				return (self.current_url)
		return(self.current_url)
		

	def access_videos(self, result_info: dict, start_date, end_date):
		# self.page.close()
		all_videos = []
		counter = 0
		for link in self.iterate_video_links(result_info):
			print('entrei')
			self.set_url(link)
			element_vid = self.get_request_createdTime(requests.get(self.
			current_url, headers=self.headers), result_info, start_date, end_date)
			print("ALL VIDEOS ARE: ", all_videos)
			if (element_vid != 0 and element_vid != 1):
				all_videos.append(element_vid)
			if (element_vid == 0 and counter > 3):
					break
			counter += 1

		filtered_result_info = {k: v for k, v in result_info.items() if k in all_videos}
		return filtered_result_info
	
	def get_feed_info(self):
			result_info = {}
			if not self.page:
				raise Exception("Browser or page not initialized. Call start_browser() first.")
			self.page.goto(self.current_url, timeout=30000)
			input("VERIFY IF THE PAGE HAS A PROBLEM OF CAPTCHA OR ERROR. THEN, PRESS ENTER TO CONTINUE")
	  
			self.page.wait_for_load_state("domcontentloaded",timeout=30000)

			self.page.wait_for_selector("//div[@id='main-content-others_homepage']")

			feed = self.page.locator("//div[@id='main-content-others_homepage']")
			items = feed.locator('//div[@class="css-1uqux2o-DivItemContainerV2 e19c29qe7"]')
			views = self.page.locator('//div[@class="css-1qb12g8-DivThreeColumnContainer eegew6e2"]//strong[@class="video-count css-dirst9-StrongVideoCount e148ts222"]')
			count = items.count()
			for i in range(count):
				item = items.nth(i)
				result_info[item.locator("a").get_attribute("href")] = {"description": item.locator("img").get_attribute("alt"), 'views' : views.nth(i).inner_text()}
			return result_info

	def standard_procedure(self, dates: list):
		if self.browser == None: 
			self.start_browser()
		data = self.get_feed_info()
		print("FEED DATA -> ", data)
		value = self.access_videos(data, dates[0], dates[1])
		return value
		#  print(data)