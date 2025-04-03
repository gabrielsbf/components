from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime, timezone


class Twitter_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.x.com/")

    # def get_href(self, since: datetime, until: datetime = None):
    #     if not self.page:
    #             raise Exception("Browser or page not initialized. Call start_browser() first.")
    #     self.set_url(self.current_url + 'NiteroiPref')
    #     self.page.goto(self.current_url, timeout=30000)
    #     self.page.wait_for_load_state('domcontentloaded', timeout=30000)
    #     self.page.wait_for_selector("//section[@class='css-175oi2r']", timeout=10000)
    #     self.page.wait_for_timeout(5000)
    #     feed = self.page.locator('//section[@class="css-175oi2r"]')
        
    #     since = datetime.strptime(since, "%d/%m/%Y")  
    #     while last_date > since:
    #         self.page.mouse.wheel(0, 1000)
    #         self.page.wait_for_timeout(2000)
    #         times = feed.locator('//time').all()
    #         if not times:
    #             print("Nenhuma tag encontrada")
    #             break
    #         last_datetime_str = times[-1].get_attribute("datetime")
    #         last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
    #         print(f"Ultima data", last_date)
    #     print('all datas')
            



    def get_href(self, since: str, until: str):
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        
        self.set_url(self.current_url + 'NiteroiPref')
        self.page.reload()
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_selector("//section[@class='css-175oi2r']", timeout=30000)
        self.page.wait_for_timeout(5000)

        feed = self.page.locator('//section[@class="css-175oi2r"]')

        since = datetime.strptime(since, "%d/%m/%Y").replace(tzinfo=timezone.utc)
        until = datetime.strptime(until, "%d/%m/%Y").replace(tzinfo=timezone.utc) 

        last_date = datetime.now(timezone.utc)  
        links_filtrados = []

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
                        link_href = links[i].get_attribute("href") if i < len(links) else None
                        if link_href:
                            links_filtrados.append((last_date, link_href))
                            print(f"Link adicionado: {link_href}")

            if last_date < since:
                break

        print("Links filtrados:", links_filtrados)
        return links_filtrados



             
        # # items = feed.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
        # times = feed.locator('//time')     
        # # if items.count() == 0:
        # #      raise Exception("Nada encontrado")
        # # hrefs = [item.get_attribute("href") for item in items.all() if item.get_attribute("href")]
        # time_values = [t.get_attribute("datetime") for t in times.all() if t.get_attribute("datetime")]
        # print(time_values)

    def standard_procedure(self):
        self.start_browser_user()
        data = self.get_href('01/03/2025', '31/03/2025' )
        self.stop_browser()