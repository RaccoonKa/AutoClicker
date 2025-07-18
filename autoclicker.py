import threading
import pyautogui
import time


class AutoClicker:
    def __init__(self):
        self.points = []
        self.interval = 1.0
        self.running = False
        self.thread = None
        self.hotkey_enabled = True
        self.click_delay = 0.01
        self.second_points = []
        self.second_interval = 0.5
        self.click_delay = 0.01
        self.transition_delay = 2.0
        self.point_delay = 0.0
        self.second_point_delay = 0.0

    def add_point(self, x, y):
        self.points.append((x, y))

    def set_interval(self, interval):
        self.interval = max(0.0, interval)

    def start(self):
        if not self.running and self.points:
            self.running = True
            self.thread = threading.Thread(target=self._click_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
        return False

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.1)
            self.thread = None

    def _click_loop(self):
        while self.running:
            for point in self.points:
                if not self.running:
                    return
                x, y = point
                pyautogui.mouseDown(x, y)
                time.sleep(self.click_delay)
                if self.point_delay > 0:
                    time.sleep(self.point_delay)

            for point in self.points:
                if not self.running:
                    return
                x, y = point
                pyautogui.mouseUp(x, y)
                time.sleep(self.click_delay)
                if self.point_delay > 0:
                    time.sleep(self.point_delay)
            time.sleep(self.interval)

    def toggle_hotkey(self, state):
        self.hotkey_enabled = state

    def add_second_point(self, x, y):
        self.second_points.append((x, y))

    def set_second_interval(self, interval):
        self.second_interval = max(0.0, interval)

    def execute_second_algorithm(self):
        time.sleep(self.transition_delay)
        for point in self.second_points:
            x, y = point
            pyautogui.mouseDown(x, y)
            time.sleep(self.click_delay)
            if self.second_point_delay > 0:
                time.sleep(self.second_point_delay)

        for point in self.second_points:
            x, y = point
            pyautogui.mouseUp(x, y)
            time.sleep(self.click_delay)
            if self.second_point_delay > 0:
                time.sleep(self.second_point_delay)

        time.sleep(self.second_interval)
