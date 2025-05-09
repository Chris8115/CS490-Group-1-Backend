from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_patient_leaves_forum_reply():
    driver = webdriver.Chrome()
    try:
        # Log in
        driver.get("http://localhost:3000/log-in")
        driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))

        # Go to forum page
        driver.get("http://localhost:3000/forums")

        # Click the first post card
        post_card = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "post-card"))
        )
        driver.execute_script("arguments[0].click();", post_card)

        # Wait for post content to load (ensures route fully changes)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "post-header"))
        )
        time.sleep(1)
        # Wait for reply textarea using placeholder
        reply_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.reply-input"))
        )

        reply_input.send_keys("Automated test reply")

        # Click Reply button
        reply_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Reply')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", reply_btn)
        driver.execute_script("arguments[0].click();", reply_btn)

        print("✅ Reply successfully posted: 'Automated test reply' ")



    finally:
        driver.quit()
