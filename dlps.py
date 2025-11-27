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
    # delete dlps_compatible.txt if exists becuase we will create a new one
    import os
    if os.path.exists("dlps_compatible.txt"):
        os.remove("dlps_compatible.txt")
 
options = webdriver.ChromeOptions()
#options.add_argument("--headless")
driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
out = dict() # should be in format {game_title: [versions]}

def get_game_links_from_page():
    """Return all game post links from the current category page."""
    links = []
    posts = driver.find_elements(By.CSS_SELECTOR, "h2.post-title a, h2.entry-title a, article .entry-title a, .post .entry-title a")
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
                        f.write(f"{driver.title.replace('Download Game PSX PS2 PS3 PS4 PS5', '')}: {', '.join(versions)}\n")
                else:
                    print(f"Not compatible with your FW {fw}")
        else:
            print("No 'Working' match found")
    except Exception:
        print("Spoiler span not found")

def scrape_category():
    page_num = 1
    MAX_PAGES = 200
    while True:
        # build a sequential /page/N/ URL (with trailing slash)
        url = CATEGORY_URL.rstrip('/') + (f"/page/{page_num}/" if page_num > 1 else '/')
        driver.get(url)
        time.sleep(2)

        game_links = get_game_links_from_page()
        if not game_links:
            print(f"No game links found on {url}; stopping")
            break
        print(f"\nPage {page_num}: found {len(game_links)} games")
        for link in game_links:
            scrape_game_page(link)

        # safety: if requesting a page redirected back to category root, stop
        try:
            current = driver.current_url.rstrip('/')
            root = CATEGORY_URL.rstrip('/')
            if page_num > 1 and current == root:
                print(f"Request for page {page_num} ({url}) redirected to category root; stopping")
                break
        except Exception:
            pass

        page_num += 1
        if page_num > MAX_PAGES:
            print(f"Reached page limit ({MAX_PAGES}); stopping")
            break

try:
    scrape_category()
finally:
    driver.quit()
