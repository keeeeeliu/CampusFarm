from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import undetected_chromedriver as uc

# Disable the __del__ method to prevent errors from being printed
uc.Chrome.__del__ = lambda self: None

def check_battery():
    battery = {}
    driver = uc.Chrome()
    driver.get('https://www.ford.com/myaccount/account-dashboard')

    # Wait for the page to load and email input field to be present
    wait = WebDriverWait(driver, 20)  # Set maximum wait time (in seconds)
    try:
        # Wait for the email input field to become available
        email_field = wait.until(EC.presence_of_element_located((By.ID, 'signInName')))
        email_field.send_keys('nelfigs@umich.edu') 

        # Wait for the password input field to become available
        password_field = wait.until(EC.presence_of_element_located((By.ID, 'password')))
        password_field.send_keys('cAmpusFarm$1')  

        # Wait for the sign-in button to be clickable and click it
        sign_in_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        sign_in_button.click()

        print("Logged in successfully!")

       
    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        return

    time.sleep(25)
    # Wait for the next page to load and the Charge Level element to be visible

    try:
        # Increment attempt counter
        
        
        # Wait and extract charge level
        charge_level_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="mmota-box2-value"]')))
        charge_level = charge_level_element.text.strip('%')  # Remove the % sign
        print(f"Charge Level: {charge_level}")

        # Wait and extract estimated distance
        est_distance_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="mmota-box3-value"]')))
        est_distance = est_distance_element.text.strip(' mi')  # Remove the mi suffix
        print(f"Estimated Distance: {est_distance}")

        # Update battery dictionary
        battery['miles_left'] = est_distance
        battery['percentage'] = charge_level
        
        # Close the driver and return data
        driver.quit()
        return battery

    except Exception as e:
        print(f"Attempt {attempt} failed. Error extracting data: {e}")

