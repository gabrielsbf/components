from playwright.sync_api import sync_playwright

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
