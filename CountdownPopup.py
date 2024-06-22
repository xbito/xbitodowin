from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import QTimer, Qt


class CountdownPopup(QDialog):
    def __init__(self, app):
        self.app = app
        super().__init__()
        self.setWindowTitle("Xbitodowin - Pomodoro Timer")
        self.setGeometry(100, 100, 250, 115)
        self.layout = QVBoxLayout()
        self.layout.addStretch(1)
        self.setLayout(self.layout)

        # Set the window to always stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Positioning the window near the top right of the screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = screen_geometry.width() * 0.9 - self.width()  # 10% from the right edge
        y = screen_geometry.height() * 0.1  # 10% from the top
        self.move(int(x), int(y))

        # Create a horizontal layout for buttons and the countdown label
        self.controls_layout = QHBoxLayout()

        # Create control buttons
        self.reverse_button = QPushButton("-")
        self.fast_reverse_button = QPushButton("--")
        self.forward_button = QPushButton("+")
        self.fast_forward_button = QPushButton("++")

        self.reverse_button.clicked.connect(lambda: self.adjust_timer(-1))
        self.fast_reverse_button.clicked.connect(lambda: self.adjust_timer(-5))
        self.forward_button.clicked.connect(lambda: self.adjust_timer(1))
        self.fast_forward_button.clicked.connect(lambda: self.adjust_timer(5))

        # Add buttons to the controls layout
        self.controls_layout.addWidget(self.fast_reverse_button)
        self.controls_layout.addWidget(self.reverse_button)

        self.countdown_label = QLabel("30:00")
        self.countdown_label.setStyleSheet("font-size: 24px;")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        # Add the countdown label to the controls layout
        self.controls_layout.addWidget(self.countdown_label)

        self.controls_layout.addWidget(self.forward_button)
        self.controls_layout.addWidget(self.fast_forward_button)

        # Add the controls layout to the main layout
        self.layout.addLayout(self.controls_layout)

        self.start_pause_button = QPushButton("Start")
        self.start_pause_button.setStyleSheet("font-size: 18px; padding: 5px;")
        self.start_pause_button.clicked.connect(self.toggle_timer)
        self.layout.addWidget(self.start_pause_button)

        # Adding a Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("font-size: 18px; padding: 5px;")
        self.reset_button.clicked.connect(self.reset_timer)
        self.layout.addWidget(self.reset_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.initial_seconds = 1800  # 30 minutes
        self.remaining_seconds = self.initial_seconds
        self.is_timer_running = False  # Track timer state

        self.layout.addStretch(1)

    def toggle_timer(self):
        if self.is_timer_running:
            self.timer.stop()
            self.start_pause_button.setText("Start")
        else:
            self.timer.start(1000)  # Update every second
            self.start_pause_button.setText("Pause")
        self.is_timer_running = not self.is_timer_running

    def update_countdown(self):
        self.remaining_seconds -= 1
        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.countdown_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.start_pause_button.setText("Start")
            self.is_timer_running = False
            self.app.beep()

    def reset_timer(self):
        self.timer.stop()
        self.remaining_seconds = self.initial_seconds
        self.countdown_label.setText("30:00")
        self.start_pause_button.setText("Start")
        self.is_timer_running = False

    def adjust_timer(self, minutes_change):
        # Convert minutes to seconds
        seconds_change = minutes_change * 60
        new_remaining_seconds = self.remaining_seconds + seconds_change

        # Ensure the timer is within the 1 to 120 minutes range
        if new_remaining_seconds < 60:
            self.remaining_seconds = 60  # Minimum of 1 minute
        elif new_remaining_seconds > 7200:
            self.remaining_seconds = 7200  # Maximum of 120 minutes
        else:
            self.remaining_seconds = new_remaining_seconds

        self.update_countdown_display()

    def update_countdown_display(self):
        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.countdown_label.setText(f"{minutes:02d}:{seconds:02d}")
