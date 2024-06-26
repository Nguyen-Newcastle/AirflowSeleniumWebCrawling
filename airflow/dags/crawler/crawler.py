import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from bs4 import BeautifulSoup
from dns_resolver import resolve_domain
from url_queue import URLQueue
from robots_checker import RobotsChecker

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.driver = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        self.url_queue = URLQueue()
        self.robots_checker = RobotsChecker()
        self.crawled_urls = set()
        self.max_urls_per_day = 100

    def crawl(self):
        domain = self.base_url.split('//', 1)[1].split('/', 1)[0]
        ip = resolve_domain(domain)
        if not ip:
            print(f"Could not resolve domain: {domain}")
            return

        self.url_queue.enqueue(self.base_url)
        while len(self.crawled_urls) < self.max_urls_per_day and not self.url_queue.is_empty():
            url = self.url_queue.dequeue().decode('utf-8')
            if url not in self.crawled_urls and self.robots_checker.is_allowed(url):
                self.process_url(url)

    def process_url(self, url):
        self.driver.get(url)
        
        # URL Check
        if self.driver.current_url != url:
            print(f"URL redirected: {url} -> {self.driver.current_url}")
            return

        # Content Check
        if not self.is_valid_content():
            print(f"Invalid content for URL: {url}")
            return

        # Extract and save content
        content = self.driver.find_element(By.TAG_NAME, "body").text
        self.save_content(url, content)
        
        # Extract and save images
        images = self.driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            self.save_image(img.get_attribute("src"))
        
        # Extract and save URLs
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for link in soup.find_all('a', href=True):
            new_url = link['href']
            if new_url.startswith(self.base_url):
                self.url_queue.enqueue(new_url)
        
        self.save_url(url)
        self.crawled_urls.add(url)

    def is_valid_content(self):
        # Implement your content validation logic here
        return True

    def save_content(self, url, content):
        filename = f"content/{url.replace('/', '_')}.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def save_image(self, img_url):
        filename = f"images/{img_url.split('/')[-1]}"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(requests.get(img_url).content)

    def save_url(self, url):
        with open("ALL_url.txt", "a") as f:
            f.write(f"{url}\n")
        with open("crawled.txt", "a") as f:
            f.write(f"{url},{datetime.now().strftime('%Y-%m-%d')}\n")

    def close(self):
        self.driver.quit()

# Usage
#if __name__ == "__main__":
    #crawler = WebCrawler("https://www.24h.com.vn/")
    #crawler.crawl()
    #crawler.close()
