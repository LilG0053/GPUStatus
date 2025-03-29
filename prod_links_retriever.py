from selenium.webdriver.common.by import By
from url_file import urls
import requests
import time
import re
import random
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
            
    def fetch_and_check_products(self, driver):
        # Define search terms
        amazon_search_query = "5070ti"
        newegg_search_query = "5070ti"
        self.get_amazon_product_links(driver, amazon_search_query)
        self.get_newegg_product_links(driver, newegg_search_query)
        amazon_search_query = "9070xt"
        newegg_search_query = "9070xt"
        self.get_amazon_product_links(driver, amazon_search_query)
        self.get_newegg_product_links(driver, newegg_search_query)
        for url in urls:
            if self.is_valid_url(url):
                # If the URL is valid, add it to the set of product links
                self.product_links.add(url)
            else:
                print(f"Skipping invalid url: {url}")
                
        return list(self.product_links) #convert set to list for easier handling
    
    def get_amazon_product_links(self, driver, search_query):
        amazon_url = f"https://www.amazon.com/s?k={search_query}"
        driver.get(amazon_url)
        time.sleep(2)  # wait for the page to load
        try:
            # Look for product links in the search result
            products = driver.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item h2 a")
            for product in products:
                link = product.get_attribute("href")
                # Check if the title contains exactly "5070ti" or "9070xt"
                title_element = product.find_element(By.XPATH, "./ancestor::div[@data-asin]//span[@class='a-text-normal']")
                title = title_element.text.lower()
                if ("5070ti" in title or "9070xt" in title or "9070 xt" in title) and self.is_not_PC(title) and (link not in self.product_links):
                    self.product_links.add(link)  # Add to the set of product links
        except Exception as e:
            print(f"Error extracting Amazon product links: {e}")

    def get_newegg_product_links(self, driver, search_query):
        newegg_url = f"https://www.newegg.com/p/pl?d={search_query}"
        driver.get(newegg_url)
        time.sleep((random.random() * 5) + 10)  # wait for the page to load
        try:
            # Look for product links in the search result
            products = driver.find_elements(By.CSS_SELECTOR, ".item-title")
            for product in products:
                link = product.get_attribute("href")
                title = product.text.lower()
                # Check if the title contains exactly "5070ti" or "9070xt"
                if ("5070ti" in title or "9070xt" in title or "9070 xt" in title) and self.is_not_PC(title) and (link not in self.product_links):
                    self.product_links.add(link)
        except Exception as e:
            print(f"Error extracting Newegg product links: {e}")
    
    def is_not_PC(self, title):
        # Use regular expression to ensure the title doesn't contain "pc" or "gaming pc"
        invalid_keywords = [r"\bpc\b", r"\bgaming pc\b", r"\bdesktop\b", r"\bpc\b"]
        return not any(re.search(keyword, title) for keyword in invalid_keywords)