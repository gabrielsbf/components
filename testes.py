from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright




def teste():
    chrome_profile_path = "C:/Users/Alex_/AppData/Local/Google/Chrome/User Data"
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir= chrome_profile_path,
            headless=False,
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe"
        )
        page = browser.new_page()
        page.goto('https://www.threads.net')
        input("Pressione Enter para fechar...")
        browser.close()

teste()