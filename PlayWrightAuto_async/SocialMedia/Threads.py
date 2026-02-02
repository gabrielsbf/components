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
        await self.page.wait_for_timeout(3000)

        locs = load_locators()
        await self.safe_locator("THREADS_FEED", "Feed dos Posts - Geral")
        feed = self.page.locator(locs["THREADS_FEED"])

        since = since if isinstance(since, datetime) else datetime.strptime(since, "%d/%m/%Y")
        until = until if isinstance(until, datetime) else datetime.strptime(until, "%d/%m/%Y").replace(hour=23, minute=59, second=59)

        collected: dict[str, dict] = {} 
        last_date = datetime.now()

        last_seen_count = 0
        stagnant_rounds = 0

        while last_date >= since and stagnant_rounds < 6:
            await self.safe_locator("THREADS_FEED_POST", "Posts Individuais")
            posts = feed.locator(locs["THREADS_FEED_POST"])
            count = await posts.count()

            if count == last_seen_count:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0
                last_seen_count = count

            for i in range(count):
                post = posts.nth(i)

                href = await post.locator(locs["THREADS_POST_HREF"]).get_attribute("href")
                if not href:
                    continue
                full_link = f"https://www.threads.net{href}"
                if full_link in collected:
                    continue

                dt_str = await post.locator("//time").get_attribute("datetime")
                if not dt_str:
                    continue
                post_date = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.000Z")

                if post_date < since:
                    pass

                if since <= post_date <= until:
                    metrics_text = await post.locator(locs["THREADS_METRICS"]).all_inner_texts()

                    description_locator = post.locator(locs["THREADS_DESCRIPTION"])
                    description = (
                        await description_locator.text_content()
                        if await description_locator.count() > 0
                        else "Sem descrição"
                    )

                    metrics = convert_text_to_metrics(metrics_text)
                    collected[full_link] = {
                        "date_created": post_date.strftime("%d/%m/%Y %H:%M:%S"),
                        "description": description,
                        "link_url": full_link,
                        "visualizations": metrics.get("Visualizações", 0),
                        "likes": metrics.get("Curtidas", 0),
                        "comments": metrics.get("Comentários", 0),
                        "reposts": metrics.get("Repostados", 0),
                        "shares": metrics.get("Compartilhamentos", 0),
                    }

            if count > 0:
                last_post = posts.nth(count - 1)
                last_dt = await last_post.locator("//time").get_attribute("datetime")
                if last_dt:
                    last_date = datetime.strptime(last_dt, "%Y-%m-%dT%H:%M:%S.000Z")

            await self.page.mouse.wheel(0, 1200)
            await self.page.wait_for_timeout(800)

        return list(collected.values())


    async def standard_procedure(self, dates: list[datetime]) -> dict:
            data = await self.get_href(dates[0], dates[1])
            logger.info("Procedure completed.")
            return data
