from components.PlayWrightAuto.essencial import PlayEssencial
import requests
import datetime
import re

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

	def iterate_video_links(self, result_info: dict):
		for key in list(result_info.keys()):
			yield key

	def requests_seletion(self, response, find_term, configs : str):
		begin = response.text.find(find_term)
		end = response.text[begin:].find(configs) + begin
		result = response.text[begin:end]
		print(result)
		result = str(result.replace('"', '')).removeprefix(find_term.replace('"', ''))
		result = re.findall(r'\d+', result)
		return result

	def get_request_createdTime(self, response, result_info: dict, start_date, end_date, photo_metrics = None):
		def requests_seletion(response, find_term, configs : str):
			begin = response.text.find(find_term)
			end = response.text[begin:].find(configs) + begin
			result = response.text[begin:end]
			result = str(result.replace('"', '')).removeprefix(find_term.replace('"', ''))
			result = re.findall(r'\d+', result)
			return result		
		print(f"Status Code: {response.status_code}")
		findResp = response.text.find("webapp.video-detail") - 1
		if findResp <= -1:
			print("not found")
			result_info[self.current_url]["date_created"] = photo_metrics[4] if photo_metrics else "notFound"
			result_info[self.current_url]["curtidas"] = photo_metrics[0] if photo_metrics else "notFound"
			result_info[self.current_url]["compartilhamentos"] = photo_metrics[3] if photo_metrics else "notFound"
			result_info[self.current_url]["comentários"] = photo_metrics[1] if photo_metrics else "notFound"
			result_info[self.current_url]["reproduções"] = photo_metrics[5] if photo_metrics else "notFound"
			result_info[self.current_url]["salvos"] = photo_metrics[2] if photo_metrics else "notFound"
			result_info[self.current_url]["repostado"] = photo_metrics[6] if photo_metrics else "notFound"
			if photo_metrics != None:
				processed_date = datetime.datetime.strptime(photo_metrics[4], '%d/%m/%Y %H:%M:%S')
				if processed_date < start_date:
					return (0)
				if processed_date > end_date:
					return (1)
		else:
			begin = response.text[findResp:].find("createTime") + findResp - 1
			end = response.text[begin:].find(",") + begin
			result = response.text[begin:end]
			result = int(str(result.replace('"', '')).removeprefix("createTime:"))
			processed_date = datetime.datetime.fromtimestamp(result)
			print(processed_date)
			if processed_date < start_date:
				return (0)
			if processed_date > end_date:
				return (1)
			result_info[self.current_url]["date_created"] = datetime.datetime.fromtimestamp(int(result)).strftime("%d/%m/%Y %H:%M:%S")
			interactions = requests_seletion(response, '"statsV2":', '}')
			result_info[self.current_url]["curtidas"] = interactions[0] if len(interactions) != 0 else "notFound"
			result_info[self.current_url]["compartilhamentos"] = interactions[1] if len(interactions) != 0 else "notFound"
			result_info[self.current_url]["comentários"] = interactions[2] if len(interactions) != 0 else "notFound"
			result_info[self.current_url]["reproduções"] = interactions[3] if len(interactions) != 0 else "notFound"
			result_info[self.current_url]["salvos"] = interactions[4] if len(interactions) != 0 else "notFound"
			result_info[self.current_url]["repostado"] = interactions[5] if len(interactions) != 0 else "notFound"
		return(self.current_url)
		

	def access_videos(self, result_info: dict, start_date, end_date):
		# self.page.close()
		all_videos = []
		counter = 0
		for link in self.iterate_video_links(result_info):
			self.set_url(link)
			
			print('entrei')
			link_splited = link.split('/')
			def search_metrics_photo(link_splited):
				if link_splited[4] == "photo":
					print("This is a photo")
					self.page.goto(self.current_url, timeout=30000)
					self.page.wait_for_load_state("domcontentloaded",timeout=30000)
					input("VERIFY IF THE PAGE HAS A PROBLEM OF CAPTCHA OR ERROR. THEN, PRESS ENTER TO CONTINUE")
					self.page.wait_for_selector("//button[@class='css-rninf8-ButtonActionItem edu4zum0']")
					mertrics = self.page.locator("//button[@class='css-rninf8-ButtonActionItem edu4zum0']//strong[@class='css-1l70c6-StrongText edu4zum2']").all_inner_texts()
					date = self.page.locator("//span[@class='css-5set0y-SpanOtherInfos evv7pft3']").all_inner_texts()
					print("mertrics are: ", mertrics)
					print("date is: ", date)
					data_str = re.findall(r'\d+', date[0])
					print("data_str is: ", data_str)
					if len(data_str) < 3:
						year_now = datetime.datetime.now().year
						print("year_now is: ", year_now)
						data_str.insert(0, str(year_now))
					processed_date = datetime.datetime.strptime("/".join(data_str), '%Y/%m/%d')
					mertrics.append(processed_date.strftime("%d/%m/%Y %H:%M:%S"))
					return mertrics
			response = requests.get(self.current_url, headers=self.headers)
			metrics_photo = search_metrics_photo(link_splited)
			element_vid = self.get_request_createdTime(response, result_info, start_date, end_date, metrics_photo)
			# element = self.requests_seletion(response, '"statsV2":', '}')
			# print("elements is >>>", element)
			print("ALL VIDEOS ARE: ", all_videos)
			print("element_vid is: ", element_vid)
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
				print(result_info)
			return result_info

	def standard_procedure(self, dates: list):
		if self.browser == None: 
			self.start_browser_user()
		data = self.get_feed_info()
		print("FEED DATA -> ", data)
		value = self.access_videos(data, dates[0], dates[1])
		print(value)
		return value

		#  print(data)