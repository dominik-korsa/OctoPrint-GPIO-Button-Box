import threading
from time import sleep
from rpi_ws281x import PixelStrip, Color

LED_PIN = 18


class LedManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.state = None
        self.psu_on = False
        self.strip = None

    def start(self):
        self.strip = PixelStrip(2, LED_PIN)
        self.strip.begin()
        self.update_psu_on()
        self.update_printer_state()
        threading.Thread(target=self.thread).start()

    def update_printer_state(self):
        self.state = self.plugin.get_state()
        self.draw_led()

    def update_psu_on(self):
        self.set_psu_on(self.plugin.get_psu_on())

    def set_psu_on(self, psu_on):
        self.psu_on = psu_on
        self.draw_led()

    def thread(self):
        while True:
            self.draw_led()
            sleep(0.02)

    def draw_led(self):
        self.strip.setPixelColor(0, Color(0, 255, 0) if self.psu_on else Color(255, 0, 0))
        self.strip.setPixelColor(1, Color(0, 0, 255))
        self.strip.show()
