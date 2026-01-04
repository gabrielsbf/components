from components.PlayWrightAuto.essencial import PlayEssencial
from components.PlayWrightAuto.locators import *
from datetime import datetime
import logging
import re



logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Twitter_Automation(PlayEssencial):
    def __init__(self, account, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
        self.account = account
        super().__init__(f"https://www.x.com/{self.account}", playwright, browser_data_path, chrome_executable_path, browser, page)

    def collect_filtered_post_links(self, start_date :  datetime, end_date : datetime)-> list[dict]:
        """
            Collects links and post data published between two dates on an X (formerly Twitter) page.

            This method scrolls through the user's timeline to dynamically load posts. 
            For each post found within the specified date range, it extracts:
            - post URL
            - tweet text (with whitespace cleaned)
            - publication date
            - engagement metrics: replies, reposts, likes, and views

            Parameters:
            ----------
            data_inicio : datetime
                The minimum post date to include.
            data_fim : datetime
                The maximum post date to include.

            Returns:
            -------
            List[Dict[str, Dict]]
                A list of dictionaries where each item has the post URL as the key, 
                and the associated metadata as the value.
        """
        def convert_text_to_metrics(metrics_text : str)-> dict:
                pattern = r"(\d+)\s+(respostas?|repost|curtidas?|visualizações)"
                matches = re.findall(pattern, metrics_text)
                metrics_dict = {}
                for value, key in matches:
                    if not key.endswith('s'):
                        key += 's'
                    key = key.lower()
                    metrics_dict[key] = int(value)
                return metrics_dict
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")
        self.set_url(self.current_url)
        self.page.goto(self.current_url, timeout=50000)
        self.page.wait_for_load_state('domcontentloaded', timeout=50000)
        self.page.wait_for_timeout(5000)
        feed_container = self.page.safeLocator(TWITTER_FEED_CONTAINER, "Container de Feed do Twitter")
        logger.info('Iniciando coleta de posts...')
        total_posts = feed_container.count()
        processed_hrefs = set()
        filtered_posts = []
        continue_collecting = True
        while continue_collecting:
            self.page.mouse.wheel(0, 2000)
            self.page.wait_for_timeout(500)
            posts = feed_container.safeLocator('//article', "Posts do Twitter")
            total_posts = posts.count()
            if total_posts == 0:
                logger.info('Saindo do loop')
                break

            for i in range(total_posts):
                post = posts.nth(i)
                engagement_summary_str = post.safeLocator(TWITTER_METRICS, "Twitter -> Métricas do Post").get_attribute("aria-label") if post.locator(TWITTER_METRICS).count() > 0 else None
                # element = post.safeLocator(TWITTER_POST_HREF, "Twitter -> Link do Post")
                datetime_str = post.safeLocator("time", "Data do Post") if post.locator("time").count() > 0 else None
                try: datetime_str =  datetime_str.get_attribute("datetime") if datetime_str else None
                except: datetime_str = datetime_str
                post_datetime = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ") if datetime_str else "Sem data"
                post_url = post.safeLocator(TWITTER_POST_HREF, "Twitter -> HREF Posts").get_attribute("href")
                if post_url in processed_hrefs:
                    continue
                processed_hrefs.add(post_url)          
                post_metrics = convert_text_to_metrics(engagement_summary_str) if engagement_summary_str else {}
                post_decription = post.safeLocator(TWITTER_DESCRIPTION, "Twitter -> Descrição do Post").inner_text() if post.locator(TWITTER_DESCRIPTION).count() > 0 else "Sem descrição"
                post_decription = re.sub(r'\s+', ' ', post_decription).strip() if post_decription else "Sem descrição"

                if type(post_datetime) != str and post_datetime < start_date:
                    continue_collecting = False
                    logger.info(f"Post de {post_datetime} está antes de {start_date}. Encerrando busca.")
                    break
                if type(post_datetime) != str and post_datetime >  end_date:
                    continue
                logger.debug(f"Data do post: {post_datetime}")
                logger.debug(f"Link encontrado: {post_url}")
                logger.debug(f"Descrição do post: {post_decription}")
                logger.debug(f"Métricas do post: {engagement_summary_str}")
                logger.debug(f"Métricas convertidas: {post_metrics}")
                filtered_posts.append(({f"https://www.x.com{post_url}" : 
                                            {'Descrição' : post_decription, 
                                            'Data' : post_datetime, 
                                            'Comentários' : post_metrics.get('respostas', 0), 
                                            'Compartilhamentos' : post_metrics.get('reposts', 0),
                                            'Curtidas' :  post_metrics.get('curtidas', 0),
                                            'Visualizações' :  post_metrics.get('visualizações', 0) }}))
                logger.debug(f"Link adicionado: {post_url}")
        logger.debug(f"Links filtrados: {filtered_posts}")
        logger.debug(f"Total de links filtrados: {len(filtered_posts)}")
        return filtered_posts

    def standard_procedure(self, dates: list[datetime])-> list[dict]:
        self.start_browser_user()
        data = self.collect_filtered_post_links(dates[0], dates[1])
        input("Verifique os dados coletados e pressione Enter para continuar...")
        self.stop_browser()
        return data