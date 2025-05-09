from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_doctor_prescribes_medication():
    driver = webdriver.Chrome()
    try:
        # Log in as doctor
        driver.get("http://localhost:3000/log-in")
        driver.find_element(By.ID, "form1").send_keys("bpoupard0@prlog.org")
        driver.find_element(By.ID, "form2").send_keys("test")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/doctor/dashboard"))

        driver.get("http://localhost:3000/doctor/view-patients")

        first_patient = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "patient-view-name"))
        )
        driver.execute_script("arguments[0].click();", first_patient)

        prescribe_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Prescribe Medication')]"))
        )
        driver.execute_script("arguments[0].click();", prescribe_btn)

        first_med = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.list-group li"))
        )
        driver.execute_script("arguments[0].click();", first_med)

        confirm_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Prescribe')]"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)

        time.sleep(2)
        print("✅ Doctor successfully prescribed medication.")

    finally:
        time.sleep(2)
        driver.quit()
