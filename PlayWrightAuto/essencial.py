from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


# from components.ProxyGenerate.getProxy import ProxyRequest

class PlayEssencial:
    def __init__(self, url=None):
        self.current_url = url
        self.browser = None
        self.page = None

    def set_url(self, url):
        if url == None:
            return 
        self.current_url = url
        print(f"{self.current_url} was set as current URL")
        return url
    

    def start_browser(self):
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=False)  # Set headless=True to run without UI
        self.page = self.browser.new_page()
    
    def start_browser_user(self):
        chrome_profile_path = "C:/Users/Alex_/AppData/Local/Google/Chrome/User Data"
        playwright = sync_playwright().start()

        self.browser = playwright.chromium.launch_persistent_context(
            user_data_dir= chrome_profile_path,
            headless=False,
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe"
        )
        self.page = self.browser.new_page()
            # page.goto('https://www.threads.net')
            # input("Pressione Enter para fechar...")
            # browser.close()
        
    def stop_browser(self):
        if self.browser:
            input()
            self.browser.close()
