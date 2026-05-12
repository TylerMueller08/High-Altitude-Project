import threading, utils, time, csv, cv2, os

class ServiceWorker(threading.Thread):
    def __init__(self, bme280):
        super().__init__()
        self.bme280 = bme280
        self.running = False
        self.daemon = True

    def start(self):
        self.running = True
        super().start()

    def run(self):
        video_enabled = False
        cap = None
        out = None

        folder = f"data/{utils.timestamp()}"
        os.makedirs(folder, exist_ok=True)

        video_file = f"{folder}/video.mp4"
        csv_file = f"{folder}/data.csv"

        cap = cv2.VideoCapture(0)
        video_enabled = cap.isOpened()
        out = None
        if not video_enabled:
            utils.log("Service Worker", "Camera stream not found. Proceeding.")
        else:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(
                video_file,
                cv2.VideoWriter_fourcc(*'mp4v'),
                1.0,
                (width, height)
            )
            utils.log("Service Worker", "Video Recording Initialized.")

        with open(csv_file, "w", newline="") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["Timestamp [MST]", "Altitude [m]", "Temperature[C]", "Humidity [%]", "Pressure [hPa]"])
            utils.log("Service Worker", f"CSV Logging Started at {csv_file}")

            while self.running:
                start_loop = time.time()
                
                try:
                    timestamp = utils.timestamp("%H:%M:%S")
                    alt = round(self.bme280.altitude, 2)
                    temp = round(self.bme280.temperature, 2)
                    hum = round(self.bme280.relative_humidity, 2)
                    pres = round(self.bme280.pressure, 2)
                    
                    writer.writerow([timestamp, alt, temp, hum, pres])
                    csvf.flush() 
                except Exception as e:
                    utils.log("Service Worker", f"Sensor Error: {e}")

                if video_enabled:
                    ret, frame = cap.read()
                    if ret:
                        cv2.putText(frame, f"Alt: {alt}m | Temp: {temp}C", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        out.write(frame)
                    else:
                        utils.log("Service Worker", "Lost camera connection.")
                        video_enabled = False

                elapsed = time.time() - start_loop
                time.sleep(max(0, 1.0 - elapsed))

        if cap: cap.release()
        if out: out.release()

        utils.log("Service Worker", f"Recording Started: {folder}")

        with open(csv_file, "w", newline="") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["Timestamp [MST]", "Altitude [m]", "Temperature[C]", "Humidity [%]", "Pressure [hPa]"])

            while self.running:
                start_loop = time.time()
                
                ret, frame = cap.read()
                if not ret:
                    utils.log("Service Worker", "Failed to capture video frame.")
                    break

                try:
                    timestamp = utils.timestamp("%H:%M:%S")
                    alt = round(self.bme280.altitude, 2)
                    temp = round(self.bme280.temperature, 2)
                    hum = round(self.bme280.relative_humidity, 2)
                    pres = round(self.bme280.pressure, 2)
                except Exception as e:
                    utils.log("Service Worker", f"Sensor read error: {e}")
                    continue

                font = cv2.FONT_HERSHEY_SIMPLEX
                color = (255, 255, 255)
                thickness = 2
                scale = 0.7

                cv2.putText(frame, f"Time: {timestamp}", (10, 30), font, scale, color, thickness)
                cv2.putText(frame, f"Alt:  {alt} m",     (10, 60), font, scale, color, thickness)
                cv2.putText(frame, f"Temp: {temp} C",     (10, 90), font, scale, color, thickness)
                cv2.putText(frame, f"Hum:  {hum} %",     (10, 120), font, scale, color, thickness)
                cv2.putText(frame, f"Pres: {pres} hPa",   (10, 150), font, scale, color, thickness)

                out.write(frame)
                writer.writerow([timestamp, alt, temp, hum, pres])
                csvf.flush()

                elapsed = time.time() - start_loop
                time.sleep(max(0, 1.0 - elapsed))

        cap.release()
        out.release()
        utils.log("Service Worker", "Recording Stopped and Files Saved.")

    def stop(self):
        self.running = False