from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QDialog, QDialogButtonBox, QDateTimeEdit
from PyQt5.QtCore import QTimer, QDateTime, Qt
import json
import os

class TaskManager(QWidget):
    TASKS_FILE = "tasks.json"

    def __init__(self, parent=None):
        super().__init__(None)  # Force parent to None for a clean window
        self.setWindowTitle("Task Manager")
        self.setFixedSize(400, 400)
        layout = QVBoxLayout(self)

        # Input for new task
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task...")
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_task_button)
        layout.addLayout(input_layout)

        # Task list
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        # Reminder timer
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute

        # Store tasks as (item, due_datetime)
        self.tasks = []
        self.load_tasks()
        self.reminder_callback = None  # Callback for dog reminder
        self.reminder_lead_minutes = 10  # Remind 10 minutes before due

    def add_task(self):
        text = self.task_input.text().strip()
        if not text:
            return
        from PyQt5.QtCore import QDateTime
        due, ok = self.get_due_datetime("Set Due Date & Time", QDateTime.currentDateTime())
        if not ok:
            return
        item = QListWidgetItem(f"{text} (Due: {due.toString('yyyy-MM-dd hh:mm')})")
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        self.task_list.addItem(item)
        self.tasks.append((item, due))
        self.task_input.clear()
        self.save_tasks()

    def check_reminders(self):
        from PyQt5.QtCore import QDateTime
        now = QDateTime.currentDateTime()
        for item, due in self.tasks:
            if item.checkState() == Qt.Unchecked:
                minutes_to_due = now.secsTo(due) / 60
                if 0 <= minutes_to_due <= self.reminder_lead_minutes:
                    if self.reminder_callback:
                        self.reminder_callback(item.text())
                if now > due:
                    QMessageBox.information(self, "Task Reminder", f"Task '{item.text()}' is due!")

    def mark_task_complete(self, item):
        item.setCheckState(Qt.Checked)
        self.save_tasks()

    def closeEvent(self, event):
        self.save_tasks()
        super().closeEvent(event)

    def save_tasks(self):
        # Save only unchecked tasks
        tasks_to_save = []
        for item, due in self.tasks:
            if item.checkState() == Qt.Unchecked:
                tasks_to_save.append({
                    "text": item.text(),
                    "due": due.toString("yyyy-MM-dd hh:mm")
                })
        with open(self.TASKS_FILE, "w") as f:
            json.dump(tasks_to_save, f)

    def load_tasks(self):
        from PyQt5.QtCore import QDateTime
        if not os.path.exists(self.TASKS_FILE):
            return
        try:
            with open(self.TASKS_FILE, "r") as f:
                tasks_to_load = json.load(f)
            for task in tasks_to_load:
                text = task["text"]
                due = QDateTime.fromString(task["due"], "yyyy-MM-dd hh:mm")
                item = QListWidgetItem(text)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.task_list.addItem(item)
                self.tasks.append((item, due))
        except Exception as e:
            print(f"[TaskManager] Failed to load tasks: {e}")

    def get_due_datetime(self, title, default_dt):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QDateTimeEdit
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        dt_edit = QDateTimeEdit(default_dt)
        dt_edit.setCalendarPopup(True)
        layout.addWidget(dt_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted:
            return dt_edit.dateTime(), True
        else:
            return default_dt, False

    def add_task_from_voice(self, text, due_qdatetime):
        item = QListWidgetItem(f"{text} (Due: {due_qdatetime.toString('yyyy-MM-dd hh:mm')})")
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        self.task_list.addItem(item)
        self.tasks.append((item, due_qdatetime))
        self.save_tasks()
