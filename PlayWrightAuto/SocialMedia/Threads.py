from components.PlayWrightAuto.essencial import PlayEssencial, sync_playwright
from datetime import datetime, timezone



class Threads_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.threads.net/")

    def get_href(self, since: str, until: str):
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        
        self.set_url(self.current_url + '@niteroipref?hl=pt-br')
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_selector('//div[@aria-label="Corpo da coluna"]', timeout=30000)
        self.page.wait_for_timeout(5000)
        feed = self.page.locator('//div[@class="x1a2a7pz x1n2onr6"]')  
        
        count = feed.count()
        print(f"Total de posts encontrados: {count}")
        since =  datetime.strptime(since, "%d/%m/%Y").replace(tzinfo=timezone.utc)
        until =  datetime.strptime(until, "%d/%m/%Y").replace(tzinfo=timezone.utc)

        last_date = datetime.now(timezone.utc)  
        links_filtrados = []
        while last_date >= since:
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(2000)
            posts = feed.locator('//div[@class="xrvj5dj xd0jker x1evr45z"]')
            count = posts.count()
            last_post = posts.nth(count - 1)
            access_date = last_post.locator('//div[@class="x78zum5 x1c4vz4f x2lah0s"]//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1lku1pv x12rw4y6 xrkepyr x1citr7e x37wo2f"]')
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            if last_datetime_str:
                    last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
                    if last_date < since:
                        break
        posts = feed.locator('//div[@class="xrvj5dj xd0jker x1evr45z"]')
        count = posts.count()
        for i in range(count):
            post = posts.nth(i)
            access_desc = post.locator('//div[@class="x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7"]//span')
            
            access_date = post.locator('//div[@class="x78zum5 x1c4vz4f x2lah0s"]//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1lku1pv x12rw4y6 xrkepyr x1citr7e x37wo2f"]')
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            desc = access_desc.inner_text()
            print(">>>>>>>>>>>>>>>>", access_desc)
            if last_datetime_str:
                last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
                print(f"Data encontrada: {last_date}")
                if since <= last_date <= until:
                    link_href = access_date.get_attribute("href")
                    links_filtrados.append((last_date, link_href, desc))
                    print(f"Link adicionado: {link_href}")

                elif last_date < since:
                    break
            
        print("Links filtrados:", links_filtrados)
        return links_filtrados


        # for i in range(count):
        #     post = feed.nth(i)
        #     hrefs = post.locator('a').all()
        #     timestamps = post.locator('time').all()  
        #     post_time = timestamps[0].get_attribute("datetime") if timestamps else "Sem timestamp"
            
        #     for link in hrefs:
        #         url = link.get_attribute("href")
        #         print(f"Post {i + 1}: {url} | Data: {post_time}")

        # print("Feito")


    def standard_procedure(self):
            # self.start_browser()
            self.start_browser_user()

            data = self.get_href("25/03/2025", "31/03/2025")
            self.stop_browser()