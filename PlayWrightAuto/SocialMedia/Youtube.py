from components.PlayWrightAuto.essencial import PlayEssencial
import pandas as pd
from datetime import datetime
import locale


class Youtube_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.youtube.com/")
    
    def get_href(self):
        if not self.page:
                raise Exception("Browser or page not initialized. Call start_browser() first.")
        self.set_url(self.current_url + 'PrefeituradeNiter%C3%B3iOficial/videos')
        self.page.goto(self.current_url, timeout=30000)
        self.page.wait_for_selector('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]')
        links = self.page.locator('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]')
        video_list = []
        for i in range(2):
                print('entrei no for')
                href = links.nth(i).get_attribute("href")
                name = links.nth(i).inner_text()
                video_list.append({'link' : "https://www.youtube.com" + href, 'name' : name})
        return video_list
    
    def get_data(self):
        videos_data = self.get_href()
        for href in videos_data:
            self.set_url(href.get("link"))
            self.page.goto(self.current_url + href.get("link"), timeout=30000)
            self.page.wait_for_selector('//div[@id="description"]//tp-yt-paper-button[@id="expand"]')
            self.page.locator('//div[@id="description"]//tp-yt-paper-button[@id="expand"]').click()
            self.page.wait_for_selector('(//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"])[3]')
            date_ = self.page.locator('(//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"])[3]')
            date = date_.inner_text().split(" ")
            remove = ["Estreou", "em", "de"]
            date = list(filter(lambda x: x not in remove, date))
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            date = " ".join(date).replace(".", "")
            print(date)
            href["date"] = datetime.strptime(date, "%d %b %Y")
        return videos_data
    
    def standard_procedure(self):
        self.start_browser()
        data = self.get_data()
        self.stop_browser()
        return data
    
    def save_data(self):
        data = self.standard_procedure()
        df = pd.DataFrame(data)
        print(df)