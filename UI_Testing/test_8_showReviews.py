from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_first_review_after_switch():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:3000/log-in")

        # Log in as patient
        driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))

        # Click "Switch Doctor"
        switch_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Switch Doctor')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", switch_button)
        driver.execute_script("arguments[0].click();", switch_button)

        time.sleep(1)

        # Wait for and click "Change Doctor"
        change_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Change Doctor')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", change_button)
        driver.execute_script("arguments[0].click();", change_button)

        # Wait for doctor cards to appear again
        cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "doctor-search-card"))
        )

        # Click "Show Reviews" for first doctor
        first_card = cards[0]
        show_reviews_btn = first_card.find_element(By.XPATH, ".//button[contains(text(), 'Show Reviews')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", show_reviews_btn)
        driver.execute_script("arguments[0].click();", show_reviews_btn)

        # Wait for review paragraph to appear
        review_text = WebDriverWait(first_card, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".p-3.mt-1.mb-1.bg-light.border.rounded p")
            )
        )

        print("First Review Text:", review_text.text)

    finally:
        driver.quit()
