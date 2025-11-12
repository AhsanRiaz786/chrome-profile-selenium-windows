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



def kill_chrome_processes():
    """Kill all Chrome processes on Windows"""
    try:
        # Use taskkill command for more reliable Chrome termination
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe', '/T'], 
                      stderr=subprocess.DEVNULL, 
                      stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error killing Chrome processes: {e}")
    
    time.sleep(3)


def run(profile_path: str):
    # Kill any existing Chrome instances
    kill_chrome_processes()
    
    # Parse the profile path
    original_path = os.path.dirname(profile_path)
    profile_name = os.path.basename(profile_path)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="ChromeTemp_")
    temp_profile = os.path.join(temp_dir, "UserData")
    
    # Source profile path
    source_profile = os.path.join(original_path, profile_name)
    
    # Create temp profile directory
    os.makedirs(temp_profile, exist_ok=True)
    
    print(f"Copying profile from {source_profile} to {dest_profile}...")
    
    # Copy profile to temp location with better error handling
    dest_profile = os.path.join(temp_profile, profile_name)
    try:
        shutil.copytree(
            source_profile, 
            dest_profile, 
            ignore=shutil.ignore_patterns(
                'Service Worker', 
                'Code Cache', 
                'GPUCache',
                'ShaderCache',
                'DawnCache',
                '*.lock',
                '*.log'
            ),
            dirs_exist_ok=False
        )
    except Exception as e:
        print(f"Error copying profile: {e}")
        shutil.rmtree(temp_dir)
        return
    
    # Copy important files from user data directory
    for file_name in ["Local State", "Preferences", "Secure Preferences"]:
        source_file = os.path.join(original_path, file_name)
        if os.path.exists(source_file):
            try:
                shutil.copy2(source_file, temp_profile)
            except Exception as e:
                print(f"Could not copy {file_name}: {e}")
    
    print("Profile copied successfully. Starting Chrome...")
    
    # Setup Chrome options
    if USE_UC:
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={temp_profile}")
        options.add_argument(f"--profile-directory={profile_name}")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "credentials_enable_service": True,
            "profile.password_manager_enabled": True,
            "profile.default_content_setting_values.notifications": 2
        })
        
        try:
            driver = uc.Chrome(options=options, version_main=141)
        except Exception as e:
            print(f"Error with version_main=141, trying without version specification: {e}")
            driver = uc.Chrome(options=options)
    else:
        options = Options()
        options.add_argument(f"--user-data-dir={temp_profile}")
        options.add_argument(f"--profile-directory={profile_name}")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "credentials_enable_service": True,
            "profile.password_manager_enabled": True,
            "profile.default_content_setting_values.notifications": 2
        })
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    
    driver.implicitly_wait(10)
    
    try:
        # Navigate to websites
        print("Navigating to Google...")
        driver.get("https://www.google.com")    
        time.sleep(10)
        
        print("Navigating to YouTube...")
        driver.get("https://www.youtube.com/")
        time.sleep(10)
        
        print("Navigating to Instagram...")
        driver.get("https://www.instagram.com/")
        time.sleep(10)
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during navigation: {e}")
    finally:
        driver.quit()
        
        # Clean up temp directory
        time.sleep(2)
        try:
            shutil.rmtree(temp_dir)
            print("Temporary profile cleaned up.")
        except Exception as e:
            print(f"Could not remove temp directory: {e}")


if __name__ == "__main__":
    # Windows Chrome profile path examples:
    # Default profile: C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Default
    # Profile 1: C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Profile 1
    
    # Replace with your actual Windows username
    username = os.getenv('USERNAME')
    profile_path = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default"
    
    # Or specify manually:
    # profile_path = r"C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Default"
    
    run(profile_path=profile_path)