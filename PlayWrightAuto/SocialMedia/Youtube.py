from components.PlayWrightAuto.essencial import PlayEssencial

class Youtube_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.youtube.com/")

    def get_info(self):
        # url = self.set_url("https://www.youtube.com/c/PrefeituradeNiter%C3%B3iOficial/videos")
        # self.start_browser()
        if not self.page:
                raise Exception("Browser or page not initialized. Call start_browser() first.")
        self.page.goto(self.current_url + 'PrefeituradeNiter%C3%B3iOficial/videos', timeout=30000)

        self.page.wait_for_selector('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]')

        prev_count = 0
        while True:
            self.page.mouse.wheel(0, 1000)  
            self.page.wait_for_timeout(1000)  

            videos = self.page.locator('//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]')
            if videos.count() == prev_count:  
                break
            prev_count = videos.count()
        href_list = []
        for i in range(videos.count()):
            href = videos.nth(i).get_attribute("href")
            name = videos.nth(i).inner_text()
            href_list.append(href)
        print("fim")
        return href_list
    
    
    def get_data(self):
        href_list = self.get_info()
        for href in href_list:

            if not self.page:
                    raise Exception("Browser or page not initialized. Call start_browser() first.")
            self.page.goto(self.current_url + href, timeout=30000)
            self.page.wait_for_selector('//div[@id="description"]//tp-yt-paper-button[@id="expand"]')

            self.page.locator('//div[@id="description"]//tp-yt-paper-button[@id="expand"]').click()

            self.page.wait_for_selector('//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"]')

            videos = self.page.locator('//div[@id="info-container"]//span[@class="style-scope yt-formatted-string bold"]')
            for i in range(videos.count()):
                name = videos.nth(i).inner_text()
                print(name)
# //div[@id="description"]//tp-yt-paper-button[@id="expand"]
         
    
    def standard_procedure(self):
        self.start_browser()
        data = self.get_data()
        self.stop_browser()
        
        # result_info = {}
        # return result_info
    
