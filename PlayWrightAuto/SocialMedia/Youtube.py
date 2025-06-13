from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime
from typing import Generator
from requests import Response
import requests
import re


class Youtube_Automation(PlayEssencial):
    def __init__(self, account, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
        super().__init__("https://www.youtube.com/", playwright, browser_data_path, chrome_executable_path, browser, page)
        self.account = account
        self.headers = {
            "authority": "www.youtube.com",
            "method": "GET",
            # "path": "/watch?v=UWmmoKIC8B4",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-form-factors": '"Desktop"',
            "sec-ch-ua-full-version": '"134.0.6998.178"',
            "sec-ch-ua-full-version-list": '"Chromium";v="134.0.6998.178", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.178"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"19.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "service-worker-navigation-preload": "true",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "x-browser-channel": "stable",
            "x-browser-copyright": "Copyright 2025 Google LLC. All rights reserved.",
            "x-browser-validation": "wTKGXmLo+sPWz1JKKbFzUyHly1Q=",
            "x-browser-year": "2025",
            "x-client-data": "CIi2yQEIo7bJAQipncoBCKP3ygEIk6HLAQiJo8sBCJ3+zAEIhaDNAQj9284BCK/kzgEIl+bOAQjv5s4BGODizgEYm+fOAQ=="
        }
    def get_video_content(self)-> Generator[dict, None, None]:
        video_info = []
        def extract_hrefs(url)-> None:
            self.set_url(url)
            self.page.goto(self.current_url, timeout=30000)
            input("VERIFY IF THE PAGE HAS A PROBLEM OF CAPTCHA OR ERROR. THEN, PRESS ENTER TO CONTINUE")
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(3000)
            hrefs = self.page.eval_on_selector_all('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]', '(links) => links.map(link => link.href)')
            titles = self.page.eval_on_selector_all('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]', '(links) => links.map(link => link.title)')
            print(f"hrefs are: {hrefs}\ntitles are:{titles}", hrefs)
            [video_info.append(info) for info in zip(hrefs, titles)]
        extract_hrefs(self.current_url + self.account + '/videos')
        extract_hrefs('https://www.youtube.com/c/'+ self.account + '/streams')
        print("VIDEO INFO IS:", video_info)
        for href, title in video_info:
            yield {"title": title, "href": href}

    def scrape_videos_by_date(self, start_date :  datetime, end_date : datetime)-> dict:
        filtered_videos = {}
        def extract_text_between(response : Response, start_maker : str, end_maker : str)-> str:
            if type(start_maker) == list:
                start_maker = start_maker[0] if response.text.find(start_maker[0]) != -1 else start_maker[1]
                start_index = response.text.find(start_maker)
                end_index = response.text[start_index:].find(end_maker) + start_index
                snippet = response.text[start_index:end_index]
                snippet = str(snippet.replace('"', '')).removeprefix(start_maker.replace('"', ''))
                return snippet
            start_index = response.text.find(start_maker)
            end_index = response.text[start_index:].find(end_maker) + start_index
            snippet = response.text[start_index:end_index]
            snippet = str(snippet.replace('"', '')).removeprefix(start_maker.replace('"', ''))
            return snippet
        for video in self.get_video_content():
            self.set_url(video['href'])
            response = requests.get(self.current_url, headers=self.headers)
            processed_date_raw = extract_text_between(response, list(['"startTimestamp":', '"uploadDate":']), ",")
            processed_date = datetime.fromisoformat(processed_date_raw.strip().strip('}')).replace(tzinfo=None)

            comments_raw = extract_text_between(response, '"contextualInfo":', ",")
            views_raw = extract_text_between(response, '"views":', ",")
            likes = extract_text_between(response, '"likeCount":', ",")


            comments = re.findall(r"\d+", comments_raw)
            views = re.findall(r"\d+(?:[\.,]\d+)?", views_raw)

            comments_count = comments[0] if comments else "0"
            views_count = views[0] if views else "0"

            if processed_date > end_date:
                continue
            if processed_date < start_date:
                break
            filtered_videos[video['href']] = {"title": video['title'], 
                                         "date": processed_date, 
                                         "likes" : likes, 
                                         "comments" : comments_count, 
                                         "views" : views_count
            }             
        # print("Total de vídeos filtrados:", len(filtered_videos))
        # print(filtered_videos)
        return filtered_videos

    def standard_procedure(self, dates: list[datetime])-> dict:
        """
			Standard procedure to access TikTok videos within a specified date range.
			Args:
				dates (list[datetime:datetime]): List containing two datetime objects representing the start and end dates.
			Returns:
		"""
        if self.browser == None: 
            self.start_browser_user()
        data = self.scrape_videos_by_date(dates[0], dates[1])
        # self.stop_browser()
        return data
    