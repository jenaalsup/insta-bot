from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    profile_username = input("Enter the Instagram usernames you want to scrape: ")
    return username, password, profile_username

def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)  
    
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
    )
    
    username_input.send_keys(username)
    password_input.send_keys(password)
    
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_button.click()
    
    time.sleep(5)

def scrape_followers(driver, username):
    driver.get(f'https://www.instagram.com/{username}/')
    time.sleep(3.5)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))).click()
    time.sleep(2)
    print(f"Scraping followers for {username}...")

    users = set()
    prev_user_count = 0
    no_new_users_count = 0
    max_no_new_users = 5  # number of scrolls without new users before stopping

    while True:
        followers = driver.find_elements(By.XPATH, "//a[contains(@href, '/') and not(contains(@href, 'instagram.com'))]")

        for i in followers:
            if i.get_attribute('href'):
                users.add(i.get_attribute('href').split("/")[3])

        if len(users) == prev_user_count:
            no_new_users_count += 1
        else:
            no_new_users_count = 0

        print(f"Current number of followers: {len(users)}")

        if no_new_users_count >= max_no_new_users:
            print("No new users found after multiple scrolls. Stopping.")
            break

        prev_user_count = len(users)
        ActionChains(driver).send_keys(Keys.END).perform()
        time.sleep(2)  

    users = list(users)
    print(f"Total followers scraped: {len(users)}")
    return users

def scrape_following(driver, username):
    driver.get(f'https://www.instagram.com/{username}/')
    time.sleep(3.5)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))).click()
    time.sleep(2)
    print(f"[Info] - Scraping following for {username}...")

    users = set()
    prev_user_count = 0
    no_new_users_count = 0
    max_no_new_users = 5  

    try:
        while True:
            following = driver.find_elements(By.XPATH, "//a[contains(@href, '/') and not(contains(@href, 'instagram.com'))]")

            for i in following:
                if i.get_attribute('href'):
                    users.add(i.get_attribute('href').split("/")[3])

            if len(users) == prev_user_count:
                no_new_users_count += 1
            else:
                no_new_users_count = 0

            print(f"[Debug] - Current number of following: {len(users)}")

            if no_new_users_count >= max_no_new_users:
                print("[Info] - No new users found after multiple scrolls. Stopping.")
                break

            prev_user_count = len(users)
            ActionChains(driver).send_keys(Keys.END).perform()
            time.sleep(2)  

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Number of users when error occurred: {len(users)}")

    users = list(users)
    print(f"[Info] - Total number of following scraped: {len(users)}")
    return users

def compare_followers_following(followers, following):
    not_following_back = set(following) - set(followers)
    return list(not_following_back)


service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--log-level=3")
mobile_emulation = {
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
options.add_experimental_option("mobileEmulation", mobile_emulation)
driver = webdriver.Chrome(service=service, options=options)

username, password, profile_username = prompt_credentials()
login(driver, username, password)
followers = scrape_followers(driver, profile_username)
following = scrape_following(driver,profile_username)
not_following_back = compare_followers_following(followers, following)

print(not_following_back)

driver.quit() 
