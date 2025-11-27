import time, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import sys
CATEGORY_URL = "https://dlpsgame.com/category/ps5"
SPOILER_SELECTOR = '//*[@id="Blog1"]/div/div/div/div[4]/div[2]'
# get the fw from the sys arguments if provided
fw = sys.argv[1] if len(sys.argv) > 1 else None
if fw:
    # fw should be in format "6.xx" or "7.xx" - extracting the major version as int
    FW_VERSION = int(fw.split('.')[0])
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
out = dict() # should be in format {game_title: [versions]}

def get_game_links_from_page():
    """Return all game post links from the current category page."""
    links = []
    posts = driver.find_elements(By.CSS_SELECTOR, "h2.post-title a, h2.entry-title a")
    for p in posts:
        href = p.get_attribute("href")
        if href and "dlpsgame.com" in href:
            links.append(href)
    return links

def scrape_game_page(url):
    driver.get(url)
    time.sleep(2)
    try:
        el = driver.find_element(By.XPATH, SPOILER_SELECTOR)
        #print('debug: ', el.get_attribute('textContent'))
        text = el.get_attribute('textContent').strip()
        print(f"Game: {driver.title}")
        print("Raw text:", text)
        match = re.search(r"Working\s*([0-9xX\.\s—\-]+)", text)
        #match if theres the text "Backport "
        bp_match = re.search(r"Backport\s*([0-9xX\.\s—\-]+)", text) if match else None
        if match:
            raw = match.group(1) + ("-" + bp_match.group(1) if bp_match else "")
            versions = [v.strip() for v in re.split(r"[—\-]", raw) if v.strip()]
            
            print("Versions:", versions)
            if fw:
                compatible = False
                for v in versions:
                    v_major = int(v.split('.')[0].replace('x','0').replace('X','0'))
                    if v_major <= FW_VERSION:
                        compatible = True
                        break
                if compatible:
                    print(f"Compatible with your FW {fw}")
                    out[driver.title] = versions
                    with open("dlps_compatible.txt", "a") as f:
                        f.write(f"{driver.title}: {', '.join(versions)}\n")
                else:
                    print(f"Not compatible with your FW {fw}")
        else:
            print("No 'Working' match found")
    except Exception:
        print("Spoiler span not found")

def scrape_category():
    page_num = 1
    while True:
        url = CATEGORY_URL + f"/page/{page_num}" if page_num > 1 else CATEGORY_URL
        driver.get(url)
        time.sleep(2)
        game_links = get_game_links_from_page()
        if not game_links:
            break
        print(f"\nPage {page_num}: found {len(game_links)} games")
        for link in game_links:
            scrape_game_page(link)
        # check if next page exists
        try:
            driver.find_element(By.LINK_TEXT, str(page_num+1))
            page_num += 1
        except:
            break

try:
    scrape_category()
finally:
    driver.quit()
