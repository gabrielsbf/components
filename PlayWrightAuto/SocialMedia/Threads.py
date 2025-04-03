from components.PlayWrightAuto.essencial import PlayEssencial
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
        input()
        while last_date >= since:
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(2000)

            times = feed.locator('//time').all()
            links = feed.locator('//a').all()  

            print(f"Encontrados {len(times)} elementos <time>.")

            for i, time_element in enumerate(times):
                last_datetime_str = time_element.get_attribute("datetime")
                if last_datetime_str:
                    last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
                    print(f"Data encontrada: {last_date}")

                    if since <= last_date <= until:
                        link_href = links[i].get_attribute("href") 
                        if link_href == '/@niteroipref':
                            del link_href
                        else:
                            links_filtrados.append((last_date, link_href))
                            print(f"Link adicionado: {link_href}")

            if last_date < since:
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
            self.start_browser()
            data = self.get_href("01/03/2025", "31/03/2025")
            self.stop_browser()