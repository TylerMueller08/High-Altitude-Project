import time
from servicehandler import ServiceHandler

def main():
    services = ServiceHandler()
    services.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        services.stop()

if __name__ == "__main__":
    main()