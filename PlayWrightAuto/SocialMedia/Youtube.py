from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime
import locale
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

    def get_video_content(self):
        video_info = []
        def extract_hrefs(url):
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
        # Make video info ordered. So we can get the most recent video first, and make a break on the oldest
        # self.page.close()
        print("VIDEO INFO IS:", video_info)
        for href, title in video_info:
            yield {"title": title, "href": href}

    def scrape_videos_by_date(self, start_date :  datetime, end_date : datetime):
        filtered_videos = {}
        def requests_seletion(response, find_term, configs : str):
            if type(find_term) == list:
                find_term = find_term[0] if response.text.find(find_term[0]) != -1 else find_term[1]
                begin = response.text.find(find_term)
                end = response.text[begin:].find(configs) + begin
                result = response.text[begin:end]
                result = str(result.replace('"', '')).removeprefix(find_term.replace('"', ''))
                return result
            begin = response.text.find(find_term)
            end = response.text[begin:].find(configs) + begin
            result = response.text[begin:end]
            result = str(result.replace('"', '')).removeprefix(find_term.replace('"', ''))
            return result
        for video in self.get_video_content():
            self.set_url(video['href'])
            print()
            response = requests.get(self.current_url, headers=self.headers)
            processed_date = requests_seletion(response, list(['"startTimestamp":', '"uploadDate":']), ",")
            processed_date = datetime.fromisoformat(processed_date.strip().strip('}')).replace(tzinfo=None)
            comments = requests_seletion(response, '"contextualInfo":', ",")
            likes = requests_seletion(response, '"likeCount":', ",")
            views = requests_seletion(response, '"views":', ",")
            comments = re.findall(r"\d+", comments)
            views = re.findall(r"\d+(?:[\.,]\d+)?", views)
            if processed_date > end_date:
                continue
            if processed_date < start_date:
                break
            filtered_videos[video['href']] = {"title": video['title'], 
                                         "date": processed_date, 
                                         "likes" : likes, 
                                         "comments" : comments[0] if comments != [] else 0, 
                                         "views" : views[0] if views != [] else 0
            }             
        print("Total de vídeos filtrados:", len(filtered_videos))
        print(filtered_videos)
        return filtered_videos

    def standard_procedure(self, dates: list):
        if self.browser == None: 
            self.start_browser_user()
        data = self.scrape_videos_by_date(dates[0], dates[1])
        # self.stop_browser()
        return data
    











# //button[@class="yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-leading yt-spec-button-shape-next--segmented-start yt-spec-button-shape-next--enable-backdrop-filter-experiment"]//div[@class="yt-spec-button-shape-next__button-text-content"]



    # def get_data(self, initial_data = None, final_data = None):
    #     all_videos = {}
    #     for video in self.get_video_content():
    #         self.set_url(video['href'])
    #         self.page.goto(self.current_url, timeout=30000)
    #         self.page.wait_for_selector('//div[@id="description"]//tp-yt-paper-button[@id="expand"]')
    #         self.page.locator('//div[@id="description"]//tp-yt-paper-button[@id="expand"]').click()
    #         self.page.wait_for_selector('(//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"])[3]')
    #         date_ = self.page.locator('(//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"])[3]')
    #         date = date_.inner_text().split(" ")
    #         remove = ["Estreou", "em", "de"]
    #         date = list(filter(lambda x: x not in remove, date))
    #         locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    #         date = " ".join(date).replace(".", "")
    #         extract_date = datetime.strptime(date, "%d %b %Y")
    #         if extract_date > initial_data and extract_date < final_data :
    #             all_videos[video['href']] = {"title": video['title'], "date": extract_date}
    #             print('passei no if')
    #             continue
    #         break
    #     return all_videos



    # findTerm = '"startTimestamp":' if response.text.find('"startTimestamp":') != -1 else '"uploadDate":'
            # like_count = response.text.find('"likeCount":')
            # end_like = response.text[like_count:].find(",") + like_count
            # likes = response.text[like_count:end_like]
            # print(">>>>>>>> LIKES", likes)
            # comments = response.text.find('"contextualInfo":')

            # print("FIND TERM IS:" , findTerm)
            # begin = response.text.find(findTerm)
            # end = response.text[begin:].find(",") + begin
            # result = response.text[begin:end]
            # print(f"begin: {begin} end: {end} RESULT IS: ", result)
            # date = str(date.replace('"', '')).removeprefix(findTerm.replace('"', ''))
            # print("Result", result)
            # processed_date = datetime.fromisoformat(result[0:-6])
            # processed_date = processed_date.strftime('%d/%m/%Y')
            # print("processed", processed_date)
            # end_date = datetime.fromisoformat(end_date)
            # print("end date", end_date)
            # print("start date", start_date)