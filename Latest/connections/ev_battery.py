from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

def check_battery():
    # Automatically install and get the path to chromedriver
    chromedriver_path = chromedriver_autoinstaller.install()
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Open the webpage
    driver.get('https://login.ford.com/4566605f-43a7-400a-946e-89cc9fdb0bd7/B2C_1A_SignInSignUp_en-US/oauth2/v2.0/authorize?redirect_uri=https%3A%2F%2Fwww.ford.com%2Fmyaccount%2F&response_type=code&state=%7B%22policy%22%3A%22email_susi_policy%22%2C%22lang%22%3A%22en_us%22%2C%22state%22%3A%22YWNjb3VudC1kYXNoYm9hcmQ%3D%22%2C%22queryHash%22%3A%22%22%2C%22existingPath%22%3A%22%22%2C%22forwardUrl%22%3A%22%22%7D&client_id=a0c72c3b-8ede-4eff-b66a-f00d31fe3694&scope=a0c72c3b-8ede-4eff-b66a-f00d31fe3694%20openid&code_challenge=3iDcAQwnSzbF35RfAyDRs8E_OMRbQczrudWgxoE_iMQ&code_challenge_method=S256&ui_locales=en-US&template_id=Ford-MFA-Authentication&ford_application_id=b08429de-8440-478d-a323-7a1e05cc9844&country_code=USA&language_code=en-US')

    # Wait for the page to load and email input field to be present
    wait = WebDriverWait(driver, 20)  # Set maximum wait time (in seconds)
    try:
        # Wait for the email input field to become available
        email_field = wait.until(EC.presence_of_element_located((By.ID, 'signInName')))
        email_field.send_keys('campusfarm@umich.edu') 

        # Wait for the password input field to become available
        password_field = wait.until(EC.presence_of_element_located((By.ID, 'password')))
        password_field.send_keys('cFSPC&EV!1')  

        # Wait for the sign-in button to be clickable and click it
        sign_in_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        sign_in_button.click()
        time.sleep(500)

        print("Logged in successfully!")
    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        return

    # Wait for the next page to load and the Charge Level element to be visible
    try:
        charge_level_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="mmota-box2-value"]')))
        charge_level = charge_level_element.text.strip('%')  # Remove the % sign
        print(f"Charge Level: {charge_level}")

        est_distance_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="mmota-box3-value"]')))
        est_distance = est_distance_element.text.strip(' mi')  # Remove the mi suffix
        print(f"Estimated Distance: {est_distance}")
    except Exception as e:
        print("Error extracting data:", e)

    driver.quit()

check_battery()
