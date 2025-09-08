from components.PlayWrightAuto.essencial import PlayEssencial
from components.PlayWrightAuto.locators import *
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Threads_Automation(PlayEssencial):
    def __init__(self, account, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
        self.account = account
        super().__init__(f'https://www.threads.net/{self.account}', playwright, browser_data_path, chrome_executable_path, browser, page)

    
         
    def get_href(self, since: str | datetime, until: str | datetime) -> list[dict]:
        def convert_text_to_metrics(metrics_text: list) -> dict:
            metrics_dict = {}
            metrics_dict['Curtidas'] = metrics_text[0] if metrics_text[0] != '' else 0
            metrics_dict['Comentários'] = metrics_text[1] if len(metrics_text) > 1 and metrics_text[1] != '' else 0
            metrics_dict['Repostados'] = metrics_text[2] if len(metrics_text) > 2 and metrics_text[2] != '' else 0
            metrics_dict['Compartilhamentos'] = metrics_text[3] if len(metrics_text) > 3 and metrics_text[3] != '' else 0
            return metrics_dict
        
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        self.set_url(self.current_url)
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_timeout(5000)
        feed = self.page.safeLocator(THREADS_FEED, "Feed dos Posts - Geral")
        count = feed.count()
        since = since if type(since) == datetime else datetime.strptime(since, "%d/%m/%Y")
        until = until if type(until) == datetime else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
        last_date = datetime.now()  
        filtered_posts = []
        while last_date >= since:
            logger.info("Scrolling to load more posts...")
            self.page.mouse.wheel(0, 1000)
            self.page.wait_for_timeout(500)
            posts = feed.safeLocator(THREADS_FEED_POST, "Posts Individuais -> De forma geral")
            count = posts.count()
            last_post = posts.nth(count - 1)
            access_date = last_post.locator('//time')
            last_datetime_str = access_date.get_attribute("datetime")
            if last_datetime_str:
                    last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                    if last_date < since:
                        break
        posts = feed.safeLocator(THREADS_FEED_POST, "Posts Individuais -> De forma geral")
        count = posts.count()
        for i in range(count):
            post = posts.nth(i)
            metrics = post.safeLocator(THREADS_METRICS, "Métricas do Threads").all_inner_texts()
            href = post.safeLocator(THREADS_POST_HREF, "link do Threads").get_attribute("href")
            description = post.safeLocator(THREADS_DESCRIPTION, "Descrição do Post")
            if description.count() > 0:
                 description = description.text_content()
            else:
                 description = "Sem descrição"
            metrics = convert_text_to_metrics(metrics)
            last_datetime_str = post.safeLocator("//time", "Última data de Todos os Posts - Comparação").get_attribute("datetime")
            logger.info(f"Post {i+1}/{count} - Link: {href} - Date: {last_datetime_str} - Metrics: {metrics} - Description: {description}\n\n")
            if last_datetime_str:
                last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                if since <= last_date <= until:
                    filtered_posts.append((
                    {href : {'Descrição' :  description, 
                    'Data' : last_date.strftime("%d/%m/%Y %H:%M:%S"), 
                    'Curtidas' : metrics.get('Curtidas', 0),
                    'Comentários' : metrics.get('Comentários', 0),
                    'Visualizações' : metrics.get('Visualizações', 0),
                    'Repostados' : metrics.get('Repostados', 0),
                    'Compartilhamentos' : metrics.get('Compartilhamentos', 0),}}
                    )) 
                elif last_date < since:
                    break
        input("Pressione Enter para continuar...")
        return filtered_posts


    def standard_procedure(self, dates:list[datetime])-> list[dict]:
            if self.browser == None: 
                self.start_browser_user()
            data = self.get_href(dates[0], dates[1])
            self.stop_browser()
            return data