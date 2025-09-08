from playwright.sync_api import sync_playwright, Locator
from components.ProxyGenerate.getProxy import ProxyRequest
import logging
from components.PlayWrightAuto.LocatorImport import safeLocator

logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlayEssencial:
    def __init__(self, url=None, playwright=None, browser_data_path=None, chrome_executable_path=None, browser=None, page=None):
        print("PlayEssencial was initialized")
        print("browser is : ", browser, "page is : ", page)
        self.current_url = url
        self.playwright = None if playwright == None else playwright
        self.browser = None if browser == None else browser
        self.page = None if page == None else page
        self.browser_data_path = browser_data_path
        self.chrome_executable_path = chrome_executable_path
        
    def validate_locator(self, locator : Locator)-> None:
        def check_locator(locator: Locator, description="element"):
            try:
                self.page.wait_for_selector(locator, timeout=5000)
                logging.info(f"Locator {description} encontrado: {locator}\n")
                return True
            except:
                logging.error(f"O locator {description} não foi encontrado: {locator}")
                return False
    
        if not check_locator(locator) :
            raise Exception(f"Os seguintes locators não foram encontrados: {locator}")
        return locator

    def set_url(self, url):
        if url == None:
            return 
        self.current_url = url
        print(f"{self.current_url} was set as current URL")
        return url
   
    def start_sync_playwright(self):
        if self.playwright is None:
            self.playwright = sync_playwright().start()

    def start_browser(self):
        if self.playwright is None:
            self.start_sync_playwright()
        self.browser = self.playwright.chromium.launch(headless=False)  # Set headless=True to run without UI
        self.page = self.browser.new_page()
    
    def start_browser_user(self):
        if self.playwright is None:
                    self.start_sync_playwright()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir= self.browser_data_path,
            headless=False,
            executable_path= self.chrome_executable_path,
        )
        self.page = self.browser.new_page()
        
    def stop_browser(self):
        if self.browser:
            input()
            self.browser.close()
