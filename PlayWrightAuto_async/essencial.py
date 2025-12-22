from playwright.async_api import async_playwright
from components.PlayWrightAuto_async.locators import *
import logging
import asyncio
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLOBAL_LOGGER")


class PlayEssencial:
    def __init__(
        self,
        url=None,
        playwright=None,
        browser_data_path=None,
        chrome_executable_path=None,
        browser=None,
        page=None
    ):
        logger.info("PlayEssencial was initialized")
        logger.info(f"browser is : {browser}, page is : {page}")

        self.current_url = url
        self.playwright = playwright
        self.browser = browser
        self.page = page
        self.browser_data_path = browser_data_path
        self.chrome_executable_path = chrome_executable_path

    @staticmethod
    def normalize_datetime(dt: datetime) -> datetime:
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    async def safe_locator(self, locator_key: str, description="Não Definido"):
        locs = load_locators()  
        locator_value = locs[locator_key]   

        while True:
            try:
               
                await self.page.wait_for_selector(locator_value, timeout=5000)
                logging.info(f"Locator encontrado: {description}")
                return self.page.locator(locator_value)

            except Exception:
                logging.error(
                    f"Erro ao buscar locator '{locator_key}' ({description})\n"
                    f"XPath atual: {locator_value}"
                )
                new_value = input(
                    f"Digite o NOVO XPath/CSS para '{description}' (chave: {locator_key}): "
                )
                locs[locator_key] = new_value
                save_locators(locs)
                locator_value = new_value

    def set_url(self, url):
        if url is None:
            return
        self.current_url = url
        logger.info(f"{self.current_url} was set as current URL")
        return url

    async def start_async_playwright(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()

    async def start_browser(self):
        if self.playwright is None:
            await self.start_async_playwright()

        self.browser = await self.playwright.chromium.launch(
            headless=False
        )
        self.page = await self.browser.new_page()

    async def start_browser_user(self):
        if self.playwright is None:
            await self.start_async_playwright()

        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.browser_data_path,
            headless=False,
            executable_path=self.chrome_executable_path,
        )

        self.page = await self.browser.new_page()

    async def stop_browser(self):
        if self.browser:
            await asyncio.sleep(0.1)
            await self.browser.close()
