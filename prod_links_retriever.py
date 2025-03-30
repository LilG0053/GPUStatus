from selenium.webdriver.common.by import By
from url_file import urls
import requests
import time
import re
import random
import json
class link_retriever:
    def __init__(self):
        self.product_links = set()
    
    def is_valid_url(self, url):
        #Check if a URL is valid by sending a request to the link.
        try:
            # Make a GET request instead of HEAD, to follow redirects and get the final response
            response = requests.get(url, timeout=5, allow_redirects=True)
            # Check if the status code indicates a valid page
            if response.status_code == 200 or response.status_code == 500:
                return True
            else:
                print(f"URL {url} returned status code {response.status_code}. Skipping.")
                return False
        except requests.RequestException as e:
            print(f"Error with URL {url}: {e}")
            return False  # Invalid URL if there's an error or if the request fails
    
    def get_amazon_product_links(self, driver, search_query):
        amazon_url = f"https://www.amazon.com/s?k={search_query}"
        driver.get(amazon_url)
        time.sleep((random.random() * 5))  # wait for the page to load
        try:
            # Look for product links in the search result
            products = driver.find_elements(By.XPATH, "//a[@class='a-link-normal s-line-clamp-2 s-link-style a-text-normal']")
            for product in products:
                print(product.text)
                link = product.get_attribute("href")
                # Check if the title contains exactly "5070ti" or "9070xt"
                title = product.text.lower()
                if ("5070ti" in title or "9070xt" in title or "9070 xt" in title or "5070 ti" in title) and self.is_not_PC(title) and (link not in self.product_links):
                    self.product_links.add(link)  # Add to the set of product links
                    print(f"Found Amazon product link: {link}")
        except Exception as e:
            print(f"Error extracting Amazon product links: {e}")

    def get_newegg_product_links(self, driver, search_query):
        newegg_url = f"https://www.newegg.com/p/pl?d={search_query}"
        driver.get(newegg_url)
        time.sleep((random.random() * 5) + 10)  # throw off bot detection
        try:
            # Look for product links in the search result
            products = driver.find_elements(By.CSS_SELECTOR, ".item-title")
            for product in products:
                link = product.get_attribute("href")
                title = product.text.lower()
                # Check if the title contains exactly "5070ti" or "9070xt"
                if ("5070ti" in title or "9070xt" in title or "9070 xt" in title or "5070 ti" in title) and self.is_not_PC(title) and (link not in self.product_links):
                    self.product_links.add(link)
                    print(f"Found Newegg product link: {link}")
        except Exception as e:
            print(f"Error extracting Newegg product links: {e}")
    
    def get_bestbuy_product_links(self, driver, search_query):
        bestbuy_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={search_query}"
        driver.get(bestbuy_url)
        time.sleep((random.random() * 5) + 3)  # throw off bot detection
        
        try:
            #get product links
            products = driver.find_elements(By.CLASS_NAME, "sku-title")
            for product in products:
                product = product.find_element(By.TAG_NAME, "a")
                link = product.get_attribute("href")
                title = product.text.lower()
                # Check if the title contains exactly "5070ti" or "9070xt"
                if ("5070ti" in title or "9070xt" in title or "9070 xt" in title or "5070 ti" in title) and self.is_not_PC(title) and (link not in self.product_links):
                    self.product_links.add(link)
                    print(f"Found Best Buy product link: {link}")
        except Exception as e:
            print(f"Error extracting Best Buy product links: {e}")
            
    def save_and_load_urls_to_file(self, new_url_list, filename='backup_urls.json'):
        try:
            with open(filename, 'r') as f:
                existing_urls = set(json.load(f))
            print(f"New URLs saved to {filename}")
        except (FileNotFoundError, json.JSONDecodeError):
            existing_urls = set()
        
        new_urls_to_save = [url for url in new_url_list if url not in existing_urls]
        
        if new_urls_to_save:
            existing_urls.update(new_urls_to_save)
            
            with open(filename, 'w') as f:
                json.dump(list(existing_urls), f)
            print(f"Added {len(new_urls_to_save)} new URLs to {filename}")
        else:
            print("No new URLs to save.")
        
        return list(existing_urls)
                        
    def fetch_and_check_products(self, driver):
        # define search terms
        ti_search_query = "5070ti"
        self.get_bestbuy_product_links(driver, ti_search_query)
        self.get_amazon_product_links(driver, ti_search_query)
        self.get_newegg_product_links(driver, ti_search_query)
        xt_search_query = "9070xt"
        self.get_bestbuy_product_links(driver, xt_search_query)
        self.get_amazon_product_links(driver, xt_search_query)
        self.get_newegg_product_links(driver, xt_search_query)
        for url in urls:
            time.sleep(random.random() * 0.1)  # dont spam with requests
            if self.is_valid_url(url):
                # If the URL is valid, add it to the set of product links
                self.product_links.add(url)
            else:
                print(f"Skipping invalid url: {url}")
        print(f"Total product links found: {len(self.product_links)}")
        return self.save_and_load_urls_to_file(self.product_links, 'backup_urls.json')
    
    def is_not_PC(self, title):
        # Use regular expression to ensure the title doesn't contain "pc" or "gaming pc"
        invalid_keywords = [r"\bgaming pc\b", r"\bdesktop\b", r"\bcomputer\b", r"\blaptop\b"]
        return not any(re.search(keyword, title) for keyword in invalid_keywords)