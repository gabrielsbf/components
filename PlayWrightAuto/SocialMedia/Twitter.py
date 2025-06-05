from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime, timezone


class Twitter_Automation(PlayEssencial):
    def __init__(self, account, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
        self.account = account
        super().__init__(f"https://www.x.com/{self.account}", playwright, browser_data_path, chrome_executable_path, browser, page)

    def get_href(self, since: str, until: str):
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        
        self.set_url(self.current_url)
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_selector("//section[@class='css-175oi2r']", timeout=30000)
        self.page.wait_for_timeout(5000)
        feed = self.page.locator('//div[@class="css-175oi2r r-150rngu r-16y2uox r-1wbh5a2 r-rthrr5"]')
        count = feed.count()
        print(f"Total de posts encontrados: {count}")
        since = since if type(since) == datetime else datetime.strptime(since, "%d/%m/%Y")
        until = until if type(until) == datetime else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
        last_date = datetime.now()  
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
                full_post = "//div[@class='css-175oi2r r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu']"
                access_metrics = post.locator("//div[@class='css-175oi2r r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu']//div[@class='css-175oi2r r-18u37iz r-1h0z5md r-13awgt0']").all_inner_texts()
                access_desc = post.locator(f"{full_post}//div[@class='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim']")
                all_desc = access_desc.all()
                post_descs = "".join([desc.inner_text().replace("\n", "") for desc in all_desc])
                access_date = post.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
                get_href = access_date.get_attribute("href")
                if get_href in [list(link.keys())[0] for link in links_filtrados]:
                    print("ja existe")
                    continue
                else:
                    if last_datetime_str:
                        last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                        if since <= last_date <= until:
                            links_filtrados.append(({get_href : 
                                                     {'Descrição' : post_descs, 
                                                      'Data' : last_date.strftime("%d/%m/%Y %H:%M:%S"), 
                                                      'Comentários' : access_metrics[0] if access_metrics[0] != '' else 0 , 
                                                      'Compartilhamentos' :  access_metrics[1] if access_metrics[1] != '' else 0, 
                                                      'Curtidas' :  access_metrics[2] if access_metrics[2] != '' else 0, 
                                                      'Visualizações' :  access_metrics[3] if access_metrics[3] != '' else 0}}))
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