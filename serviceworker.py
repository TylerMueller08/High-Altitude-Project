import threading, utils, time, csv, os

class ServiceWorker(threading.Thread):
    def __init__(self, bme280):
        super().__init__()
        self.bme280 = bme280
        self.running = False

    def start(self):
        self.running = True
        super().start()

    def run(self):
        folder = f"data/{utils.timestamp()}"
        os.makedirs(folder, exist_ok=True)
        csv_file = f"{folder}/data.csv"

        with open(csv_file, "w", newline="") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["Timestamp [MST]", "Altitude [m]", "Temperature[°C]", "Humidity [%]", "Pressure [hPa]"])
            
            utils.log("Service Worker", f"CSV Recording Started at {csv_file}")

            while self.running:
                timestamp = utils.timestamp("%H:%M:%S")
                writer.writerow([
                    timestamp, 
                    round(self.bme280.altitude, 2), 
                    round(self.bme280.temperature, 2), 
                    round(self.bme280.relative_humidity, 2), 
                    round(self.bme280.pressure, 2)
                ])
                time.sleep(1) 

        utils.log("Service Worker", "Recording Stopped.")

    def stop(self):
        self.running = False