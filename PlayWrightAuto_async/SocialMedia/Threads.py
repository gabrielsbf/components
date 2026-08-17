from components.PlayWrightAuto_async.essencial import PlayEssencial, logger
from components.PlayWrightAuto_async.locators import *
from datetime import datetime
import asyncio

class Threads_Automation(PlayEssencial):
    def __init__(self, account, core):
        self.account = account
        self.playwright = core.playwright
        self.browser = core.browser
        self.page = core.page
        self.browser_data_path = core.browser_data_path
        self.chrome_executable_path = core.chrome_executable_path
        self.current_url = f"https://www.threads.net/@{self.account}"
        
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

        locs = load_locators()
        await self.safe_locator("THREADS_FEED", "Feed dos Posts - Geral")
        feed = self.page.locator(locs["THREADS_FEED"])

        since = since if isinstance(since, datetime) else datetime.strptime(since, "%d/%m/%Y")
        until = until if isinstance(until, datetime) else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)

        last_date = datetime.now()
        filtered_posts = []

        async def process_post(post):
            async with sem:
                await self.safe_locator("THREADS_METRICS", "Métricas")
                await self.safe_locator("THREADS_POST_HREF", "Link")
                await self.safe_locator("THREADS_DESCRIPTION", "Descrição")

                metrics_text = await post.locator(locs["THREADS_METRICS"]).all_inner_texts()

                href_locator = post.locator(locs["THREADS_POST_HREF"])
                href = await href_locator.get_attribute("href")

                description_locator = post.locator(locs["THREADS_DESCRIPTION"])
                description = (
                    await description_locator.text_content()
                    if await description_locator.count() > 0
                    else "Sem descrição"
                )

                metrics = convert_text_to_metrics(metrics_text)

                last_datetime_str = await post.locator("//time").get_attribute("datetime")
                if not last_datetime_str:
                    return None

                post_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
                date = post_date.strftime("%d/%m/%Y %H:%M:%S")
            
                
                if since <= post_date <= until:
                    return {
                    'date_created': date,
                    'description': description,
                    'link_url': f"https://www.threads.net{href}",
                    'visualizations': metrics.get("Visualizações", 0),
                    'likes': metrics.get("Curtidas", 0),
                    'comments': metrics.get("Comentários", 0),
                    'reposts': metrics.get("Repostados", 0),
                    'shares': metrics.get("Compartilhamentos", 0),
                    }

                return None

        filtered_posts = []
        links = []
        while last_date >= since:
            await self.page.mouse.wheel(0, 1000)
            await self.page.wait_for_timeout(500)

            await self.safe_locator("THREADS_FEED_POST", "Posts Individuais")
            posts = feed.locator(locs["THREADS_FEED_POST"])

            count = await posts.count()
            last_post = posts.nth(count - 1)
            access_date = last_post.locator('//time')

            last_datetime_str = await access_date.get_attribute("datetime")
            sem = asyncio.Semaphore(5)
            tasks = [process_post(posts.nth(i)) for i in range(count)]
            results = await asyncio.gather(*tasks)
            filtered_posts.extend([r for r in results if r is not None and r["link_url"] not in links ])
            links.extend([r['link_url'] for r in results if r])
            if last_datetime_str:
                last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")

                if last_date < since:
                    break
        
        # posts = feed.locator(locs["THREADS_FEED_POST"]) 
        # count = await posts.count()

        

        

        return filtered_posts

    async def standard_procedure(self, dates: list[datetime]) -> dict:
            data = await self.get_href(dates[0], dates[1])
            logger.info("Procedure completed.")
            return data
