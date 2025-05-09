from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_view_pharmacy_product_records():
    driver = webdriver.Chrome()
    try:
        # Log in as pharmacy
        driver.get("http://localhost:3000/pharmacy-log-in")
        driver.find_element(By.ID, "form1").send_keys("3")
        driver.find_element(By.ID, "form2").send_keys("asdfhog")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/pharmacy/dashboard"))

        # Go to product records
        driver.get("http://localhost:3000/pharmacy/records")

        # Wait for product records to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "doctor-search"))
        )

        product_blocks = driver.find_elements(By.CLASS_NAME, "doctor-search")
        for block in product_blocks:
            try:
                product_name = block.find_element(By.TAG_NAME, "h3").text.strip()
                if product_name:
                    print("📦 Product:", product_name)
            except:
                continue

    finally:
        driver.quit()
