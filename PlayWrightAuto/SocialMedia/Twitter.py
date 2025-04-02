from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime
import locale


class Twitter_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.x.com/")

    def get_href(self, since: datetime, until: datetime = None):
        if not self.page:
                raise Exception("Browser or page not initialized. Call start_browser() first.")
        self.set_url(self.current_url + 'NiteroiPref')
        self.page.goto(self.current_url, timeout=30000)
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)
        self.page.wait_for_selector("//section[@class='css-175oi2r']", timeout=10000)
        self.page.wait_for_timeout(5000)
        feed = self.page.locator('//section[@class="css-175oi2r"]')
        if isinstance(since, str):
            since = datetime.strptime(since, "%d/%m/%Y")  
        while last_date > since:
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(2000)
            times = feed.locator('//time').all()
            if not times:
                print("Nenhuma tag encontrada")
                break
            last_datetime_str = times[-1].get_attribute("datetime")
            last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
            print(f"Ultima data", last_date)
        print('all datas')
            

             
        # # items = feed.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
        # times = feed.locator('//time')     
        # # if items.count() == 0:
        # #      raise Exception("Nada encontrado")
        # # hrefs = [item.get_attribute("href") for item in items.all() if item.get_attribute("href")]
        # time_values = [t.get_attribute("datetime") for t in times.all() if t.get_attribute("datetime")]
        # print(time_values)

    def standard_procedure(self):
        self.start_browser()
        data = self.get_href('01/03/2025')
        self.stop_browser()