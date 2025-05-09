from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_patient_login():
    driver = webdriver.Chrome()
    driver.get("http://localhost:3000/log-in")


    # Fill login form
    driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
    driver.find_element(By.ID, "form2").send_keys("password")

    # Submit login
    login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
    driver.execute_script("arguments[0].click();", login_btn)

    print("✅ Patient logged in successfully.")
    # Wait for redirect to dashboard
    WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))


    assert "/patient/dashboard" in driver.current_url

    driver.quit()
