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

        cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
        utils.log("Service Worker", "Attempting to access camera stream.")
        time.sleep(2.5)

        video_enabled = cap.isOpened()
        out = None
        target_fps = 20.0
        frame_duration = 1.0 / target_fps

        if not video_enabled:
            utils.log("Service Worker", "Camera stream not found. Proceeding with sensor logging.")
        else:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width > 0 and height > 0:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(video_file, fourcc, target_fps, (width, height))
                utils.log("Service Worker", f"Video Recording Initialized with {width}x{height} at {target_fps} FPS.")
            else:
                utils.log("Service Worker", "Camera Reported Invalid Resolution. Video Recording Disabled.")
                video_enabled = False

        with open(csv_file, "w", newline="") as csvf:
            writer = csv.writer(csvf)
            writer.writerow(["Timestamp [MST]", "Altitude [m]", "Temperature[C]", "Humidity [%]", "Pressure [hPa]"])
            
            last_sensor_update = 0
            alt, temp, hum, pres, timestamp = (0, 0, 0, 0, "00:00:00")

            next_frame_time = time.time()
            utils.log("Service Worker", f"CSV Logging Started at {csv_file}")

            while self.running:
                loop_start = time.time()
                
                if loop_start - last_sensor_update >= 1.0:
                    try:
                        timestamp = utils.timestamp("%H:%M:%S")
                        alt = round(self.bme280.altitude, 2)
                        temp = round(self.bme280.temperature, 2)
                        hum = round(self.bme280.relative_humidity, 2)
                        pres = round(self.bme280.pressure, 2)
                        
                        writer.writerow([timestamp, alt, temp, hum, pres])
                        csvf.flush()
                        last_sensor_update = loop_start
                    except Exception as e:
                        utils.log("Service Worker", f"Sensor Read Error: {e}")
                
                if video_enabled:
                    try:
                        ret, frame = cap.read()
                        if ret:
                            txt = f"{timestamp} | {alt}m | {temp}C"
                            cv2.putText(frame, txt, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
                            cv2.putText(frame, txt, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                            out.write(frame)
                        else:
                            utils.log("Service Worker", "Camera Stream Lost During Capture.")
                    except Exception as e:
                        utils.log("Service Worker", f"Video Capture Error: {e}")
                
                next_frame_time += frame_duration
                sleep_time = next_frame_time - time.time()

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_frame_time = time.time()

        if cap: cap.release()
        if out: out.release()
        utils.log("Service Worker", f"Recording Stopped and Cleanup Complete. Files Saved in {folder}")

    def stop(self):
        self.running = False