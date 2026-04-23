import board
from adafruit_bme280 import basic as adafruit_bme280
from serviceworker import ServiceWorker

class ServiceHandler:
    def __init__(self):
        self.i2c = board.I2C()
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
        self.bme280.sea_level_pressure = 1013.25

    def start(self):
        self.worker = ServiceWorker(bme280=self.bme280)
        self.worker.start()
        print("Started BioAltitude Services.")

    def stop(self):
        if hasattr(self, "worker"):
            self.worker.stop()
            self.worker.wait()
        print("Stopped BioAltitude Services.")