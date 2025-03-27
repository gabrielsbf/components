from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime
import locale


class Youtube_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.youtube.com/")
    
    def get_href(self):
        print("passei no get_href")
        if not self.page:
                raise Exception("Browser or page not initialized. Call start_browser() first.")
        self.set_url(self.current_url + 'PrefeituradeNiter%C3%B3iOficial/videos')
        self.page.goto(self.current_url, timeout=30000)
        hrefs = self.page.eval_on_selector_all('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]', '(links) => links.map(link => link.href)')
        titles = self.page.eval_on_selector_all('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]', '(links) => links.map(link => link.title)')
        for href, title in zip(hrefs, titles):
            yield {"title": title, "href": href}
      
    
    def get_data(self, initial_data = None, final_data = None):
        all_videos = {}
        for video in self.get_href():
            self.set_url(video['href'])
            self.page.goto(self.current_url, timeout=30000)
            self.page.wait_for_selector('//div[@id="description"]//tp-yt-paper-button[@id="expand"]')
            self.page.locator('//div[@id="description"]//tp-yt-paper-button[@id="expand"]').click()
            self.page.wait_for_selector('(//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"])[3]')
            date_ = self.page.locator('(//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"])[3]')
            date = date_.inner_text().split(" ")
            remove = ["Estreou", "em", "de"]
            date = list(filter(lambda x: x not in remove, date))
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            date = " ".join(date).replace(".", "")
            extract_date = datetime.strptime(date, "%d %b %Y")
            if extract_date > datetime.strptime(initial_data, "%d/%m/%Y") and extract_date < datetime.strptime(final_data, "%d/%m/%Y") :
                all_videos[video['href']] = {"title": video['title'], "date": extract_date.strftime("%d/%m/%Y")}
                print('passei no if')
                continue
            break
        print(all_videos)
        return all_videos
    
    def standard_procedure(self):
        self.start_browser()
        data = self.get_data("01/03/2025", "31/03/2025")
        self.stop_browser()
        return data
    
