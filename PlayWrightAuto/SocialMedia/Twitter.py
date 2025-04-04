from components.PlayWrightAuto.essencial import PlayEssencial
from datetime import datetime, timezone


class Twitter_Automation(PlayEssencial):
    def __init__(self):
        super().__init__("https://www.x.com/")

    def get_href(self, since: str, until: str):
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        
        self.set_url(self.current_url + 'NiteroiPref')
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_selector("//section[@class='css-175oi2r']", timeout=30000)
        self.page.wait_for_timeout(5000)
        feed = self.page.locator('//section[@class="css-175oi2r"]')
        count = feed.count()
        print(f"Total de posts encontrados: {count}")
        since = datetime.strptime(since, "%d/%m/%Y").replace(tzinfo=timezone.utc)
        until = datetime.strptime(until, "%d/%m/%Y").replace(tzinfo=timezone.utc)
        last_date = datetime.now(timezone.utc)  
        links_filtrados = []

        while last_date >= since:
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(500)
            posts = feed.locator("//article[@class='css-175oi2r r-18u37iz r-1udh08x r-1c4vpko r-1c7gwzm r-o7ynqc r-6416eg r-1ny4l3l r-1loqt21']")
            count = posts.count()
            print(f"Total de posts encontrados loop for: {count}")
            last_post = posts.nth(count - 1)
            access_date = last_post.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            if last_datetime_str:
                    print("last datetime str is", last_datetime_str)
                    last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
                    print(f"Ultima data encontrada: {last_date}")
                    if last_date < since:
                        break
        posts = feed.locator("//article[@class='css-175oi2r r-18u37iz r-1udh08x r-1c4vpko r-1c7gwzm r-o7ynqc r-6416eg r-1ny4l3l r-1loqt21']")
        count = posts.count()           
        print(f">>>>>>>>Total de posts encontrados: {count}")  
        for i in range(count):
            print('passei aqui')
            print("i is", i)
            post = posts.nth(i)
            access_date = post.locator("//div[@class='css-175oi2r']//div[@class='css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-1udbk01 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim']//span[@class='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3']")
            all_desc = access_date.all()
            post_descs = "".join([desc.inner_text().replace("\n", "") for desc in all_desc])    
            #     print("desc is>", desc.inner_text().split(" "))
            #     desc =  " ".join(desc.inner_text().split(" "))
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>desc is", desc)




            # print("access desc is.", access_desc.count())
            print('passei aqui')
            access_date = post.locator('//a[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"]')
            print("href is.", access_date.get_attribute("href"))
            # print("access desc is.", access_desc.inner_text())
            # if access_desc.count() > 0:
            #     desc = access_desc.text_content()
            # else:
            #     desc = "Sem descrição"
            last_datetime_str = access_date.locator("time").get_attribute("datetime")
            if last_datetime_str:
                last_date = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00"))
                print(f"Data encontrada: {last_date}")
                if since <= last_date <= until:
                    link_href = access_date.get_attribute("href")
                    links_filtrados.append(({link_href : {'Descrição' : post_descs, 'Data' : last_date.strftime("%d/%m/%Y %H:%M:%S")}}))
                    print(f"Link adicionado: {link_href}")
                
                elif last_date < since:
                    break
        
        print("Links filtrados:", links_filtrados)
        return links_filtrados


             


    def standard_procedure(self):
        self.start_browser_user()
        data = self.get_href('01/04/2025', '04/04/2025' )
        self.stop_browser()