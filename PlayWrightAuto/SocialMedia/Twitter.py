from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime, timezone


class Twitter_Automation(PlayEssencial):
    def __init__(self, account, browser_data_path=None, chrome_executable_path=None):
        self.account = account
        super().__init__(f"www.x.com/{self.account}", browser_data_path, chrome_executable_path)

    def get_href(self, since: str, until: str):
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        
        self.set_url(self.current_url + 'NiteroiPref')
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_selector("//section[@class='css-175oi2r']", timeout=30000)
        self.page.wait_for_timeout(5000)
        feed = self.page.locator('//div[@class="css-175oi2r r-150rngu r-16y2uox r-1wbh5a2 r-rthrr5"]')
        count = feed.count()
        print(f"Total de posts encontrados: {count}")
        since = datetime.strptime(since, "%d/%m/%Y").replace(tzinfo=timezone.utc)
        until = datetime.strptime(until, "%d/%m/%Y").replace(tzinfo=timezone.utc).replace(hour=23, minute=59, second=59)
        last_date = datetime.now(timezone.utc)  
        links_filtrados = []

        while last_date >= since:
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(500)
            posts = feed.locator("//article")
            count = posts.count()
            # print(f"Total de posts encontrados loop: {count}")
            last_post = posts.nth(count -1)
            # print("last_post is", last_post)
            access_date = last_post.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            for i in range(count):
                post = posts.nth(i)
                access_date = post.locator("//div[@class='css-175oi2r']//div[@class='css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-1udbk01 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim']//span[@class='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3']")
                all_desc = access_date.all()
                post_descs = "".join([desc.inner_text().replace("\n", "") for desc in all_desc])
                access_date = post.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
                get_href = access_date.get_attribute("href")
                if get_href in [list(link.keys())[0] for link in links_filtrados]:
                    print("ja existe")
                    continue
                else:
                    if last_datetime_str:
                        last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
                        if since <= last_date <= until:
                            links_filtrados.append(({get_href : {'Descrição' : post_descs, 'Data' : last_date.strftime("%d/%m/%Y %H:%M:%S")}}))
                            print(f"Link adicionado: {get_href}")
                                    
                        elif last_date < since:
                            print("Ultima data menor que a data inicial", since, "Ultima data", last_date)
                            break
        print("Links filtrados:", links_filtrados)
        return links_filtrados

    def standard_procedure(self, dates: list[datetime]):
        self.start_browser_user()
        data = self.get_href(dates[0], dates[1])
        self.stop_browser()
        return data