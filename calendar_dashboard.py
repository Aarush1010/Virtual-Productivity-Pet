# calendar_dashboard.py
# A separate dashboard window for Google Calendar integration
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout, QDateTimeEdit, QDialog, QDialogButtonBox, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QDateTime
import datetime
from calendar_integration import CalendarIntegration

class CalendarDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendar Dashboard")
        self.setFixedSize(500, 400)
        self.setStyleSheet("")
        self.cal = CalendarIntegration()
        self.layout = QVBoxLayout(self)

        self.event_list = QListWidget()
        self.layout.addWidget(QLabel("Upcoming Events:"))
        self.layout.addWidget(self.event_list)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_events)
        btn_row.addWidget(self.refresh_btn)
        self.add_btn = QPushButton("Add Event")
        self.add_btn.clicked.connect(self.add_event_dialog)
        btn_row.addWidget(self.add_btn)
        self.delete_btn = QPushButton("Delete Event")
        self.delete_btn.clicked.connect(self.delete_selected_event)
        btn_row.addWidget(self.delete_btn)
        self.layout.addLayout(btn_row)

        self.refresh_events()

    def refresh_events(self):
        self.event_list.clear()
        try:
            events = self.cal.get_upcoming_events(20)
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date', ''))
                summary = event.get('summary', '(No Title)')
                item = QListWidgetItem(f"{summary} | {start}")
                item.setData(Qt.UserRole, event['id'])
                self.event_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Calendar Error", f"Could not fetch events: {e}")

    def add_event_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Event")
        layout = QVBoxLayout(dialog)
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("Event Title")
        layout.addWidget(title_edit)
        start_dt = QDateTimeEdit(QDateTime.currentDateTime())
        start_dt.setCalendarPopup(True)
        layout.addWidget(QLabel("Start Time:"))
        layout.addWidget(start_dt)
        end_dt = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        end_dt.setCalendarPopup(True)
        layout.addWidget(QLabel("End Time:"))
        layout.addWidget(end_dt)
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Description (optional)")
        layout.addWidget(desc_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.cal.add_event(
                    title_edit.text(),
                    start_dt.dateTime().toPyDateTime(),
                    end_dt.dateTime().toPyDateTime(),
                    desc_edit.text()
                )
                self.refresh_events()
            except Exception as e:
                QMessageBox.warning(self, "Calendar Error", f"Could not add event: {e}")

    def delete_selected_event(self):
        item = self.event_list.currentItem()
        if not item:
            QMessageBox.information(self, "Delete Event", "Select an event to delete.")
            return
        event_id = item.data(Qt.UserRole)
        try:
            self.cal.delete_event(event_id)
            self.refresh_events()
        except Exception as e:
            QMessageBox.warning(self, "Calendar Error", f"Could not delete event: {e}")
