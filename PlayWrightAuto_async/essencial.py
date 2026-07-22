import os
import logging
from playwright.async_api import async_playwright, Locator, BrowserContext, Page, Playwright
from components.PlayWrightAuto_async.locators import *


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
        storage_state_path=None,
        browser=None, 
        page=None
    ):
        logger.info("PlayEssencial foi inicializado")
        self.current_url = url
        self.playwright: Playwright | None = playwright
        self.browser: BrowserContext | None = browser
        self.page: Page | None = page
        self.browser_data_path = browser_data_path
        self.chrome_executable_path = chrome_executable_path
        self.storage_state_path = storage_state_path
        
    async def validate_locator(self, locator: Locator) -> Locator:
        """Verifica se o Locator fornecido está visível/disponível na página."""
        try:
            await locator.wait_for(timeout=5000, state="visible")
            logger.info(f"Locator encontrado com sucesso: {locator}")
            return locator
        except Exception as e:
            logger.error(f"O locator não foi encontrado ou não ficou visível: {locator}")
            raise Exception(f"Os seguintes locators não foram encontrados: {locator}") from e

    def set_url(self, url: str):
        if url is None:
            return 
        self.current_url = url
        logger.info(f"{self.current_url} definido como URL atual")
        return url
   
    async def start_async_playwright(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()

    async def start_browser(self, storage_state_path: str | None = None):
        """Inicia o navegador com argumentos anti-detecção e suporte a storage_state."""
        if self.playwright is None:
            await self.start_async_playwright()

        state_file = storage_state_path or self.storage_state_path

        browser_instance = await self.playwright.chromium.launch(
            headless=False,
            channel="chrome",  # Usa o Chrome oficial do computador
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ]
        )

        context_args = {
            "viewport": None,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if state_file and os.path.exists(state_file):
            self.browser = await browser_instance.new_context(storage_state=state_file, **context_args)
            logger.info(f"Navegador iniciado com a sessão de: {state_file}")
        else:
            if state_file:
                logger.warning(f"Aviso: O arquivo '{state_file}' não foi encontrado. Abrindo sem sessão prévia.")
            self.browser = await browser_instance.new_context(**context_args)
            logger.info("Navegador iniciado sem sessão prévia.")

        self.page = await self.browser.new_page()


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

    async def start_browser_user(self):
        """Inicia o navegador com perfil de usuário persistente e flags anti-robô."""
        if self.playwright is None:
            await self.start_async_playwright()
            
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.browser_data_path,
            headless=False,
            executable_path=self.chrome_executable_path,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"]
        )
        
        if self.browser.pages:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()

    async def save_storage_state(self, path: str | None = None):
        """Salva a sessão atual (cookies e localStorage) em um arquivo JSON."""
        target_path = path or self.storage_state_path or "state.json"
        if self.browser:
            await self.browser.storage_state(path=target_path)
            logger.info(f"✅ Estado de autenticação salvo em '{target_path}'")
        else:
            logger.error("Não foi possível salvar o estado: navegador/contexto não foi inicializado.")

    async def stop_browser(self):
        """Encerra o contexto do navegador e o processo do Playwright."""
        if self.browser:
            input("Pressione Enter no terminal para fechar o navegador...")
            await self.browser.close()
            
        if self.playwright:
            await self.playwright.stop()
            logger.info("Instância do Playwright encerrada.")