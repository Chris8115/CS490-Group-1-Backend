from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_pharmacy_accepts_order():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:3000/pharmacy-log-in")
        
        driver.find_element(By.ID, "form1").send_keys("3")
        driver.find_element(By.ID, "form2").send_keys("asdfhog")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/pharmacy/dashboard"))

        driver.get("http://localhost:3000/pharmacy/deliveries")

        time.sleep(3)

        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept Order')]"))
        )
        driver.execute_script("arguments[0].click();", accept_button)

        print("✅ Order accepted successfully.")

    finally:
        time.sleep(2)
        driver.quit()
