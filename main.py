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
import cv2
import numpy as np
import pytesseract

# Set Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

        image_found = False
        for i in range(1, 6):  # Try first 5 images
            try:
                # Scroll a bit to load more images
                driver.execute_script("window.scrollBy(0, 200)")
                time.sleep(1)

                # Click the thumbnail
                thumb_xpath = f'(//div[contains(@class,"eA0Zlc")])[{i}]'
                thumb = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, thumb_xpath))
                )
                thumb.click()

                # Wait for full image to load
                full_img = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//img[@jsname="kn3ccd"]'))
                )
                img_url = full_img.get_attribute("src")

                if img_url and img_url.startswith("http"):
                    filename = os.path.join(save_dir, f"{query.replace(' ', '_')}_{i}.jpg")
                    urllib.request.urlretrieve(img_url, filename)

                    # Watermark check
                    img = cv2.imread(filename)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(gray)

                    if len(text.strip()) == 0:
                        msg = f"✅ {city}: Image without watermark saved at {filename}"
                        print(msg)
                        image_found = True
                        break
                    else:
                        print(f"⚠️ {city}: Watermark detected in image {i}, trying next...")

            except Exception as inner_e:
                print(f"⚠️ {city}: Failed to process image {i}: {inner_e}")
                continue

        if not image_found:
            msg = f"❌ {city}: All top 5 images have watermark or failed to load."

    except Exception as e:
        msg = f"❌ {city}: General error - {e}"

    finally:
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(msg + "\n")
        driver.quit()
