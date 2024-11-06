from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

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

# Locate the "Edit Schedule" button and click it
try:
    edit_schedule_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'edit-schedule-label'))
    )
    ActionChains(driver).move_to_element(edit_schedule_button).click(edit_schedule_button).perform()
    print("Edit Schedule button clicked successfully!")
except Exception as e:
    print("Error finding or clicking the Edit Schedule button:", e)

# Optional: Close the browser after a delay
time.sleep(3)
driver.quit()
