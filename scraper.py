from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from etext import send_sms_via_email
import prod_links_retriever
import asyncio
import bcolors as colors
import logger
import time
import product as p
import keyboard
import atexit
import random
import concurrent.futures
import threading
import asyncio
import gpu_discord_bot
import sys


#Global shared event to notify threads to exit
exit_event = threading.Event()
#global colors bc im lazy
colors = colors.bcolors()

gpu_discord_bot = gpu_discord_bot.gpu_discord_bot()

def checkEsc():
    if keyboard.is_pressed("esc"):
        print("Exiting program...")
        exit_event.set()

def exit_handler():
    #make sure firefox closes when the program exits
    print("Exiting and quitting all drivers")

def try_get_element(driver, by, value):
    try:
        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((by, value)))
        return element
    except Exception as e:
        return None

def get_site_name(url):
    try:
        return url.split(".")[1]
    except:
        raise Exception("Unable to get site name from URL: " + str(url))

def strip_non_unicode(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def scrape_amazon(driver):
    try:
        time.sleep(0.746)
        raw_product_name = WebDriverWait(driver, 1).until(
                        EC.visibility_of_element_located((By.ID, "title"))
                    ).text
    except:
        raw_product_name = WebDriverWait(driver, 1).until(
                        EC.visibility_of_element_located((By.TAG_NAME, "title"))
                    ).text
        #strip product name of weird characters
    product_name = raw_product_name.replace("(", "").replace(")", "").replace(",", "")
    price_whole = driver.find_element(By.CLASS_NAME, "a-price-whole").text
    price_frac = driver.find_element(By.CLASS_NAME, "a-price-fraction").text
        #check if theres a learn more button, if so, product is unavailable
    unavailable = driver.find_elements(By.ID, "fod-cx-message-with-learn-more")
    if not unavailable:
        try:
            unavailable = WebDriverWait(driver, 0).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Currently unavailable.')]"))
                ).text
        except:
            unavailable = False
    return p.product(product_name, price_whole + "." + price_frac, unavailable)
    
def scrape_newegg(driver):
    try:
        time.sleep(1)
        raw_product_name = WebDriverWait(driver, 1).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "product-title"))).text
    except:
            #captcha is present, need to solve it
        time.sleep(random.random() * 2)
        actions = ActionChains(driver)
        captcha_box = driver.find_element(By.NAME, "check")
            #moving mouse to captcha box and clicking it actually solves the captcha
        actions.move_to_element(captcha_box).click().perform()
        time.sleep(20)
        raw_product_name = WebDriverWait(driver, 7).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "product-title"))).text
        #strip product name of weird characters
    product_name = raw_product_name.replace("(", "").replace(")", "").replace(",", "")
    price = driver.find_element(By.CLASS_NAME, "price-current").find_element(By.TAG_NAME, "strong").text
    unavailable = driver.find_element(By.CLASS_NAME, "message-information").text
    return p.product(product_name, price, unavailable)

def scrape_bestbuy(driver):
    try:
        time.sleep(1)
        raw_product_name = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                    ).text
    except:
        print("Unable to find product name on Best Buy page.")
    product_name = raw_product_name.replace("(", "").replace(")", "").replace(",", "").replace("-", "")
    try:
        price = WebDriverWait(driver, 1). EC.visibility_of_element_located((By.CLASS_NAME, "priceView-hero-price")).find_element(By.TAG_NAME, "span").text
    except:
        price = price = WebDriverWait(driver, 1). EC.visibility_of_element_located((By.ID, "large-customer-price")).find_element(By.TAG_NAME, "span").text
        print("bestbu issue, popup?")
    try:
        btn_text = driver.find_element(By.XPATH, "//button[contains(@class, 'add-to-cart-button')]").text
    except:
        print("button not found Bestbuy")
        btn_text = driver.find_element(By.XPATH, "//button[contains(@class, 'c-button-primary')]").text
    unavailable = btn_text == "Coming Soon" or btn_text == "Unavailable Nearby" or btn_text == "Sold Out"
    prod = p.product(product_name, price, unavailable)
    return prod

def process_site(site, driver):
    if site == "amazon":
        prod = scrape_amazon(driver)
    elif site == "newegg":
        prod = scrape_newegg(driver)
    elif site == "bestbuy":
        prod = scrape_bestbuy(driver)
    else:
        raise Exception("Unknown site for site name: " + site)
    return prod

def create_driver():
    user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6301.195 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6267.195 Safari/537.36 OPR/103.0.4784.198',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
    ]
    options = Options()
    options.set_preference("dom.geo.enabled", False)
    options.set_preference("permissions.default.geo", 2)
    options.set_preference("dom.push.enabled", False)
    options.set_preference("dom.webnotifications.enabled", False)  # Disable notifications
    options.set_preference("dom.webdriver.enabled", False)  # Disable webdriver flag
    options.set_preference("permissions.default.image", 2)  # Disable webdriver flag
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    return webdriver.Firefox(options=options)

def product_communication(ph, URL, prod):
    #OO abuser, fix this later
    if not prod.name or prod.price == "." or prod.unavailable:
        ph.printNotAvailable(prod.name)
    elif (int(prod.price.split(".")[0].replace(",", "")) < 1200) and (prod.unavailable == False) and ("5080" in prod.name.split(" ")):
        print(f"{colors.OKGREEN}Product is available{colors.ENDC}: {prod.name} for {colors.OKCYAN}${prod.price}{colors.ENDC}. Find it here: {URL}")
        asyncio.run(gpu_discord_bot.send_discord_message(f"GPU ALERT: {URL}. Product: {prod.name}.", URL))
        print("Sending bot message for 5080...")
    elif (int(prod.price.split(".")[0].replace(",", "")) < 890) and (prod.unavailable == False) and ("9070" in prod.name.split(" ") or "9070XT" in prod.name.split(" ") or "9070 XT" in prod.name.split(" ")):
        print(f"{colors.OKGREEN}Product is available{colors.ENDC}: {prod.name} for {colors.OKCYAN}${prod.price}{colors.ENDC}. Find it here: {URL}")
        asyncio.run(gpu_discord_bot.send_discord_message(f"GPU ALERT: {URL}. Product: {prod.name}.", URL))
        print("Sending bot message for 7090XT...")
    elif (int(prod.price.split(".")[0].replace(",", "")) < 900) and (prod.unavailable == False):
        print(f"{colors.OKGREEN}Product is available{colors.ENDC}: {prod.name} for {colors.OKCYAN}${prod.price}{colors.ENDC}. Find it here: {URL}")
        asyncio.run(gpu_discord_bot.send_discord_message(f"GPU ALERT: {URL}. Product: {prod.name}.", URL))
        print("Sending bot message for 5070ti with price: " + str(prod.price) + "...")
    else:
        print(f"{colors.OKGREEN}Product is available{colors.ENDC}: {prod.name} for {colors.OKCYAN}${prod.price}{colors.ENDC}. Find it here: {URL}")
        
def process_product_chunk(driver, chunk, ph):
    driver = create_driver()  # Create one driver per chunk
    while True:
        for i, URL in enumerate(chunk):
            print("debug index: " + str(i))
            print(f"Checking {URL}...") 
            checkEsc()
            if exit_event.is_set():
                print("Exiting program...")
                driver.quit()
                return
            site = get_site_name(URL)
            driver.get(URL)
            prod = process_site(site, driver)
            product_communication(ph, URL, prod)

def execute_concurrent_processing(driver, ph, URLs, chunk_size):
    with concurrent.futures.ThreadPoolExecutor(max_workers=chunk_size) as executor:
        while True:
            if exit_event.is_set():  # Check if exit event is triggered
                print("Exiting program due to escape key press.")
                break  # Exit the loop and terminate the program
            futures = []
            for i in range(0, len(URLs), len(URLs) // chunk_size):
                chunk = URLs[i:i + (len(URLs) // chunk_size)]
                futures.append(executor.submit(process_product_chunk, driver, chunk, ph))

            # Wait for all futures to complete
            concurrent.futures.wait(futures)
            time.sleep(1)
    
    
#options.add_argument("--headless")
# options.set_preference("permissions.default.image", 2)  # Disable images
# options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Disable flash

def main():
    skip_collection = False
    #if argument is passed, skip the collection of product links
    if sys.argv[1] == "SKIP":
        skip_collection = True
        
    asyncio.run(gpu_discord_bot.send_discord_message("Scanning for GPUs..."))
    driver = create_driver()
    atexit.register(exit_handler)
    ph = logger.ph()
    plr = prod_links_retriever.link_retriever()
    URLs = plr.fetch_and_check_products(driver, skip_collection)
    print("Hold escape to exit the program. ")
    chunk_size = 3
    driver.quit()
    execute_concurrent_processing(driver, ph, URLs, chunk_size)
    print("All threads have finished. Exiting the program.")


if __name__ == "__main__":
    main()
                