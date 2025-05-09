from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--log-level=3")  # Suppresses logs: 0 = ALL, 3 = FATAL
service = Service(log_path='NUL')  # Suppress console output on Windows

def test_patient_submits_daily_survey():
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("http://localhost:3000/log-in")
        driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))

        driver.get("http://localhost:3000/patient/progress")

        # Wait for the daily survey form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "calories")))

        # Fill out and submit the form
        driver.find_element(By.ID, "calories").send_keys("2000")
        driver.find_element(By.ID, "recordedWeight").send_keys("180")
        driver.find_element(By.ID, "waterIntake").send_keys("2.5")

        
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

        try:
            submit_btn.click()
        except Exception as e:
            driver.execute_script("arguments[0].click();", submit_btn)  # Fallback click



        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Daily survey submitted.')]"))
        )


        print("✅ Daily survey submitted successfully.")
    finally:
        driver.quit()
