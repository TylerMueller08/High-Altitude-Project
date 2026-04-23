import threading, utils, time, csv, cv2, os

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

        video_file = f"{folder}/video.mp4"
        csv_file = f"{folder}/data.csv"

        csvf = open(csv_file, "w", newline="")
        writer = csv.writer(csvf)
        writer.writerow(["Timestamp [MST]", "Altitude [m]", "Temperature[°C]", "Humidity [%]", "Pressure [hPa]"])

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            utils.log("Service Worker", "Could not open video stream.")
            return
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(
            video_file,
            cv2.VideoWriter_fourcc(*'mp4v'),
            1.0,
            (width, height))

        utils.log("Service Worker", f"Video Recording Started at {video_file}")
        utils.log("Service Worker", f"CSV Recording Started at {csv_file}")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                utils.log("Service Worker", "Failed to capture video frame.")
                break

            timestamp = utils.timestamp("%H:%M:%S")
            altitude = round(self.bme280.altitude, 2)
            temperature = round(self.bme280.temperature, 2)
            humidity = round(self.bme280.relative_humidity, 2)
            pressure = round(self.bme280.pressure, 2)

            cv2.putText(frame, timestamp, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Altitude: {altitude} m", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Temperature: {temperature} °C", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Humidity: {humidity} %", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Pressure: {pressure} hPa", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            out.write(frame)
            writer.writerow([timestamp, altitude, temperature, humidity, pressure])
            
            time.sleep(1)

        cap.release()
        out.release()
        csvf.close()

        utils.log("Service Worker", "Recording Stopped.")

    def stop(self):
        self.running = False