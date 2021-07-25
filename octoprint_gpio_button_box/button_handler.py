import gpiozero
from time import time


class ButtonHandler:
    def __init__(self, pin, on_short_click, on_long_click=None, long_duration=2):
        self.button = gpiozero.Button(pin)
        self.long_duration = long_duration
        self.press_start = None
        self.button.when_pressed = self.when_pressed
        self.button.when_released = self.when_released
        self.on_short_click = on_short_click
        self.on_long_click = on_long_click

    def when_pressed(self):
        self.press_start = time()

    def when_released(self):
        if self.on_long_click is not None and time() - self.press_start >= self.long_duration:
            self.on_long_click()
        else:
            self.on_short_click()
        self.press_start = None

    def close(self):
        self.button.close()
