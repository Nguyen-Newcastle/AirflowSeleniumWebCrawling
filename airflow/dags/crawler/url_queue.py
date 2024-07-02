from queue import Queue

class URLQueue:
    def __init__(self):
        self.queue = Queue()

    def enqueue(self, url):
        self.queue.put(url)

    def dequeue(self):
        return self.queue.get()

    def is_empty(self):
        return self.queue.empty()

