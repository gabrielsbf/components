from components.PlayWrightAuto_async.essencial import PlayEssencial, logger
from components.PlayWrightAuto_async.locators import *
from datetime import datetime
import asyncio
import re


class Twitter_Automation(PlayEssencial):
    def __init__(self, account, core):
        self.account = account
        self.playwright = core.playwright
        self.browser = core.browser
        self.page = core.page
        self.browser_data_path = core.browser_data_path
        self.chrome_executable_path = core.chrome_executable_path
        self.current_url = f"https://www.x.com/{self.account}"

    async def collect_filtered_post_links(self, start_date: datetime, end_date: datetime) -> list[dict]:

        def convert_text_to_metrics(metrics_text: str) -> dict:
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

        await self.set_url(self.current_url)
        await self.page.goto(self.current_url, timeout=50000)
        await self.page.wait_for_load_state('domcontentloaded')
        await self.page.wait_for_timeout(5000)

        locs = load_locators()

        await self.safe_locator("TWITTER_FEED_CONTAINER", "Container do Feed")
        await self.page.wait_for_selector(locs["TWITTER_FEED_CONTAINER"], timeout=30000)
        await self.page.wait_for_timeout(5000)

        feed_container = self.page.locator(locs["TWITTER_FEED_CONTAINER"])

        processed_hrefs = set()
        filtered_posts = []
        continue_collecting = True

        await self.safe_locator("TWITTER_POST_HREF", "Link do Post")
        await self.safe_locator("TWITTER_DESCRIPTION", "Descrição do Post")
        await self.safe_locator("TWITTER_METRICS", "Métricas do Post")

       
        sem = asyncio.Semaphore(5)

        async def process_post(post):

            async with sem:
                metrics = post.locator(locs["TWITTER_METRICS"])

                try:
                    count = await metrics.count()
                except:
                    count = 0

                engagement_text = await metrics.get_attribute("aria-label") if count > 0 else None

                element = post.locator(locs["TWITTER_POST_HREF"]).first

                if await element.count() == 0:
                    return None

                time_el = element.locator("time")
                datetime_str = await time_el.get_attribute("datetime") if await time_el.count() > 0 else None
                post_datetime = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ") if datetime_str else None

                if not post_datetime:
                    return None

                post_url = await element.get_attribute("href")

                if post_url in processed_hrefs:
                    return None

                if post_datetime < start_date:
                    return "STOP"

                if post_datetime > end_date:
                    return None

                processed_hrefs.add(post_url)

                
                description_locator = post.locator(locs["TWITTER_DESCRIPTION"])
                post_description = await description_locator.inner_text() if await description_locator.count() > 0 else "Sem descrição"

              
                post_metrics = convert_text_to_metrics(engagement_text) if engagement_text else {}

                return {
                    f"https://www.x.com{post_url}": {
                        "description": post_description,
                        "date_create": post_datetime,
                        "comments": post_metrics.get("respostas", 0),
                        "shares": post_metrics.get("reposts", 0),
                        "likes": post_metrics.get("curtidas", 0),
                        "views": post_metrics.get("visualizações", 0),
                    }
                }

        while continue_collecting:
            await self.page.mouse.wheel(0, 1000)
            await self.page.wait_for_timeout(500)

            posts = feed_container.locator('//article')
            total = await posts.count()
            if total == 0:
                break

            tasks = [process_post(posts.nth(i)) for i in range(total)]

            results = await asyncio.gather(*tasks)

            for r in results:
                if r == "STOP":
                    continue_collecting = False
                    break

                if r:
                    filtered_posts.append(r)

        return filtered_posts

    async def standard_procedure(self, dates: list[datetime]) -> dict:
            data = await self.collect_filtered_post_links(dates[0], dates[1])
            logger.info("Procedure completed.")
            return data

