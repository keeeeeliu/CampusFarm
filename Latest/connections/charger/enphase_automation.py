from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import time

# # Disable the __del__ method to prevent errors from being printed
# uc.Chrome.__del__ = lambda self: None

def charger_on():
    driver = uc.Chrome()
    # chromdriver_path = chromedriver_autoinstaller.install()
    # service = Service(chromdriver_path)
    # driver = webdriver.Chrome(service=service)
    # Open the webpage
    driver.get('https://enlighten.enphaseenergy.com')

    # Wait for the page to load
    time.sleep(2)

    # Enter login details
    try:
        # Find the email input field and enter your email
        email_field = driver.find_element(By.ID, 'user_email') 
        email_field.send_keys('campusfarm@umich.edu') 

        # Find the password input field and enter your password
        password_field = driver.find_element(By.ID, 'user_password') 
        password_field.send_keys('CFSPC&EV!')  

        # F5dind and click the sign-in button
        sign_in_button = driver.find_element(By.ID, 'submit')
        sign_in_button.click()

        print("Logged in successfully!")
    except Exception as e:
        print("Error during login:", e)

    time.sleep(3)

    # Click the myEnlighten button and switch to the new tab
    try:
        myEnlighten_button = driver.find_element(By.ID, 'myenlighten_link')
        myEnlighten_button.click()
        print("Clicked on myEnlighten button.")

        # Wait briefly for the new tab to open
        time.sleep(2)

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last opened tab
        print("Switched to the new tab.")
    except Exception as e:
        print("Error during myEnlighten click or switching tabs:", e)

    time.sleep(5)

    try:
        # Using XPath to target the button that contains the "Charge Now" text
        charge_now_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div[3]/div/div/div/div/div[3]/div/div[2]/div/div/button'))
        )
        ActionChains(driver).move_to_element(charge_now_button).click(charge_now_button).perform()
        print("Charge Now button clicked successfully!")
        time.sleep(5)
        driver.quit()
    except Exception as e:
        print("Error finding or clicking the Charge Now button:", e)

    driver.quit()

def charger_off():
    # Automatically install and get the path to chromedriver
    # chromedriver_path = chromedriver_autoinstaller.install()
    # service = Service(chromedriver_path)
    driver = uc.Chrome()
    # chromdriver_path = chromedriver_autoinstaller.install()
    # service = Service(chromdriver_path)
    # driver = webdriver.Chrome(service=service)

    # Open the webpage
    driver.get('https://enlighten.enphaseenergy.com')

    # Wait for the page to load
    time.sleep(2)

    # Enter login details
    try:
        # Find the email input field and enter your email
        email_field = driver.find_element(By.ID, 'user_email') 
        email_field.send_keys('campusfarm@umich.edu') 

        # Find the password input field and enter your password
        password_field = driver.find_element(By.ID, 'user_password') 
        password_field.send_keys('CFSPC&EV!')  

        # Find and click the sign-in button
        sign_in_button = driver.find_element(By.ID, 'submit')
        sign_in_button.click()

        print("Logged in successfully!")
    except Exception as e:
        print("Error during login:", e)

    time.sleep(3)

    # Click the myEnlighten button and switch to the new tab
    try:
        myEnlighten_button = driver.find_element(By.ID, 'myenlighten_link')
        myEnlighten_button.click()
        print("Clicked on myEnlighten button.")

        # Wait briefly for the new tab to open
        time.sleep(2)

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last opened tab
        print("Switched to the new tab.")
    except Exception as e:
        print("Error during myEnlighten click or switching tabs:", e)

    time.sleep(5)

    # Locate and click the "Stop" button specifically
    try:
        stop_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div[3]/div/div/div/div/div[3]/div/div[2]/div/div/button'))
        )
        ActionChains(driver).move_to_element(stop_button).click(stop_button).perform()
        print("Stop button clicked successfully!")
        time.sleep(5)
    except Exception as e:
        print("Error finding or clicking the Stop button:", e)

    driver.quit() 

def plugged_in_and_charging():
    # Automatically install and get the path to chromedriver
    driver = uc.Chrome()
    # chromdriver_path = chromedriver_autoinstaller.install()
    # service = Service(chromdriver_path)
    # driver = webdriver.Chrome(service=service)
    # Open the webpage
    driver.get('https://enlighten.enphaseenergy.com')

    # Wait for the page to load
    time.sleep(5)

    ev_connection_status = {}
    # Enter login details
    try:
        email_field = driver.find_element(By.ID, 'user_email') 
        email_field.send_keys('campusfarm@umich.edu') 

        password_field = driver.find_element(By.ID, 'user_password') 
        password_field.send_keys('CFSPC&EV!')  

        sign_in_button = driver.find_element(By.ID, 'submit')
        sign_in_button.click()

        print("Logged in successfully!")
    except Exception as e:
        print("Error during login:", e)

    time.sleep(10)

    # Click the myEnlighten button and switch to the new tab
    try:
        myEnlighten_button = driver.find_element(By.ID, 'myenlighten_link')
        myEnlighten_button.click()
        print("Clicked on myEnlighten button.")

        # Wait briefly for the new tab to open
        time.sleep(3)

        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last opened tab
        print("Switched to the new tab.")
    except Exception as e:
        print("Error during myEnlighten click or switching tabs:", e)

    time.sleep(3)

    max_retries = 3  # Set the maximum number of retries
    attempt = 0

    while attempt < max_retries:

        try:
            attempt += 1
            # Locate the span element using its class name
            status_box = driver.find_element(By.CLASS_NAME, 'ev_info_icon_section')
            
            # Extract the text content
            status_text = status_box.text.strip()
            print(f"Status text: {status_text}")
            
            # Check if the text matches "Not Charging: Manual override"
            if "Not Charging: Manual override" in status_text or "Charging" in status_text or "Not Charging" in status_text:
                connected = True
                print("connected")
                attempt = 4
            else:
                connected = False
                print("not connected")
                attempt = 4

        except Exception as e:
            print("Error checking plug-in status:", e)
            if attempt == max_retries:
                    print("Max retries reached. Exiting...")
                    driver.quit()
                    return None

    ev_connection_status['connected'] = connected
    if connected == False:
        ev_connection_status['charging'] = False
        driver.quit()
        print("Therefore not charging")
        return ev_connection_status

    time.sleep(5)  # Ensure the new tab's content loads completely

        # Wait for the Charge Now button to appear

    try:
        # Locate the "Stop" button using the XPath
        stop_button = driver.find_element(By.XPATH, "//button[contains(@class, 'start-stop-button')]//span[text()='Stop']")
        print("Stop button found! Charging")
        ev_connection_status['charging'] = True
        driver.quit()  # Quit the driver if the button is found
        return ev_connection_status  # Return True if the button is found
    except Exception:
        # Handle the case where the button is not found
        print("Stop button not found. Not charging")
        ev_connection_status['charging'] = False
        driver.quit()  # Quit the driver even if the button is not found
        return ev_connection_status  # Return False if the button is not found