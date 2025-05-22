# ai_monitor.py
# Monitors active app and notifies DigitalDog if a distracting app is used too long (macOS only)
import time
from PyQt5.QtCore import QTimer, QObject
from AppKit import NSWorkspace
import subprocess

DISTRACTING_BUNDLE_IDS = [
    "com.apple.Safari",
    "com.google.Chrome",
    "org.mozilla.firefox",
    "com.google.Chrome.app.yt",  # YouTube in Chrome (custom, may not always work)
    "com.netflix.Netflix",
    "com.instagram.desktop",      # Instagram desktop app (if installed)
    "com.brave.Browser",          # Brave browser
    "com.microsoft.edgemac",      # Microsoft Edge
    # Add more bundle IDs as needed
]
DISTRACTING_URL_KEYWORDS = [
    "instagram.com",
    "youtube.com",
    "netflix.com",
    "twitch.tv",
    "facebook.com",
    # Add more site keywords as needed
]
DISTRACTING_THRESHOLD_SECONDS = 5  # 1 minute

class AIMonitor(QObject):
    def __init__(self, dog):
        super().__init__()
        self.dog = dog
        self.last_app = None
        self.distract_start_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_active_app)
        self.timer.start(2000)  # Check every 2 seconds
        self.last_url = None

    def get_chrome_url(self):
        try:
            script = 'tell application "Google Chrome" to get URL of active tab of front window'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            url = result.stdout.strip()
            return url
        except Exception as e:
            return None

    def get_brave_url(self):
        try:
            script = 'tell application "Brave Browser" to get URL of active tab of front window'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            url = result.stdout.strip()
            return url
        except Exception as e:
            return None

    def check_active_app(self):
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        bundle_id = active_app.bundleIdentifier()
        # print(f"[AI] Active app: {bundle_id}")
        url = None
        if bundle_id == "com.google.Chrome":
            url = self.get_chrome_url()
        elif bundle_id == "com.brave.Browser":
            url = self.get_brave_url()
        else:
            url = None

        if url and any(keyword in url for keyword in DISTRACTING_URL_KEYWORDS):
            if self.last_url != url:
                self.distract_start_time = time.time()
                self.last_url = url
            elif self.distract_start_time and (time.time() - self.distract_start_time > DISTRACTING_THRESHOLD_SECONDS):
                self.react_to_distraction(bundle_id, url)
            return
        else:
            self.last_url = None
            self.distract_start_time = None
        if bundle_id in DISTRACTING_BUNDLE_IDS:
            if self.last_app != bundle_id:
                self.distract_start_time = time.time()
                self.last_app = bundle_id
            elif self.distract_start_time and (time.time() - self.distract_start_time > DISTRACTING_THRESHOLD_SECONDS):
                self.react_to_distraction(bundle_id)
        else:
            self.last_app = None
            self.distract_start_time = None

    def show_mac_notification(self, title, message):
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])

    def react_to_distraction(self, bundle_id, url=None):
        # Always send a macOS notification for distraction
        if url and "instagram.com" in url:
            self.show_mac_notification("Digital Dog", "Instagram detected! Let's get back to work! 🐶")
        else:
            self.show_mac_notification("Digital Dog", "Hey! Let's get back to work! 🐶")
        # Optionally, also show the chat bubble if the pet is visible
        if hasattr(self.dog, 'show_reminder_bubble') and self.dog.isVisible():
            if url and "instagram.com" in url:
                self.dog.show_reminder_bubble("Instagram detected! Let's get back to work! 🐶")
            else:
                self.dog.show_reminder_bubble("Hey! Let's get back to work! 🐶")
        # Reset so it doesn't spam
        self.distract_start_time = time.time()
