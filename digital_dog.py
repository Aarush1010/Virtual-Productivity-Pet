# digital_dog.py
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QTime
from dashboard import DogDashboard
from dog_animation import load_frames

class DigitalDog(QWidget):
    def __init__(self):
        super().__init__()
        # Make the dog window background transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("")  # Remove any background color
        # Set a larger minimum and initial size for the dog window
        self.setMinimumSize(220, 220)
        self.resize(260, 260)
        self.dashboard = DogDashboard(parent=self)
        self.dashboard.on_dashboard_closed_callback = self.on_dashboard_closed
        self.dashboard.on_dog_image_selected = self.set_dog_image

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # Animation setup
        self.animation = QPropertyAnimation(self, b"pos")
        self.inactive_timer = QTimer(self)
        self.inactive_timer.setInterval(5000)
        self.inactive_timer.timeout.connect(self.slide_out)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.next_frame)
        self.animation_timer.start(200)
        self._drag_active = False
        self._drag_position = None
        self._press_time = None
        self._click_pos = None
        self.dog_frames = load_frames("Dog tongue animation/Dog_Tongue_*.png")
        self.current_frame = 0
        self.eating_frames = load_frames("Dog eating/Dog_Eating_*.png")
        self.eating_frame_idx = 0

        # Dog image label
        self.label = QLabel(self)
        self.label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.label.setFixedSize(200, 200)
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        # Set a debug pixmap if no dog image is loaded
        if not self.dog_frames or not self.dog_frames[0]:
            from PyQt5.QtGui import QPixmap, QColor
            pixmap = QPixmap(100, 100)
            pixmap.fill(QColor('red'))
            self.label.setPixmap(pixmap)

        # Buttons (hidden by default)
        self.button_row = QHBoxLayout()
        self.feed_button = QPushButton("Feed", self)
        self.feed_button.clicked.connect(self.feed)
        self.feed_button.hide()
        self.walk_button = QPushButton("Walk", self)
        self.walk_button.clicked.connect(self.walk)
        self.walk_button.hide()
        self.hide_button = QPushButton("Hide", self)
        self.hide_button.clicked.connect(self.hide_dog)
        self.hide_button.hide()
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.play)
        self.play_button.hide()
        self.button_row.addWidget(self.feed_button)
        self.button_row.addWidget(self.walk_button)
        self.button_row.addWidget(self.hide_button)
        self.button_row.addWidget(self.play_button)
        self.layout.addLayout(self.button_row)

        # Adjust button row spacing for better readability
        self.button_row.setSpacing(12)

        # Speech bubble for reminders
        self.speech_bubble = QLabel(self)
        self.speech_bubble.setStyleSheet('''
            QLabel {
                background: white;
                border: 2px solid #888;
                border-radius: 12px;
                padding: 10px 18px;
                color: #222;
                font-size: 15px;
                min-width: 120px;
                max-width: 220px;
            }
        ''')
        self.speech_bubble.setWordWrap(True)
        self.speech_bubble.hide()
        self.speech_bubble.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.speech_bubble.mousePressEvent = self._hide_speech_bubble
        self.speech_bubble_timer = QTimer(self)
        self.speech_bubble_timer.setSingleShot(True)
        self.speech_bubble_timer.timeout.connect(self._hide_speech_bubble)

        self.resize(120, 120)
        self.move_to_top_right()
        # Do NOT call self.show() or self.raise_() here
        # Do NOT call self.activateWindow() here
        # Do NOT call slide_in here

        self._reminder_active = False  # Track if a reminder is being shown

    # --- Essential Methods and Stubs ---

    def move_to_top_right(self):
        screen = self.screen().geometry()
        x = screen.width() - self.width() - 10
        y = 10
        self.move(x, y)

    def show_dog(self):
        print('[DEBUG] show_dog called')
        self.show()
        self.raise_()
        self.activateWindow()
        print(f'[DEBUG] geometry: {self.geometry()}')
        self.slide_in()
        self.reset_inactive_timer()

    def hide_dog(self):
        print('[DEBUG] hide_dog called')
        self.hide()
        self.inactive_timer.stop()

    def reset_inactive_timer(self):
        print('[DEBUG] reset_inactive_timer called')
        self.inactive_timer.stop()
        self.inactive_timer.start()

    def get_side(self):
        """Return 'left' or 'right' depending on which side the dog is closer to."""
        screen = self.screen().geometry()
        center_x = self.x() + self.width() // 2
        if center_x < screen.width() // 2:
            return 'left'
        else:
            return 'right'

    def slide_in(self):
        print('[DEBUG] slide_in called')
        screen = self.screen().geometry()
        side = self.get_side()
        end_y = self.y() if 0 <= self.y() <= screen.height() - self.height() else 10
        if side == 'left':
            start_x = -self.width()
            end_x = 10
        else:
            start_x = screen.width()
            end_x = screen.width() - self.width() - 10
        self.show()
        self.raise_()
        self.move(start_x, end_y)
        self.animation.stop()
        self.animation.setDuration(500)
        self.animation.setStartValue(QPoint(start_x, end_y))
        self.animation.setEndValue(QPoint(end_x, end_y))
        # Always disconnect all possible slots before connecting
        try:
            self.animation.finished.disconnect()
        except Exception:
            pass
        self.animation.finished.connect(self._after_slide_in)
        self.animation.start()
        self.reset_inactive_timer()

    def _after_slide_in(self):
        print('[DEBUG] _after_slide_in called')
        # No-op, just ensures dog is visible after slide in

    def slide_out(self):
        print('[DEBUG] slide_out called')
        # Only allow slide out if no reminder is active
        if getattr(self, '_reminder_active', False):
            print('[DEBUG] slide_out blocked: reminder active')
            return
        # Original slide out logic
        if self.dashboard.isVisible():
            print('[DEBUG] slide_out aborted: dashboard is visible')
            return
        if hasattr(self.dashboard, 'task_manager') and self.dashboard.task_manager is not None and self.dashboard.task_manager.isVisible():
            print('[DEBUG] slide_out aborted: task manager is visible')
            return
        screen = self.screen().geometry()
        side = self.get_side()
        end_y = self.y()
        if side == 'left':
            end_x = -self.width()
        else:
            end_x = screen.width()
        self.animation.stop()
        self.animation.setDuration(500)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(end_x, end_y))
        try:
            self.animation.finished.disconnect()
        except Exception:
            pass
        self.animation.finished.connect(self._after_slide_out)
        self.animation.start()
        self.inactive_timer.stop()

    def _after_slide_out(self):
        print('[DEBUG] _after_slide_out called')
        self.hide()  # Only hide the dog after sliding out
        # Do NOT call move_to_top_right() or show() here

    def on_dashboard_closed(self):
        self.reset_inactive_timer()

    def set_dog_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)

    def feed(self):
        self.play_eating_animation()
        # Update dashboard food bar
        if self.dashboard:
            self.dashboard.feed_dog()

    def walk(self):
        if hasattr(self, "play_walking_animation"):
            self.play_walking_animation()
        else:
            pixmap = QPixmap("dog_walking.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label.setPixmap(pixmap)
        # Update dashboard walk bar
        if self.dashboard:
            self.dashboard.walk_dog()

    def play(self):
        # Optionally add a play animation here
        if self.dashboard:
            self.dashboard.play_with_dog()

    def next_frame(self):
        if self.dog_frames:
            self.current_frame = (self.current_frame + 1) % len(self.dog_frames)
            self.label.setPixmap(self.dog_frames[self.current_frame])

    def restore_animation(self):
        if self.dog_frames:
            self.label.setPixmap(self.dog_frames[self.current_frame])

    def play_eating_animation(self):
        if not self.eating_frames:
            self.restore_animation()
            return

        self.animation_timer.stop()  # Pause main animation
        self.eating_frame_idx = 0

        # Stop any previous eating timer
        if hasattr(self, "eating_timer") and self.eating_timer is not None:
            self.eating_timer.stop()
        self.eating_timer = QTimer(self)
        self.eating_timer.timeout.connect(self.next_eating_frame)
        self.eating_timer.start(120)  # Adjust speed as needed

    def next_eating_frame(self):
        if self.eating_frame_idx < len(self.eating_frames):
            self.label.setPixmap(self.eating_frames[self.eating_frame_idx])
            self.eating_frame_idx += 1
        else:
            self.eating_timer.stop()
            self.eating_timer = None
            self.animation_timer.start(200)  # Resume main animation
            self.restore_animation()

    # --- Dragging logic ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self._click_pos = event.pos()
            self._press_time = QTime.currentTime()
            self.inactive_timer.stop()  # Stop timer while dragging
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._drag_active:
            elapsed = self._press_time.msecsTo(QTime.currentTime()) if self._press_time else 0
            is_click = (event.pos() - self._click_pos).manhattanLength() < 5 and elapsed < 200
            if is_click:
                self.dashboard.show()
                self.dashboard.raise_()
                self.dashboard.activateWindow()
                self.inactive_timer.stop()  # Do NOT reset timer here!
            else:
                self.reset_inactive_timer()  # Only reset if it was a drag, not a click
            self._drag_active = False
            event.accept()

    # --- Hover logic for showing/hiding buttons ---
    def enterEvent(self, event):
        self.show()
        self.raise_()
        screen = self.screen().geometry()
        # If the dog is off-screen (left or right), move it back on screen
        if self.x() < 0:
            self.move(10, self.y())
        elif self.x() + self.width() > screen.width():
            self.move(screen.width() - self.width() - 10, self.y())
        self.feed_button.show()
        self.walk_button.show()
        self.hide_button.show()
        if hasattr(self, 'play_button'):
            self.play_button.show()
        self.inactive_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.feed_button.hide()
        self.walk_button.hide()
        self.hide_button.hide()
        self.play_button.hide()
        self.reset_inactive_timer()  # Restart timer when mouse leaves
        super().leaveEvent(event)

    def show_reminder_bubble(self, message):
        """Slide in the dog and show a speech bubble with the reminder message and a dismiss button."""
        self._reminder_active = True
        self.slide_in()
        self.speech_bubble.setText(message)
        # Add a dismiss button to the speech bubble if not already present
        if not hasattr(self, 'dismiss_button'):
            from PyQt5.QtWidgets import QPushButton
            self.dismiss_button = QPushButton('Dismiss', self)
            self.dismiss_button.setStyleSheet('''
                QPushButton {
                    background: #f0e68c;
                    border: 1px solid #888;
                    border-radius: 8px;
                    padding: 2px 10px;
                    font-size: 13px;
                }
                QPushButton:hover { background: #ffe;
                }
            ''')
            self.dismiss_button.clicked.connect(self._hide_speech_bubble)
        self.dismiss_button.show()
        # Position the bubble above the dog's mouth (bottom center of dog image)
        bubble_width = self.speech_bubble.sizeHint().width()
        bubble_height = self.speech_bubble.sizeHint().height()
        dog_x = self.label.x() + self.label.width() // 2 - bubble_width // 2
        dog_y = self.label.y() - bubble_height - 10
        if dog_y < 0:
            dog_y = 0
        self.speech_bubble.setGeometry(dog_x, dog_y, bubble_width, bubble_height)
        # Position the dismiss button below the bubble
        btn_width = self.dismiss_button.sizeHint().width()
        btn_height = self.dismiss_button.sizeHint().height()
        btn_x = dog_x + bubble_width // 2 - btn_width // 2
        btn_y = dog_y + bubble_height + 4
        self.dismiss_button.setGeometry(btn_x, btn_y, btn_width, btn_height)
        self.speech_bubble.show()
        self.speech_bubble.raise_()
        self.dismiss_button.raise_()
        self.speech_bubble_timer.stop()  # Don't auto-hide

    def _hide_speech_bubble(self, event=None):
        self.speech_bubble.hide()
        if hasattr(self, 'dismiss_button'):
            self.dismiss_button.hide()
        self.speech_bubble_timer.stop()
        self._reminder_active = False
        self.reset_inactive_timer()  # Allow slide out again