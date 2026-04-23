from datetime import datetime

def timestamp(format="%m-%d-%Y_%H-%M-%S"):
    return datetime.now().strftime(format)

def log(tag, message):
    print(f"[{tag} | {timestamp('%H:%M:%S')}] {message}")