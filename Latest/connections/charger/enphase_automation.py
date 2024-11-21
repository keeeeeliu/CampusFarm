from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

def charger_on():
    # Automatically install and get the path to chromedriver
    chromedriver_path = chromedriver_autoinstaller.install()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

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

    time.sleep(2)

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

    time.sleep(2)

    try:
        # Using XPath to target the button that contains the "Charge Now" text
        charge_now_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'start-stop-button')]//span[text()='Charge Now']"))
        )
        ActionChains(driver).move_to_element(charge_now_button).click(charge_now_button).perform()
        print("Charge Now button clicked successfully!")
        time.sleep(5)
    except Exception as e:
        print("Error finding or clicking the Charge Now button:", e)

    driver.quit()

def charger_off():
    # Automatically install and get the path to chromedriver
    chromedriver_path = chromedriver_autoinstaller.install()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

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

    time.sleep(2)

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

    time.sleep(2)

    # Locate and click the "Stop" button specifically
    try:
        stop_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'start-stop-button')]//span[text()='Stop']"))
        )
        ActionChains(driver).move_to_element(stop_button).click(stop_button).perform()
        print("Stop button clicked successfully!")
        time.sleep(5)
    except Exception as e:
        print("Error finding or clicking the Stop button:", e)

    driver.quit() 

def plugged_in():
    # Automatically install and get the path to chromedriver
    chromedriver_path = chromedriver_autoinstaller.install()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

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

    time.sleep(2)

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

    time.sleep(2)

        # Check for "Not Plugged-in"
    try:
        # Locate the span containing the status text
        status_box = driver.find_element(By.CLASS_NAME, 'ev_info_icon_section')

        # Get the text from the element
        status_text = status_box.text.strip()

        # Print True if it doesn't say "Not Plugged-in", False otherwise
        if status_text == "Not Plugged-in":
            driver.quit()
            return False
        else:
            driver.quit()
            return True
    except Exception as e:
        print("Error checking plug-in status:", e)

    # Close the browser
    driver.quit()

def check_charging():
    # Automatically install and get the path to chromedriver
    chromedriver_path = chromedriver_autoinstaller.install()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

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

    time.sleep(2)

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

    time.sleep(5)  # Ensure the new tab's content loads completely

        # Wait for the Charge Now button to appear
    try:
        charge_now_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'start-stop-button')]//span[text()='Stop']")
            )
        )
        if charge_now_button.is_displayed():

            print("Stop button is present.")
            driver.quit()
            return True  # Return True if the button is present
    except Exception:
        print("Stop Now button not found.")
        driver.quit()
        return False  # Return False if the button is not present

    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Quit the driver in all cases
        driver.quit()