from components.PlayWrightAuto.essencial import PlayEssencial

class Tiktok_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://tiktok.com/@niteroipref")

    def get_feed_info(self):
            result_info = {}
            if not self.page:
                raise Exception("Browser or page not initialized. Call start_browser() first.")
            self.page.goto(self.current_url, timeout=30000)
            input()
            dados = self.page.evaluate('''() => {
            if (window.webapp && window.webapp.videoDetail && window.webapp.videoDetail.itemInfo) {
                const itemInfo = window.webapp.videoDetail.itemInfo.itemStruct;
                return {
                    id: itemInfo.id,
                    desc: itemInfo.desc,
                    createTime: itemInfo.createTime
                };
            }
            return null;
        }''')
      
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
         self.stop_browser()
         print(data)