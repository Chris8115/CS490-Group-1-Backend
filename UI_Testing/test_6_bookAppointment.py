import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

BASE_URL = "http://localhost:5000"

def test_patient_books_appointment():
    driver = webdriver.Chrome()
    try:
        # Log in
        driver.get("http://localhost:3000/log-in")
        driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))

        # Go to booking page
        driver.get("http://localhost:3000/patient/book-appointment")

        # Fill form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "appointmentReason")))
        driver.find_element(By.ID, "appointmentReason").send_keys("Consultation")
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        driver.find_element(By.ID, "appointmentDate").send_keys(tomorrow.strftime("%m-%d-%Y"))
        driver.find_element(By.ID, "appointmentTime").send_keys("05:00p")

        # Submit
        driver.find_element(By.XPATH, "//button[contains(text(), 'Request Appointment')]").click()
        confirm_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm')]"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Appointment Requested")
        )
        print("Appointment successfully requested.")

    finally:
        driver.quit()
