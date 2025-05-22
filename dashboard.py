from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QFileDialog
from PyQt5.QtCore import QTimer, Qt
from task_manager import TaskManager

class DogDashboard(QWidget):
    def __init__(self, parent = None):
        super().__init__(None)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Dog Dashboard")
        self.setFixedSize(350, 250)
        # Remove any custom stylesheet to use the default macOS/Qt style
        self.setStyleSheet("")
        main_layout = QVBoxLayout(self)

        # Internal float values for bars
        self.food_value = 80.0
        self.happy_value = 90.0
        self.walk_value = 40.0

        # Food bar and button
        food_layout = QHBoxLayout()
        self.food_label = QLabel("Food")
        self.food_bar = QProgressBar()
        self.food_bar.setValue(int(self.food_value))
        self.feed_button = QPushButton("Feed")
        self.feed_button.clicked.connect(self.feed_dog)
        food_layout.addWidget(self.food_label)
        food_layout.addWidget(self.food_bar)
        food_layout.addWidget(self.feed_button)
        main_layout.addLayout(food_layout)

        # Happiness bar and button
        happy_layout = QHBoxLayout()
        self.happy_label = QLabel("Happiness")
        self.happy_bar = QProgressBar()
        self.happy_bar.setValue(int(self.happy_value))
        self.happy_button = QPushButton("Play")
        self.happy_button.clicked.connect(self.play_with_dog)
        happy_layout.addWidget(self.happy_label)
        happy_layout.addWidget(self.happy_bar)
        happy_layout.addWidget(self.happy_button)
        main_layout.addLayout(happy_layout)

        # Walking bar and button
        walk_layout = QHBoxLayout()
        self.walk_label = QLabel("Walking")
        self.walk_bar = QProgressBar()
        self.walk_bar.setValue(int(self.walk_value))
        self.walk_button = QPushButton("Walk")
        self.walk_button.clicked.connect(self.walk_dog)
        walk_layout.addWidget(self.walk_label)
        walk_layout.addWidget(self.walk_bar)
        walk_layout.addWidget(self.walk_button)
        main_layout.addLayout(walk_layout)

        # Add Task Manager button
        self.open_task_manager_button = QPushButton("Open Task Manager")
        self.open_task_manager_button.clicked.connect(self.open_task_manager)
        main_layout.addWidget(self.open_task_manager_button)

        # Timer to deplete bars
        self.deplete_timer = QTimer(self)
        self.deplete_timer.timeout.connect(self.deplete_bars)
        self.deplete_timer.start(2000)  # Deplete every 2 seconds

        self.on_dashboard_closed_callback = None
        self.task_manager = None
        self.dog_ref = parent if parent is not None else None

    def showEvent(self, event):
        # Center the dashboard on the screen when shown
        screen = self.screen().geometry()
        x = screen.x() + (screen.width() - self.width()) // 2
        y = screen.y() + (screen.height() - self.height()) // 2
        self.move(x, y)
        super().showEvent(event)

    def feed_dog(self):
        self.food_value = min(100.0, self.food_value + 20.0)
        self.food_bar.setValue(int(self.food_value))

    def play_with_dog(self):
        self.happy_value = min(100.0, self.happy_value + 15.0)
        self.happy_bar.setValue(int(self.happy_value))

    def walk_dog(self):
        self.walk_value = min(100.0, self.walk_value + 20.0)
        self.walk_bar.setValue(int(self.walk_value))

    def deplete_bars(self):
        self.food_value = max(0.0, self.food_value - 0.75)
        self.happy_value = max(0.0, self.happy_value - 1.5)
        self.walk_value = max(0.0, self.walk_value - 0.5)
        self.food_bar.setValue(int(self.food_value))
        self.happy_bar.setValue(int(self.happy_value))
        self.walk_bar.setValue(int(self.walk_value))

    def open_task_manager(self):
        if self.task_manager is None:
            self.task_manager = TaskManager()
            # Add a 'Back to Dashboard' button to the Task Manager
            from PyQt5.QtWidgets import QPushButton, QVBoxLayout
            self.back_button = QPushButton("Back to Dashboard", self.task_manager)
            self.back_button.clicked.connect(self._back_to_dashboard)
            # Insert at the top of the Task Manager layout
            layout = self.task_manager.layout()
            layout.insertWidget(0, self.back_button)
            # Connect reminder callback to dog's show_reminder_bubble
            if self.dog_ref and hasattr(self.dog_ref, 'show_reminder_bubble'):
                self.task_manager.reminder_callback = self.dog_ref.show_reminder_bubble
        self.hide()  # Hide the dashboard when opening the Task Manager
        self.task_manager.show()
        self.task_manager.raise_()
        self.task_manager.activateWindow()

    def _back_to_dashboard(self):
        if self.task_manager:
            self.task_manager.hide()
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if self.on_dashboard_closed_callback:
            self.on_dashboard_closed_callback()
        self.hide()  # Only hide the dashboard, don't close the app
        event.ignore()