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

       # Wait for the table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Get all rows from tbody
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                product_name = cells[1].text.strip()
                print(f"📦 Product: {product_name}")

    finally:
        driver.quit()
