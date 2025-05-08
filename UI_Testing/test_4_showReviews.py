from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_first_review_text():
    driver = webdriver.Chrome()
    driver.get("http://localhost:3000/log-in")

    # Log in
    driver.find_element(By.ID, "form1").send_keys("Eugene.Krabs@krustykrab.com")
    driver.find_element(By.ID, "form2").send_keys("password")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Wait for dashboard and doctor cards
    WebDriverWait(driver, 10).until(EC.url_contains("/patient/dashboard"))
    cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "doctor-search-card"))
    )

    # Click "Show Reviews" for first doctor
    first_card = cards[0]
    show_reviews_btn = first_card.find_element(By.XPATH, ".//button[contains(text(), 'Show Reviews')]")
    show_reviews_btn.click()


    # Wait for first review div to load and extract its paragraph
    review_text = WebDriverWait(first_card, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".p-3.mt-1.mb-1.bg-light.border.rounded p")
        )
    )

    print("First Review Text: ", review_text.text)


    driver.quit()
