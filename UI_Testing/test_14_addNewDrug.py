from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uuid

def test_add_pharmacy_product():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:3000/pharmacy-log-in")
        driver.find_element(By.ID, "form1").send_keys("3")
        driver.find_element(By.ID, "form2").send_keys("asdfhog")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.url_contains("/pharmacy/dashboard")
        )

        driver.get("http://localhost:3000/pharmacy/add-product")

        unique_name = f"TestProduct_{uuid.uuid4().hex[:6]}"
        driver.find_element(By.ID, "productName").send_keys(unique_name)
        driver.find_element(By.ID, "productDescription").send_keys("Automated test product")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Product Successfully Added")
        )
        print(f"✅ Product '{unique_name}' added successfully.")
        time.sleep(2)
    finally:
        driver.quit()
