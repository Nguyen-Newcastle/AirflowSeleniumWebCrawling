import requests
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

class RobotsChecker:
    def __init__(self):
        self.cache = {}

    def is_allowed(self, url):
        domain = url.split('//', 1)[1].split('/', 1)[0]
        if domain not in self.cache:
            robots_url = urljoin(f"http://{domain}", "/robots.txt")
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.cache[domain] = rp
        return self.cache[domain].can_fetch('*', url)
