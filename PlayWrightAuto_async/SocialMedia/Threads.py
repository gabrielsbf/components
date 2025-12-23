from components.PlayWrightAuto_async.essencial import PlayEssencial, logger
from components.PlayWrightAuto_async.locators import *
from datetime import datetime
import asyncio

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

        locs = load_locators()
        await self.safe_locator("THREADS_FEED", "Feed dos Posts - Geral")
        feed = self.page.locator(locs["THREADS_FEED"])

        since = since if isinstance(since, datetime) else datetime.strptime(since, "%d/%m/%Y")
        until = until if isinstance(until, datetime) else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)

        last_date = datetime.now()
        filtered_posts = []

        while last_date >= since:
            await self.page.mouse.wheel(0, 1000)
            await self.page.wait_for_timeout(500)

            await self.safe_locator("THREADS_FEED_POST", "Posts Individuais")
            posts = feed.locator(locs["THREADS_FEED_POST"])

            count = await posts.count()
            last_post = posts.nth(count - 1)
            access_date = last_post.locator('//time')

            last_datetime_str = await access_date.get_attribute("datetime")

            if last_datetime_str:
                last_date = datetime.strptime(last_datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")

                if last_date < since:
                    break


        posts = feed.locator(locs["THREADS_FEED_POST"]) 
        count = await posts.count()

        sem = asyncio.Semaphore(5)

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

                if since <= post_date <= until:
                    return {
                        f"https://www.threads.net{href}": {
                            "Descrição": description,
                            "Data": post_date.strftime("%d/%m/%Y %H:%M:%S"),
                            "Curtidas": metrics.get("Curtidas", 0),
                            "Comentários": metrics.get("Comentários", 0),
                            "Visualizações": metrics.get("Visualizações", 0),
                            "Repostados": metrics.get("Repostados", 0),
                            "Compartilhamentos": metrics.get("Compartilhamentos", 0),
                        }
                    }

                return None

        tasks = [process_post(posts.nth(i)) for i in range(count)]

        results = await asyncio.gather(*tasks)

        filtered_posts = [r for r in results if r]

        return filtered_posts

    async def standard_procedure(self, dates: list[datetime]) -> dict:
        try:
            if self.browser is None:
                await self.start_browser_user()
            data = await self.get_href(dates[0], dates[1])
            logger.info("Procedure completed.")
            return data

        finally:
            await self._shutdown()

    async def _shutdown(self):
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, "playwright") and self.playwright:
                await self.playwright.stop()
        except:
            pass
