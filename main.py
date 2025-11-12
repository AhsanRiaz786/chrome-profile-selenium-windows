import os, certifi
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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import tempfile
import subprocess
import time


def run(profile_path: str):
    # Kill Chrome processes on Windows
    subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe', '/T'], 
                  stderr=subprocess.DEVNULL, 
                  stdout=subprocess.DEVNULL, 
                  check=False)
    time.sleep(2)
    
    original_path = os.path.dirname(profile_path)
    profile_name = os.path.basename(profile_path)
    
    temp_dir = tempfile.mkdtemp(prefix="ChromeTemp_")
    temp_profile = os.path.join(temp_dir, "UserData")
    source_profile = os.path.join(original_path, profile_name)
    
    os.makedirs(temp_profile, exist_ok=True)
    dest_profile = os.path.join(temp_profile, profile_name)
    shutil.copytree(source_profile, dest_profile, ignore=shutil.ignore_patterns('Service Worker', 'Code Cache', 'GPUCache'))
    
    for file_name in ["Local State", "Preferences", "Secure Preferences"]:
        source_file = os.path.join(original_path, file_name)
        if os.path.exists(source_file):
            shutil.copy2(source_file, temp_profile)
    
    if USE_UC:
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={temp_profile}")
        options.add_argument(f"--profile-directory={profile_name}")
        options.add_argument("--headless")
        # options.add_argument("--start-maximized")
        # options.add_experimental_option("prefs", {"credentials_enable_service": True, "profile.password_manager_enabled": True})
        driver = uc.Chrome(options=options)
    else:
        options = Options()
        options.add_argument(f"--user-data-dir={temp_profile}")
        options.add_argument(f"--profile-directory={profile_name}")
        # options.add_argument("--start-maximized")
        # options.add_experimental_option("prefs", {"credentials_enable_service": True, "profile.password_manager_enabled": True})
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    # driver.implicitly_wait(10)
    
    driver.get("https://windscribe.com/")
    time.sleep(5)
    driver.save_screenshot("screenshot.png")
    # WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)
    
    input()
    driver.quit()


if __name__ == "__main__":
    # Windows Chrome profile path examples:
    # Default profile: C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Default
    # Profile 1: C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Profile 1
    
    # Get Windows username automatically
    username = os.getenv('USERNAME')
    
    # Change 'Default' to your profile name (e.g., 'Profile 1', 'Profile 2', etc.)
    profile_path = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default"
    
    # Or specify manually:
    # profile_path = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Profile 1"
    
    run(profile_path=profile_path)