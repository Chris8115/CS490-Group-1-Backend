from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_pharmacy_searches_for_patient():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:3000/pharmacy-log-in")
        driver.find_element(By.ID, "form1").send_keys("3")
        driver.find_element(By.ID, "form2").send_keys("asdfhog")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.url_contains("/pharmacy/dashboard")
        )

        # Navigate to patient search
        driver.get("http://localhost:3000/pharmacy/patient-search")

        # Fill out first and last name
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "patientFirstName")))
        driver.find_element(By.ID, "patientFirstName").send_keys("Eugene")
        driver.find_element(By.ID, "patientLastName").send_keys("Krabs")

         # Wait for result
        name_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.doctor-search h3"))
        )

        print("✅ Patient result found:", name_elem.text.strip())
        time.sleep(2)

    finally:
        driver.quit()
