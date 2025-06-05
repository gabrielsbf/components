from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime, timezone



class Threads_Automation(PlayEssencial):
    def __init__(self, account, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
        self.account = account
        super().__init__(f'https://www.threads.net/{self.account}', playwright, browser_data_path, chrome_executable_path, browser, page)

    def get_href(self, since: str | datetime, until: str | datetime):
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        
        self.set_url(self.current_url)
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_selector('//div[@aria-label="Corpo da coluna"]', timeout=30000)
        self.page.wait_for_timeout(5000)
        feed = self.page.locator('//div[@class="x1a2a7pz x1n2onr6"]')  
        
        count = feed.count()
        # print(f"Total de posts encontrados: {count}")
        since = since if type(since) == datetime else datetime.strptime(since, "%d/%m/%Y")
        until = until if type(until) == datetime else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
        # print("since is", until)

        last_date = datetime.now()  
        links_filtrados = []
        # datas = []
        while last_date >= since:
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(500)
            posts = feed.locator('//div[@class="xrvj5dj xd0jker x1evr45z"]')
            count = posts.count()
            last_post = posts.nth(count - 1)
            access_date = last_post.locator('//div[@class="x78zum5 x1c4vz4f x2lah0s"]//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1lku1pv x12rw4y6 xrkepyr x1citr7e x37wo2f"]')
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            if last_datetime_str:
                    last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                    if last_date < since:
                        break
        posts = feed.locator('//div[@class="xrvj5dj xd0jker x1evr45z"]')
        count = posts.count()
        # print(f"Total de posts encontrados: {count}")
        for i in range(count):
            post = posts.nth(i)
            access_date = post.locator('//div[@class="x78zum5 x1c4vz4f x2lah0s"]//a[@class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1lku1pv x12rw4y6 xrkepyr x1citr7e x37wo2f"]')
            # print("href is.", access_date.get_attribute("href"))
            access_desc = post.locator('//div[@class="x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7"]')
            access_comp = post.locator('//div[@class="x6s0dn4 xfkn95n xly138o xchwasx xfxlei4 x78zum5 xl56j7k x1n2onr6 x3oybdh xx6bhzk x12w9bfk x11xpdln xc9qbxq x14qfxbe"]').all_inner_texts()
            access_metrics = post.locator('//div[@class="x6s0dn4 xfkn95n xly138o xchwasx xfxlei4 x78zum5 xl56j7k x1n2onr6 x3oybdh xx6bhzk x12w9bfk x11xpdln xc9qbxq x1ye3gou xn6708d x14atkfc"]').all_inner_texts()
            # print("access desc is.", access_desc.count())
            # print('passei aqui')
            if access_desc.count() > 0:
                desc = access_desc.text_content()
            else:
                desc = "Sem descrição"
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            # print(">>>>>>>>>>>>>>>>", desc[:-9])
            if last_datetime_str:
                last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                # print(f"Data encontrada: {last_date}")
                if since <= last_date <= until:
                    link_href = access_date.get_attribute("href")
                    links_filtrados.append(({link_href : {'Descrição' :  desc[:-9], 
                                                          'Data' : last_date.strftime("%d/%m/%Y %H:%M:%S"), 
                                                          'Curtidas' : access_metrics[0] if access_metrics[0] != '' else 0, 
                                                          'Comentários' : access_metrics[1] if access_metrics[1] != '' else 0, 
                                                          'Repostados' : access_metrics[2] if access_metrics[2] != '' else 0, 
                                                          'Compartilhamentos' : access_metrics[3] if len(access_metrics) > 3 else 0}}))
                    # datas.append(last_date.strftime("%d/%m/%Y %H:%M:%S"))
                    # print(f"Link adicionado: {link_href}")
                
                elif last_date < since:
                    break
        
        print("Total de posts filtrados:", len(links_filtrados))
        print("Links filtrados:", links_filtrados)
        # print("Datas filtradas:", datas)
        return links_filtrados


    def standard_procedure(self, dates:list[datetime]):
            self.start_browser_user()
            data = self.get_href(dates[0], dates[1])
            self.stop_browser()
            return data