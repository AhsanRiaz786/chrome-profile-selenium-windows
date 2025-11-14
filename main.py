import os, certifi, subprocess, time, json

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

    # Clean up profile to prevent session restore
    prefs_path = os.path.join(profile_dir, profile_name, "Preferences")
    if os.path.exists(prefs_path):
        with open(prefs_path, 'r') as f:
            prefs = json.load(f)
        prefs['profile'] = prefs.get('profile', {})
        prefs['profile']['exit_type'] = 'normal'
        prefs['profile']['exited_cleanly'] = True
        with open(prefs_path, 'w') as f:
            json.dump(prefs, f)

    session_files = ["Current Session", "Current Tabs", "Last Session", "Last Tabs"]
    for fname in session_files:
        fpath = os.path.join(profile_dir, profile_name, fname)
        if os.path.exists(fpath):
            os.remove(fpath)

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
    options.add_argument("--hide-crash-restore-bubble")
    options.add_experimental_option("prefs", {
        "profile.exit_type": "normal",
        "profile.exited_cleanly": True
    })

    # Apply experimental options only if using standard Chrome
    if not USE_UC:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

    # Launch browser
    if USE_UC:
        driver = uc.Chrome(options=options, use_subprocess=True)
    else:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    # Force navigation even if homepage/session restore appears
    time.sleep(2)
    driver.get(target_url)
    time.sleep(3)

    # Double-check if the right page loaded
    if not driver.current_url.startswith(target_url):
        driver.get(target_url)

    # Screenshot to confirm
    time.sleep(4)
    driver.save_screenshot("screenshot.png")
    print(f"✅ Opened successfully: {driver.current_url}")

    input("Press Enter to close...")
    driver.quit()


if __name__ == "__main__":
    username = os.getenv('USERNAME')
    profile_dir = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"
    profile_name = "Default"   # or "Profile 1", "Profile 2"
    target_url = "https://windscribe.com/"

    run(profile_dir, profile_name, target_url)