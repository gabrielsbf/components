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

    
         
    async def get_href(self, since: str | datetime, until: str | datetime) -> list[dict]:

        def convert_text_to_metrics(metrics_text: list) -> dict:
            return {
                'Curtidas': metrics_text[0] if metrics_text and metrics_text[0] else 0,
                'Comentários': metrics_text[1] if len(metrics_text) > 1 else 0,
                'Repostados': metrics_text[2] if len(metrics_text) > 2 else 0,
                'Compartilhamentos': metrics_text[3] if len(metrics_text) > 3 else 0,
            }

        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser() first.")

        await self.page.goto(self.current_url, timeout=50000)
        await self.page.wait_for_load_state('domcontentloaded')
        await self.page.wait_for_timeout(5000)

        feed = self.page.safeLocator(THREADS_FEED, "Feed dos Posts - Geral")

        since = since if isinstance(since, datetime) else datetime.strptime(since, "%d/%m/%Y")
        until = until if isinstance(until, datetime) else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)

        last_date = datetime.now()
        filtered_posts = []

        while last_date >= since:
            await self.page.mouse.wheel(0, 1000)
            await self.page.wait_for_timeout(500)

            posts = feed.safeLocator(THREADS_FEED_POST, "Posts Individuais")
            count = await posts.count()
            last_post = posts.nth(count - 1)

            access_date = last_post.locator('//time')
            last_datetime_str = await access_date.get_attribute("datetime")

            if last_datetime_str:
                last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                if last_date < since:
                    break

        posts = feed.safeLocator(THREADS_FEED_POST, "Posts Individuais")
        count = await posts.count()

        for i in range(count):
            post = posts.nth(i)

            metrics_text = await post.safeLocator(
                THREADS_METRICS, "Métricas"
            ).all_inner_texts()

            href = await post.safeLocator(
                THREADS_POST_HREF, "Link"
            ).get_attribute("href")

            description_locator = post.safeLocator(THREADS_DESCRIPTION, "Descrição")
            description = (
                await description_locator.text_content()
                if await description_locator.count() > 0
                else "Sem descrição"
            )

            metrics = convert_text_to_metrics(metrics_text)

            last_datetime_str = await post.locator("//time").get_attribute("datetime")
            if last_datetime_str:
                last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")

                if since <= last_date <= until:
                    filtered_posts.append({
                        href: {
                            "Descrição": description,
                            "Data": last_date.strftime("%d/%m/%Y %H:%M:%S"),
                            **metrics
                        }
                    })

        return filtered_posts
