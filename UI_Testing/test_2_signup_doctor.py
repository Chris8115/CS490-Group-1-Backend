# UI_Testing/test_signup_doctor.py

import os
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

def test_doctor_registration():
    driver = webdriver.Chrome()
    driver.get("http://localhost:3000/sign-up")

    # Click the "Doctor" button
    driver.find_element(By.XPATH, "//button[contains(text(), 'Doctor')]").click()

    # Basic Info
    driver.find_element(By.NAME, "first_name").send_keys("Sponge")
    driver.find_element(By.NAME, "last_name").send_keys("Bob")
    driver.find_element(By.NAME, "email").send_keys("Sponge.Bob@krustykrab.com")
    driver.find_element(By.NAME, "phone_number").send_keys("1234567899")
    driver.find_element(By.NAME, "password").send_keys("password")

    # Confirm password
    driver.find_element(By.XPATH, "//label[contains(text(),'Confirm Password')]/following-sibling::input").send_keys("password")

    # Upload profile picture
    profile_pic_path = os.path.abspath("UI_Testing/assets/fake-profile.png")
    driver.find_element(By.XPATH, "//label[contains(text(),'Upload Profile Picture')]/following-sibling::input").send_keys(profile_pic_path)

    # Short Bio
    driver.find_element(By.NAME, "profile").send_keys("Experienced fry cook with 10 years of practice.")

    # Specialization
    driver.find_element(By.NAME, "specialization").send_keys("Grilling, Burgers")

    # Identification Upload
    id_path = os.path.abspath("UI_Testing/assets/fake-id.png")
    driver.find_element(By.XPATH, "//label[contains(text(),'Upload Identification')]/following-sibling::input").send_keys(id_path)

    # Medical License
    driver.find_element(By.NAME, "license_number").send_keys("123456789")

    # Address Info
    driver.find_element(By.NAME, "address").send_keys("124 Conch Street")
    driver.find_element(By.NAME, "address2").send_keys("Pineapple")
    driver.find_element(By.NAME, "city").send_keys("Bikini Bottom")
    driver.find_element(By.NAME, "state").send_keys("Pacific Ocean")
    driver.find_element(By.NAME, "country").send_keys("Underwater")
    driver.find_element(By.NAME, "zip").send_keys("12345")

    # Office location
    driver.find_element(By.NAME, "office").send_keys("Krusty Krab")

    # EULA Section
    driver.find_element(By.NAME, "eulaName").send_keys("Sponge Bob")
    today = datetime.date.today().strftime('%Y-%m-%d')
    driver.find_element(By.NAME, "date").send_keys(today)

    # Submit
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    driver.execute_script("arguments[0].click();", submit_button)

    WebDriverWait(driver, 10).until(EC.url_contains("/log-in"))

    assert "/log-in" in driver.current_url
    
