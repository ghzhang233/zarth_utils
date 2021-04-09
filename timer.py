import time


class Timer:
    def __init__(self):
        self.start_time = None
        self.last_duration = -1
        self.cumulative_duration = -1

    def clear(self):
        self.__init__()

    def start(self):
        self.start_time = time.time()

    def end(self):
        if self.start_time is not None:
            self.last_duration = time.time() - self.start_time
            self.cumulative_duration += self.last_duration
            self.start_time = None

    def get_last_duration(self, start_again=False):
        if self.start_time is not None:
            self.end()
        if start_again:
            self.start()
        return self.last_duration

    def get_cumulative_duration(self, start_again=False):
        if self.start_time is not None:
            self.end()
        if start_again:
            self.start()
        return self.cumulative_duration
