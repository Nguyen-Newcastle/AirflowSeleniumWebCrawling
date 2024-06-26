import redis

class URLQueue:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def enqueue(self, url):
        self.redis.lpush('url_queue', url)

    def dequeue(self):
        return self.redis.rpop('url_queue')

    def is_empty(self):
        return self.redis.llen('url_queue') == 0
