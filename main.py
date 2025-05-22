# main.py
import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction 
from PyQt5.QtGui import QIcon
from digital_dog import DigitalDog
from ai_monitor import AIMonitor
from calendar_dashboard import CalendarDashboard

app = QApplication(sys.argv)
dog = DigitalDog()
ai_monitor = AIMonitor(dog)
calendar_dashboard = CalendarDashboard()

# System tray icon
tray = QSystemTrayIcon(QIcon("dog_icon.png"), parent=app)
menu = QMenu()
show_action = QAction("Show Dog")
show_action.triggered.connect(dog.show_dog)
hide_action = QAction("Hide Dog")
hide_action.triggered.connect(dog.hide_dog)
feed_action = QAction("Feed Dog")
feed_action.triggered.connect(dog.feed)
menu.addAction(show_action)
menu.addAction(hide_action)
menu.addAction(feed_action)

# Optionally, add a system tray action to open the calendar dashboard
calendar_action = QAction("Open Calendar")
calendar_action.triggered.connect(calendar_dashboard.show)
menu.addAction(calendar_action)

quit_action = QAction("Quit")
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)
tray.setContextMenu(menu)
tray.show()

sys.exit(app.exec_())