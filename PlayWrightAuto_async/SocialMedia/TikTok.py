from datetime import datetime
from components.PlayWrightAuto_async.essencial import PlayEssencial, logger
from components.PlayWrightAuto_async.locators import *
import aiohttp
import json
import asyncio


class Tiktok_Automation(PlayEssencial):
    def __init__(self, account, playwright=None, browser_data_path=None,
                 chrome_executable_path=None, browser=None, page=None):

        super().__init__(
            f"https://www.tiktok.com/@{account}",
            playwright,
            browser_data_path,
            chrome_executable_path,
            browser,
            page
        )

        self.headers = {
            "authority": "www.tiktok.com",
            "method": "GET",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "accept-encoding": "gzip, deflate, br",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        }

    async def extract_text_between(self, html: str, start_marker: str, end_marker: str) -> dict:
        start_index = html.find(start_marker)
        if start_index == -1:
            return {}

        end_index = html.find(end_marker, start_index)
        if end_index == -1:
            return {}

        snippet = html[start_index:end_index]

        try:
            snippet = "{" + snippet + "}"
            return json.loads(snippet)
        except Exception:
            return {}

    async def get_request_createdTime(
        self,
        status: int,
        html: str,
        result_info: dict,
        start_date: datetime,
        end_date: datetime
    ):

        logger.info(f"Status Code: {status}")

        findResp = html.find("webapp.video-detail") - 1

        if findResp <= -1:
            logger.warning("createTime not found")
            result_info[self.current_url]["date_created"] = "notFound"
            return 1

        start_index = html[findResp:].find("createTime") + findResp - 1
        end_index = html[start_index:].find(",") + start_index

        block = html[start_index:end_index]
        timestamp = int(block.replace('"', '').removeprefix("createTime:"))

        processed_date = datetime.fromtimestamp(timestamp)
        logger.info(f"Video date: {processed_date}")

        if processed_date < start_date:
            return 0
        if processed_date > end_date:
            return 1

        response_data = await self.extract_text_between(html, '"statsV2":', ',"warnInfo"')
        stats = response_data.get("statsV2", {})

        result_info[self.current_url].update({
            "date_created": processed_date,
            "digg_count": stats.get("diggCount", "0"),
            "share_count": stats.get("shareCount", "0"),
            "comment_count": stats.get("commentCount", "0"),
            "play_count": stats.get("playCount", "0"),
            "collect_count": stats.get("collectCount", "0"),
            "repost_count": stats.get("repostCount", "0"),
        })
        return self.current_url

    async def access_videos(self, result_info: dict, start_date: datetime, end_date: datetime) -> dict:
        all_videos = []
        counter = 0

        sem = asyncio.Semaphore(5)

        async with aiohttp.ClientSession(headers=self.headers) as session:

            async def process_video(link):
                nonlocal counter
                async with sem:
                    self.set_url(link)
                    logger.info(f"Fetching: {self.current_url}")

                    async with session.get(self.current_url) as resp:
                        html = await resp.text()

                    result = await self.get_request_createdTime(
                        resp.status,
                        html,
                        result_info,
                        start_date,
                        end_date
                    )

                    if result not in (0, 1):
                        all_videos.append(result)

                    if result == 0 and counter > 3:
                        return "STOP"
                    counter += 1

                    return result

            tasks = [process_video(link) for link in result_info.keys()]
            results = await asyncio.gather(*tasks)

            if "STOP" in results:
                logger.info("STOP signal received, stopping early.")

        return {k: v for k, v in result_info.items() if k in all_videos}

    async def get_feed_info(self) -> dict:
        result_info = {}
        if not self.page:
            raise Exception("Browser or page not initialized. Call start_browser_user() first.")
        await self.page.goto(self.current_url, timeout=30000)
        input("Press Enter after the page has loaded...")
        await self.safe_locator("TIKTOK_FEED_CONTAINER", "Container do Feed")
        await self.safe_locator("TIKTOK_FEED_POST", "Post do Feed")
        locs = load_locators()
        feed = self.page.locator(locs["TIKTOK_FEED_CONTAINER"])
        items = feed.locator(locs["TIKTOK_FEED_POST"])
        count = await items.count()
        for i in range(count):
            item = items.nth(i)
            anchor = item.locator("a")
            href = await anchor.get_attribute("href")
            img = item.locator("img")
            alt_text = await img.get_attribute("alt")
            result_info[href] = {"description": alt_text}

        return result_info

    async def standard_procedure(self, dates: list[datetime]) -> dict:
        try:
            if self.browser is None:
                await self.start_browser_user()

            data = await self.get_feed_info()

            filtered = await self.access_videos(data, dates[0], dates[1])
            logger.info("Procedure completed.")

            return filtered

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
