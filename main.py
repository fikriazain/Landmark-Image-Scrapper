from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request
import os
import time
import pandas as pd


df = pd.read_excel('city_image_download_summary.xlsx')
city_list = df['CITY'].unique()

save_dir = "downloaded_images"
os.makedirs(save_dir, exist_ok=True)

log_path = "log.txt"
with open(log_path, "w") as log:
    log.write("City Image Download Log\n")
    log.write("========================\n\n")

for city in city_list:
    query = city + ' Landmark'
    print(f"🔍 Processing: {query}")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"
        driver.get(search_url)

        first_card = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '(//div[contains(@class,"eA0Zlc")])[1]'))
        )
        first_card.click()

        full_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//img[@jsname="kn3ccd"]'))
        )
        img_url = full_img.get_attribute("src")

        if img_url and img_url.startswith("http"):
            filename = os.path.join(save_dir, f"{query.replace(' ', '_')}.jpg")
            urllib.request.urlretrieve(img_url, filename)
            msg = f"✅ {city}: Image saved to {filename}"
            print(msg)
        else:
            msg = f"❌ {city}: No valid image URL found."

    except Exception as e:
        msg = f"❌ {city}: Error - {e}"

    finally:
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(msg + "\n")
        driver.quit()