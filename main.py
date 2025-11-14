import os, certifi, subprocess, time

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

try:
    import undetected_chromedriver as uc
    USE_UC = True
except ImportError:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    USE_UC = False


def run(profile_dir: str, profile_name: str, target_url: str):
    # Kill any existing Chrome instances using the profile
    subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe', '/T'],
                   stderr=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL,
                   check=False)
    time.sleep(1.5)

    # Setup Chrome options
    if USE_UC:
        options = uc.ChromeOptions()
    else:
        from selenium.webdriver.chrome.options import Options
        options = Options()

    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument(f"--profile-directory={profile_name}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    
    # CRITICAL: Hide the restore pages popup bubble
    options.add_argument("--hide-crash-restore-bubble")
    
    # Disable session restore features
    options.add_argument("--disable-session-crashed-bubble")
    options.add_argument("--disable-infobars")

    # Apply experimental options to prevent session restore
    if not USE_UC:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
    
    # CRITICAL FIX: Set profile preferences to prevent restore popup
    # This tells Chrome the previous session exited cleanly
    options.add_experimental_option("prefs", {
        "profile.exit_type": "Normal",
        "profile.exited_cleanly": True,
        "browser.startup.page": 0,  # 0 = blank page, 1 = restore, 4 = custom URL
        "session.restore_on_startup": 0  # Don't restore session
    })

    # Launch browser
    driver = None
    try:
        if USE_UC:
            driver = uc.Chrome(options=options, use_subprocess=True)
        else:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        # Navigate to blank page first to clear any restore attempts
        driver.get("about:blank")
        time.sleep(1)
        
        # Now navigate to the target URL
        print(f"Navigating to: {target_url}")
        driver.get(target_url)
        time.sleep(3)

        # Double-check if the right page loaded
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        if not current_url.startswith(target_url) and current_url != "about:blank":
            print(f"⚠️  Wrong page detected, forcing navigation...")
            driver.get(target_url)
            time.sleep(3)

        # Screenshot to confirm
        time.sleep(2)
        driver.save_screenshot("screenshot.png")
        print(f"✅ Opened successfully: {driver.current_url}")
        print("Screenshot saved to screenshot.png")

        input("\nPress Enter to close...")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        
    finally:
        # CRITICAL: Always close cleanly to prevent restore popup next time
        if driver:
            try:
                driver.close()  # Close current window
            except:
                pass
            try:
                driver.quit()   # Quit entire session cleanly
            except:
                pass


if __name__ == "__main__":
    username = os.getenv('USERNAME')
    profile_dir = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"
    profile_name = "Default"   # or "Profile 1", "Profile 2"
    target_url = "https://windscribe.com/"

    run(profile_dir, profile_name, target_url)