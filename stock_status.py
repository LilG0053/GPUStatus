from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from etext import send_sms_via_email
import message_info
import bcolors as colors
import print_handler
import time
import product as p
import keyboard
import sys
import atexit
import url_file
import random

def send_sms(message):
    send_sms_via_email(message_info.phone_number, strip_non_unicode(message), message_info.provider, message_info.sender_credentials, subject="sent using etext")    
    print("ALERT SENT! GPU IN STOCK!")
    sys.exit()
    
def checkEsc():
    if keyboard.is_pressed("esc"):
        print("Exiting program...")
        driver.quit()
        sys.exit()

def exit_handler():
    #make sure firefox closes when the program exits
    driver.quit()

def try_get_element(driver, by, value):
    try:
        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((by, value)))
        return element
    except Exception as e:
        return None

def get_site_name(url):
    return url.split(".")[1]

def strip_non_unicode(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def process_site(site, driver):
    if site == "amazon":
            try:
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
            prod = p.product(product_name, price_whole + "." + price_frac, unavailable)
    elif site == "newegg":
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
        prod = p.product(product_name, price, unavailable)
    return prod

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]
options = Options()
options.add_argument(f"user-agent={random.choice(user_agents)}")
colors = colors.bcolors()
#options.add_argument("--headless")
options.set_preference("permissions.default.image", 2)  # Disable images
options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Disable flash
driver = webdriver.Firefox(options=options)
atexit.register(exit_handler)
ph = print_handler.ph()
URLs = url_file.urls
print("Hold escape to exit the program. ")
data = {}
unavailable = False
while True:
    #check if user is trying to escape
    checkEsc()
    for idx, URL in enumerate(URLs):  
        checkEsc()
        site = get_site_name(URL)
        driver.get(URL)
        prod = process_site(site, driver)
        data[idx] = prod
        if not prod.name or prod.price == "." or prod.unavailable:
            ph.printNotAvailable(prod.name)
        elif (int(prod.price.split(".")[0]) < 750) and (prod.unavailable == False):
            send_sms(f"{prod.name} is available for ${prod.price}. Find it here: {URL}")
            print(f"{colors.OKGREEN}Product is available{colors.ENDC} for ${prod.price}. Find it here: {URL}")
        else:
            print(f"{colors.OKGREEN}Product is available{colors.ENDC} for ${prod.price}. Find it here: {URL}")
            
#should never execute, but just in case
driver.quit()