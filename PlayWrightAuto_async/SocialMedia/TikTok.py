import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Generator, Union
from components.PlayWrightAuto_async.essencial import PlayEssencial
from components.PlayWrightAuto_async.locators import *


class Tiktok_Automation(PlayEssencial):

    def __init__(self, account, **kwargs):
        super().__init__(
            f"https://tiktok.com/@{account}",
            **kwargs
        )

        self.account = account

        self.headers = {
            "authority": "www.tiktok.com",
            "accept": "text/html",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }

    #############################
    # ITERADOR DE LINKS
    #############################
    def iterate_video_links(self, result_info: dict) -> Generator[str, None, None]:
        for key in list(result_info.keys()):
            yield key

    #############################
    # EXTRAÇÃO DE STATS
    #############################
    def extract_sigi_state(self, html: str) -> dict:
        """
        Extrai o JSON SIGI_STATE que contém todas infos do vídeo.
        Muito mais confiável que regex.
        """
        marker = "window['SIGI_STATE']="

        pos = html.find(marker)
        if pos == -1:
            return {}

        start = pos + len(marker)
        end = html.find("</script>", start)
        block = html[start:end].strip()

        try:
            return json.loads(block)
        except Exception:
            return {}

    #############################
    # ANALISA DATA E STATS
    #############################
    def analyze_video_html(
        self, link: str, html: str, result_info: dict,
        start_date: datetime, end_date: datetime
    ) -> Union[int, str]:

        data = self.extract_sigi_state(html)

        if not data or "ItemModule" not in data:
            result_info[link]["date_created"] = "notFound"
            return 1

        # pega o ID do vídeo
        item_module = data["ItemModule"]
        video_ids = list(item_module.keys())
        if not video_ids:
            return 1

        video_id = video_ids[0]
        info = item_module[video_id]

        # data
        ts = int(info.get("createTime", 0))
        if ts == 0:
            return 1

        dt = datetime.fromtimestamp(ts)
        dt = self.normalize_datetime(dt)

        start_date = self.normalize_datetime(start_date)
        end_date = self.normalize_datetime(end_date)

        # lógica original
        if dt < start_date:
            return 0
        if dt > end_date:
            return 1

        # stats
        result_info[link].update({
            "date_created": dt,
            "digg_count": info.get("diggCount", "0"),
            "share_count": info.get("shareCount", "0"),
            "comment_count": info.get("commentCount", "0"),
            "play_count": info.get("playCount", "0"),
            "collect_count": info.get("collectCount", "0"),
            "repost_count": info.get("repostCount", "0"),
        })

        return link

    #############################
    # FETCH DO VÍDEO
    #############################
    async def fetch_video(self, session, sem, link, result_info, start_date, end_date):
        async with sem:
            async with session.get(link, headers=self.headers) as resp:
                html = await resp.text()

        result = self.analyze_video_html(link, html, result_info, start_date, end_date)
        return result

    #############################
    # PROCESSA TODOS OS VÍDEOS
    #############################
    async def access_videos(self, result_info: dict,
                            start_date: datetime, end_date: datetime) -> dict:

        start_date = self.normalize_datetime(start_date)
        end_date = self.normalize_datetime(end_date)

        sem = asyncio.Semaphore(5)
        results = []

        async with aiohttp.ClientSession() as session:

            tasks = [
                self.fetch_video(session, sem, link, result_info, start_date, end_date)
                for link in self.iterate_video_links(result_info)
            ]

            responses = await asyncio.gather(*tasks)

            for element_vid in responses:

                if element_vid in (0, 1):
                    continue

                if isinstance(element_vid, str):
                    results.append(element_vid)

        return {k: v for k, v in result_info.items() if k in results}

    #############################
    # FEED DO PERFIL
    #############################
    async def get_feed_info(self) -> dict:

        result_info = {}

        if not self.page:
            raise Exception("Browser not initialized")

        await self.page.goto(self.current_url, wait_until="networkidle", timeout=60000)
        input("VERIFY IF THE PAGE HAS A PROBLEM OF CAPTCHA OR ERROR. THEN, PRESS ENTER TO CONTINUE")
        await self.safe_locator(TIKTOK_FEED_CONTAINER, "Container do Feed")
        await self.safe_locator(TIKTOK_FEED_POST, "Post do Feed")
        input("VERIFY IF THE LOCATORS WERE FOUND. THEN, PRESS ENTER TO CONTINUE")
        feed = self.page.locator(TIKTOK_FEED_CONTAINER)
        items = feed.locator(TIKTOK_FEED_POST)

        count = await items.count()

        for i in range(count):
            item = items.nth(i)

            # pega o href real
            anchor = item.locator("a")
            href = await anchor.evaluate("(el) => el.href")

            desc = await item.locator("img").get_attribute("alt") or ""

            if href:
                result_info[href] = {"description": desc}

        return result_info

    #############################
    # PROCEDIMENTO PADRÃO
    #############################
    async def standard_procedure(self, dates: list[datetime]) -> dict:
        try:
            if self.browser is None:
                await self.start_browser_user()

            feed_data = await self.get_feed_info()
            videos = await self.access_videos(feed_data, dates[0], dates[1])
            return videos

        finally:
            await self.stop_browser()

    #############################
    # STOP BROWSER
    #############################
    async def stop_browser(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
