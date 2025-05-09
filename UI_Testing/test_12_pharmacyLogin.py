from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_pharmacy_login():
    driver = webdriver.Chrome()
    try:
        # Navigate to the pharmacy login page
        driver.get("http://localhost:3000/pharmacy-log-in")

        # Enter credentials
        driver.find_element(By.ID, "form1").send_keys("3")  # Pharmacist ID
        driver.find_element(By.ID, "form2").send_keys("asdfhog")  # Password

        # Submit the form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for dashboard navigation
        WebDriverWait(driver, 10).until(
            EC.url_contains("/pharmacy/dashboard")
        )

        print("✅ Pharmacy login successful.")
    finally:
        driver.quit()
