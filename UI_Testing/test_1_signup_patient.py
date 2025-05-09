from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

def test_patient_registration():
    driver = webdriver.Chrome()
    driver.get("http://localhost:3000/sign-up")

    # Click the "Patient" button
    driver.find_element(By.XPATH, "//button[contains(text(), 'Patient')]").click()

    # Basic Info
    driver.find_element(By.NAME, "first_name").send_keys("Eugene")
    driver.find_element(By.NAME, "last_name").send_keys("Krabs")
    driver.find_element(By.NAME, "email").send_keys("Eugene.Krabs@krustykrab.com")
    driver.find_element(By.NAME, "phone_number").send_keys("1234567890")
    driver.find_element(By.NAME, "password").send_keys("password")
    # find the second password field by label text 
    driver.find_element(By.XPATH, "//label[contains(text(),'Confirm Password')]/following-sibling::input").send_keys("password")


    # Upload ID
    import os

    # Convert your relative path to absolute
    file_path = os.path.abspath("UI_Testing/assets/fake-id.png")

    driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(file_path)


    # SSN
    driver.find_element(By.NAME, "ssn").send_keys("123456789")

    # Address
    driver.find_element(By.NAME, "address").send_keys("3451 Anchor Way")
    driver.find_element(By.NAME, "address2").send_keys("")
    driver.find_element(By.NAME, "city").send_keys("Bikini Bottom")
    driver.find_element(By.NAME, "state").send_keys("Pacific Ocean")
    driver.find_element(By.NAME, "country").send_keys("Underwater")
    driver.find_element(By.NAME, "zip").send_keys("12345")

    # Credit card
    driver.find_element(By.NAME, "cardnumber").send_keys("4111111111111111")
    driver.find_element(By.NAME, "cvv").send_keys("123")
    driver.find_element(By.NAME, "exp_date").send_keys("2025-12")

    # Medical History
    element = driver.find_element(By.NAME, "alcoholAddiction")
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    driver.execute_script("arguments[0].click();", element)


    driver.find_element(By.NAME, "additional").send_keys("No known allergies")

   # EULA
    driver.find_element(By.NAME, "eulaName").send_keys("Eugene Krabs")
    today = datetime.date.today().strftime('%Y-%m-%d')
    driver.find_element(By.NAME, "date").send_keys(today)

    # Submit
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    driver.execute_script("arguments[0].click();", submit_button)


    WebDriverWait(driver, 10).until(EC.url_contains("/log-in"))
    print("Patient registered successfully.")
    
    assert "/log-in" in driver.current_url

    driver.quit()
