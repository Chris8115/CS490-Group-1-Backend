from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_patient_writes_review():
    driver = webdriver.Chrome()
    try:
        # Log in as patient
        driver.get("http://localhost:3000/log-in")
        driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))

        driver.get("http://localhost:3000/patient/review")

        # Wait for dropdown to populate
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "select"))
        )

        # Select first doctor from dropdown
        select = driver.find_element(By.TAG_NAME, "select")
        options = select.find_elements(By.TAG_NAME, "option")
        assert options, "No doctors found in dropdown"
        options[0].click()

       # Wait for stars to appear by locating spans inside the rating section
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//label[text()='Rating']/following-sibling::div/span"))
        )

        stars = driver.find_elements(By.XPATH, "//label[text()='Rating']/following-sibling::div/span")
        assert len(stars) >= 3, f"Expected at least 3 stars but found {len(stars)}"

        # Click the third star
        driver.execute_script("arguments[0].scrollIntoView(true);", stars[2])
        stars[2].click()



        # Type review text
        driver.find_element(By.ID, "reviewText").send_keys("Best doctor in Bikini Bottom!")

        # Submit
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Confirm submission
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Review successfully submitted.")
        )
        print("✅ Review submitted successfully")
    finally:
        driver.quit()
