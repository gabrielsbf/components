import aiohttp
import asyncio
import re
from datetime import datetime, timezone
from typing import Generator
from components.PlayWrightAuto_async.essencial import PlayEssencial, logger
from components.PlayWrightAuto.locators import *


class Youtube_Automation(PlayEssencial):

    def __init__(self, account: str, core):
        self.playwright = core.playwright
        self.browser = core.browser
        self.page = core.page
        self.browser_data_path = core.browser_data_path
        self.chrome_executable_path = core.chrome_executable_path
        self.account = account
        self.current_url = f"https://www.youtube.com/{self.account}"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
    @staticmethod
    def extract_between(text, start, end):
        start_i = text.find(start)
        if start_i == -1:
            return ""
        end_i = text[start_i:].find(end) + start_i
        return text[start_i:end_i].replace(start, "").replace('"', "").strip()
    
    async def get_video_content(self) -> list[dict]:
        video_info = {}
            
        async def extract(url, content_type):
            await self.page.goto(url, timeout=30000)
            await self.page.wait_for_selector(YOUTUBE_VIDEO_CONTAINER, timeout=15000)

            items = await self.page.eval_on_selector_all(
                YOUTUBE_VIDEO_CONTAINER,
                """els => els.map(el => ({
                    href: el.getAttribute("href"),
                    title: el.getAttribute("title") || el.innerText
                }))"""
            )

            for item in items:
                if not item["href"]:
                    continue

                full_url = (
                    f"https://www.youtube.com{item['href']}"
                    if item["href"].startswith("/")
                    else item["href"]
                )

                if full_url not in video_info:
                    video_info[full_url] = {
                        "href": full_url,
                        "title": item["title"],
                        "type": content_type
                    }
                else:
                    video_info[full_url]["type"] = "video+stream"

        await extract(f"https://www.youtube.com/{self.account}/videos", "video")
        await extract(f"https://www.youtube.com/c/{self.account}/streams", "stream")
        

        return list(video_info.values())

    

    async def fetch_video(self, session, sem, video, start_date, end_date):
        print("Fetching video:", video["href"])
        async with sem:
            async with session.get(video["href"], headers=self.headers) as resp:
                html = await resp.text()

        date_raw = self.extract_between(
            html,
            '"uploadDate":',
            ","
        )
        print("Date raw:", date_raw)
        if not date_raw:
            return None

        processed_date = (
        datetime.fromisoformat(date_raw.strip("}"))
        .replace(tzinfo=None)
        )

        if processed_date < start_date or processed_date > end_date:
            return None

        likes = self.extract_between(html, '"likeCount":', ",")
        comments_raw = self.extract_between(html, '"contextualInfo":', ",")
        views_raw = self.extract_between(html, '"views":', ",")

        comments = re.findall(r"\d+", comments_raw)
        views = re.findall(r"\d+(?:[\.,]\d+)?", views_raw)

        res =  {
            "href": video["href"],
            "description": video["title"],
            "date_create": processed_date,
            "likes": likes,
            "comments": comments[0] if comments else "0",
            "views": views[0] if views else "0",
        }
        return res

    async def scrape_videos_by_date(self, start_date, end_date) -> dict:
        start_date = self.normalize_datetime(start_date)
        end_date = self.normalize_datetime(end_date)   
        videos = await self.get_video_content()

        sem = asyncio.Semaphore(5)
        results = {}

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_video(session, sem, v, start_date, end_date)
                for v in videos
            ]
            for result in await asyncio.gather(*tasks):
                if result == "STOP":
                    break
                if result:
                    results[result["href"]] = result
        return [results]

    async def standard_procedure(self, dates: list[datetime]) -> dict:
                data = await self.scrape_videos_by_date(dates[0], dates[1])
                logger.info("Procedure completed.")
                return data
