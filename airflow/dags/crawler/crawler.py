import os
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import re
from bs4 import BeautifulSoup
from crawler.dns_resolver import resolve_domain
from crawler.url_queue import URLQueue
from crawler.robots_checker import RobotsChecker

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
        self.content_dir = "/content" #đường dẫn lưu ảnh
        self.images_dir = "/images" #đường dẫn lưu content

    def crawl(self):
        domain = self.base_url.split('//', 1)[1].split('/', 1)[0]
        ip = resolve_domain(domain)
        if not ip:
            print(f"Could not resolve domain: {domain}")
            return

        self.url_queue.enqueue(self.base_url)
        while len(self.crawled_urls) < self.max_urls_per_day:
            url = self.url_queue.dequeue()
            if url not in self.crawled_urls and self.robots_checker.is_allowed(url):
                self.process_url(url)

    """
        Hàm để process một đường dẫn nhất định nào đó, lưu lại content của URL đó,
        và extract những ảnh trong URL đó là tìm cách lưu lại ảnh vào đường dẫn.
    """
    def process_url(self, url):
        self.driver.get(url)
        print("The current URL is", url)
        
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
            print("The image URL is", img.get_attribute("src"))
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
    
    """
        Hàm kiểm tra xem đường dẫn ảnh có hợp lệ hay không
    """
    def is_valid_image_url(self, img_url):

        try:
            response = requests.get(img_url, timeout=5)
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                return True
            return False
        except requests.RequestException:
            return False
    
    """
        Hàm kiểm tra xem ảnh đã được lưu trong n_days gần nhất hay chưa.
    """
    def is_image_exists_in_past_n_days(self, image_url, n_days = 10):
        for i in range(n_days):
            check_date = (datetime.today() - timedelta(days = i)).strftime('%d-%m-%Y')
            check_dir = os.path.join(self.images_dir, check_date)
            if not os.path.exists(check_dir):
                continue
            if f"{self._get_file_name_from_url(image_url)}.jpg" in os.listdir(check_dir):
                return True
        return False
    
    """
        Hàm tạo đường dẫn lưu trữ dữ liệu theo ngày
    """
    def create_daily_dir(self, base_dir):
        today = datetime.today().strftime('%d-%m-%Y')
        daily_dir = os.path.join(base_dir, today)
        os.makedirs(daily_dir, exist_ok=True)
        return daily_dir

    """
        Hàm để lưu content vào đường dẫn
    """
    def save_content(self, url, content):

        daily_dir = self.create_daily_dir(self.content_dir)
        file_path = os.path.join(daily_dir, f"{self._get_file_name_from_url(url)}.txt")

        #Kiểm tra xem bài đăng này đã tồn tại trong storage chưa.
        if os.path.exists(file_path):
            print(f"Nội dung đã tồn tại: {file_path}")
            return
        
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Đã lưu nội dung: {file_path}")

    """
        Hàm để lưu ảnh vào đường dẫn
    """
    def save_image(self, img_url):
        
        #Kiểm tra xem đường dẫn của ảnh có hợp lệ không
        if not self.is_valid_image_url(img_url):
            print(f"Đường link {img_url} không hợp lệ.")
            return
       
        daily_dir = self.create_daily_dir(self.images_dir)
        file_path = os.path.join(daily_dir, f"{self._get_file_name_from_url(img_url)}.jpg")

        #Kiểm tra xem ảnh đó đã được fetch trong n ngày trước đó hay chưa
        if self.is_image_exists_in_past_n_days(img_url):
            print(f"Ảnh đã tồn tại: ", f"{self._get_file_name_from_url(img_url)}.jpg")
            return
    
        #Lưu ảnh vào đường dẫn
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Đã lưu ảnh: {file_path}")
    
    def save_url(self, url):
        with open("stored_data/ALL_url.txt", "a") as f:
            f.write(f"{url}\n")
        with open("stored_data/crawled.txt", "a") as f:
            f.write(f"{url},{datetime.now().strftime('%Y-%m-%d')}\n")
    
    def _get_file_name_from_url(self, url):
        return url.split('/')[-1].split('?')[0]

    def close(self):
        self.driver.quit()

# Usage
#if __name__ == "__main__":
    #crawler = WebCrawler("https://www.24h.com.vn/")
    #crawler.crawl()
    #crawler.close()
