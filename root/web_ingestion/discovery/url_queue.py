from collections import deque


class URLQueue:
    def __init__(self):
        self.queue = deque()
        self.seen = set()

    def add_many(self, urls):
        for u in urls:
            if u not in self.seen:
                self.queue.append(u)
                self.seen.add(u)

    def next(self):
        return self.queue.popleft()

    def has_next(self):
        return len(self.queue) > 0
