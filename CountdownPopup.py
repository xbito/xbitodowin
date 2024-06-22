from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer


class CountdownPopup(QDialog):
    def __init__(self, app):
        self.app = app
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(100, 100, 200, 100)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.countdown_label = QLabel("30:00")
        self.countdown_label.setStyleSheet("font-size: 24px;")
        self.layout.addWidget(self.countdown_label)

        self.start_pause_button = QPushButton("Start")
        self.start_pause_button.setStyleSheet("font-size: 18px; padding: 5px;")
        self.start_pause_button.clicked.connect(self.toggle_timer)
        self.layout.addWidget(self.start_pause_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 1800  # 30 minutes
        self.is_timer_running = False  # Track timer state

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
