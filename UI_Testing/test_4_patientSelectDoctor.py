from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_patient_chooses_doctor():
    driver = webdriver.Chrome()
    try:
        # Log in as patient
        driver.get("http://localhost:3000/log-in")
        driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("password")
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].click();", login_btn)

        # Wait for dashboard redirect
        WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))

        # Wait for at least one doctor card to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "doctor-search-card")
        ))

        # Find the first "Choose Doctor" button and click it
        choose_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Choose Doctor')]")
        assert choose_buttons, "No 'Choose Doctor' buttons found"
        driver.execute_script("arguments[0].click();", choose_buttons[0])

        # Wait briefly for relationship to be established
        time.sleep(3)

        print("Doctor selection successful.")

    finally:
        driver.quit()
