import time


class Timer:
    def __init__(self):
        self.start_time = None
        self.last_duration = 0
        self.cumulative_duration = 0

    def clear(self):
        self.__init__()

    def start(self):
        self.last_duration = 0
        self.start_time = time.time()

    def __is_timing(self):
        return self.start_time is not None

    def end(self):
        if self.__is_timing():
            self.last_duration = time.time() - self.start_time
            self.cumulative_duration += self.last_duration
            self.start_time = None

    def pause(self):
        if self.__is_timing():
            self.last_duration += time.time() - self.start_time
            self.cumulative_duration += self.last_duration
            self.start_time = None

    def proceed(self):
        self.start_time = time.time()

    def get_last_duration(self, start_again=False):
        if self.__is_timing():
            self.end()
        last_duration = self.last_duration
        if start_again:
            self.start()
        return last_duration

    def get_cumulative_duration(self, start_again=False):
        if self.__is_timing():
            self.end()
        if start_again:
            self.start()
        return self.cumulative_duration
