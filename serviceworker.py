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
        folder = f"data/{utils.timestamp()}"
        os.makedirs(folder, exist_ok=True)

        video_file = f"{folder}/video.avi"
        csv_file = f"{folder}/data.csv"

        target_fps = 10.0
        frame_duration = 1.0 / target_fps

        cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
        utils.log("Service Worker", "Attempting to access camera stream.")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 10)

        time.sleep(2.5)

        video_enabled = cap.isOpened()
        out = None

        if not video_enabled:
            utils.log("Service Worker", "Camera stream not found. Proceeding with sensor logging.")
        else:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if width > 0 and height > 0:
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(video_file, fourcc, target_fps, (width, height))
                utils.log("Service Worker", f"Video Recording Initialized with {width}x{height} at {target_fps} FPS.")
            else:
                utils.log("Service Worker", "Camera Reported Invalid Resolution. Video Recording Disabled.")
                video_enabled = False

        with open(csv_file, "w", newline="") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["Timestamp [MST]", "Altitude [m]", "Temperature [C]", "Humidity [%]", "Pressure [hPa]"])
            
            alt, temp, hum, pres = (0, 0, 0, 0)
            last_sensor_update = 0
            timestamp = utils.timestamp("%H:%M:%S")

            utils.log("Service Worker", f"CSV Logging Started at {csv_file}")
            next_frame_time = time.monotonic()

            while self.running:
                loop_start = time.monotonic()

                if video_enabled:
                    ret, frame = cap.read()
                    if not ret:
                        utils.log("Service Worker", "Failed to read frame from camera. Stopping video recording.")
                        break

                try:
                    alt = round(self.bme280.altitude, 2)
                    temp = round(self.bme280.temperature, 2)
                    hum = round(self.bme280.relative_humidity, 2)
                    pres = round(self.bme280.pressure, 2)

                    if loop_start - last_sensor_update >= 1.0:
                        timestamp = utils.timestamp("%H:%M:%S")
                        writer.writerow([timestamp, alt, temp, hum, pres])
                        csvf.flush()
                        last_sensor_update = loop_start
                except Exception as e:
                    utils.log("Service Worker", f"Error occurred while updating sensor data: {e}")

                if video_enabled:
                    txt = f"{timestamp} | {alt}m | {temp}C | {hum}% | {pres}hPa"
                    cv2.putText(frame, txt, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
                    cv2.putText(frame, txt, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                    out.write(frame)

                    next_frame_time += frame_duration
                    sleep_time = next_frame_time - time.monotonic()
                    if sleep_time > 0:
                        time.sleep(sleep_time)

        if cap: cap.release()
        if out: out.release()
        utils.log("Service Worker", f"Recording Stopped and Cleanup Complete. Files Saved in {folder}")

    def stop(self):
        self.running = False