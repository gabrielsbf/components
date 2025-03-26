from components.PlayWrightAuto.essencial import PlayEssencial

class Tiktok_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://tiktok.com/@niteroipref")


    def iterate_video_links(self, result_info: dict):
        for key, _ in result_info.items():
            yield key

    def access_videos(self, result_info: dict):
        for link in self.iterate_video_links(result_info):
            self.current_url = link
            self.page.goto(self.current_url, timeout=30000)
            # dados = self.page.evaluate('''() => {
            #     if (window.webapp && window.webapp.videoDetail && window.webapp.videoDetail.itemInfo) {
            #         const itemInfo = window.webapp.videoDetail.itemInfo.itemStruct;
            #         return {
            #             id: itemInfo.id,
            #             desc: itemInfo.desc,
            #             createTime: itemInfo.createTime
            #         };
            #     }
            #     return null;
            # }''')
            self.page.on()
            print("DADOS IS: ", dados)

    def get_feed_info(self):
            result_info = {}
            if not self.page:
                raise Exception("Browser or page not initialized. Call start_browser() first.")
            self.page.goto(self.current_url, timeout=30000)
            input()
 
      
            self.page.wait_for_load_state("domcontentloaded",timeout=30000)

            self.page.wait_for_selector("//div[@id='main-content-others_homepage']")
            feed = self.page.locator("//div[@id='main-content-others_homepage']")
            items = feed.locator('//div[@class="css-1uqux2o-DivItemContainerV2 e19c29qe7"]')
            views = self.page.locator('//div[@class="css-1qb12g8-DivThreeColumnContainer eegew6e2"]//strong[@class="video-count css-dirst9-StrongVideoCount e148ts222"]')
            count = items.count()
            for i in range(count):
                item = items.nth(i)
                result_info[item.locator("a").get_attribute("href")] = {"desc": item.locator("img").get_attribute("alt"), 'views' : views.nth(i).inner_text()}
            return result_info

    def standard_procedure(self):
         self.start_browser()
         data = self.get_feed_info()
         self.access_videos(data)
         self.stop_browser()
         print(data)