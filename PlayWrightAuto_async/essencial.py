from playwright.async_api import async_playwright, Locator
import logging
import asyncio
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        print("PlayEssencial was initialized")
        print("browser is : ", browser, "page is : ", page)

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
    
    async def safe_locator(self, xmlPath: str, description="Não Definido") -> Locator:
            """
            Espera o locator aparecer. Se não aparecer, lança erro.
            """
            async def check_locator(xmlPath, description):
                try:
                    await self.page.wait_for_selector(xmlPath, timeout=5000)
                    logging.info(f"Locator encontrado: {description}")
                    return True
                except Exception:
                    logging.error(
                        f"ERRO: O locator '{description}' não foi encontrado. "
                        f"Path -> {xmlPath}"
                    )
                    return False

            if not await check_locator(xmlPath, description):
                raise Exception(
                    f"ERRO: Não foi possível encontrar o locator '{description}'. "
                    f"Path -> {xmlPath}"
                )

            return self.page.locator(xmlPath)

    async def validate_locator(self, locator: str) -> str:
        async def check_locator(locator: str, description="element"):
            try:
                await self.page.wait_for_selector(locator, timeout=5000)
                logging.info(f"Locator {description} encontrado: {locator}\n")
                return True
            except Exception as e:
                logging.error(f"O locator {description} não foi encontrado: {locator}")
                return False

        if not await check_locator(locator):
            raise Exception(f"Os seguintes locators não foram encontrados: {locator}")

        return locator

    # ---------------------------
    # URL
    # ---------------------------
    def set_url(self, url):
        if url is None:
            return
        self.current_url = url
        print(f"{self.current_url} was set as current URL")
        return url

    # ---------------------------
    # PLAYWRIGHT
    # ---------------------------
    async def start_async_playwright(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()

    # ---------------------------
    # BROWSER NORMAL
    # ---------------------------
    async def start_browser(self):
        if self.playwright is None:
            await self.start_async_playwright()

        self.browser = await self.playwright.chromium.launch(
            headless=False
        )
        self.page = await self.browser.new_page()

    # ---------------------------
    # BROWSER COM PERFIL
    # ---------------------------
    async def start_browser_user(self):
        if self.playwright is None:
            await self.start_async_playwright()

        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.browser_data_path,
            headless=False,
            executable_path=self.chrome_executable_path,
        )

        self.page = await self.browser.new_page()

    # ---------------------------
    # STOP
    # ---------------------------
    async def stop_browser(self):
        if self.browser:
            await asyncio.sleep(0.1)
            await self.browser.close()
