from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_doctor_creates_forum_post():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:3000/log-in")

        driver.find_element(By.ID, "form1").send_keys("Sponge.Bob@krustykrab.com")
        driver.find_element(By.ID, "form2").send_keys("SecurePassword!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/doctor/dashboard"))
        driver.get("http://localhost:3000/forums")

        create_post_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "create-post-button"))
        )
        driver.execute_script("arguments[0].click();", create_post_btn)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "create-post-modal"))
        )
        driver.find_element(By.CLASS_NAME, "modal-input").send_keys("Test Forum Post Title")
        driver.find_element(By.CLASS_NAME, "modal-textarea").send_keys("This is an automated test post from Selenium.")
        dropdown = driver.find_element(By.CLASS_NAME, "modal-dropdown")
        for option in dropdown.find_elements(By.TAG_NAME, "option"):
            if option.text.strip() == "Discussion":
                option.click()
                break

        submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
        driver.execute_script("arguments[0].click();", submit_btn)

        WebDriverWait(driver, 10).until(
            EC.url_contains("/post")
        )
        print("✅ Forum post successfully created.")


    finally:
        driver.quit()
