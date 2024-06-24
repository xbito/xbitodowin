from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import QTimer, Qt
from pydub import AudioSegment
from pydub.generators import Sine
import simpleaudio as sa
import sqlite3
from datetime import datetime


def init_pomodoro_db():
    # Function to create/connect to a SQLite database and create the table if it doesn't exist
    conn = sqlite3.connect("pomodoro_sessions.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS session_feedback
                 (start_time TEXT, end_time TEXT, feeling TEXT)"""
    )
    conn.commit()
    conn.close()


def insert_pomodoro_session(start_time, end_time, feeling):
    if not start_time:
        return  # Do not proceed if start_time is not set
    # Function to insert a session record into the database
    conn = sqlite3.connect("pomodoro_sessions.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO session_feedback (start_time, end_time, feeling) VALUES (?, ?, ?)",
        (start_time, end_time, feeling),
    )
    conn.commit()
    conn.close()


def play_melody():
    # Create a celebratory melody with a sequence of notes
    durations = [250, 250, 300, 200, 250, 300, 450]  # Durations in milliseconds
    note1 = Sine(523).to_audio_segment(duration=durations[0])  # C5
    note2 = Sine(587).to_audio_segment(duration=durations[1])  # D5
    note3 = Sine(659).to_audio_segment(duration=durations[2])  # E5
    note4 = Sine(784).to_audio_segment(duration=durations[3])  # G5
    note5 = Sine(880).to_audio_segment(duration=durations[4])  # A5
    note6 = Sine(988).to_audio_segment(duration=durations[5])  # B5
    note7 = Sine(1046).to_audio_segment(duration=durations[6])  # C6

    # Combine the notes to form a melody
    melody = note1 + note2 + note3 + note4 + note5 + note6 + note7

    # Play the melody
    play_obj = sa.play_buffer(
        melody.raw_data,
        num_channels=melody.channels,
        bytes_per_sample=melody.sample_width,
        sample_rate=melody.frame_rate,
    )
    play_obj.wait_done()


class CountdownPopup(QDialog):
    def __init__(self, app):
        self.app = app
        self.start_time = None  # To store the session start time
        # Initialize the database
        init_pomodoro_db()

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

        # Emoticon buttons for feedback
        self.happy_button = QPushButton("😊")
        self.sad_button = QPushButton("😞")
        self.happy_button.clicked.connect(lambda: self.record_feedback("happy"))
        self.sad_button.clicked.connect(lambda: self.record_feedback("sad"))
        # Add emoticon buttons to the layout
        self.layout.addWidget(self.happy_button)
        self.layout.addWidget(self.sad_button)
        self.happy_button.setEnabled(False)
        self.sad_button.setEnabled(False)

    def toggle_timer(self):
        if not self.is_timer_running:
            self.start_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )  # Store start time
        if self.is_timer_running:
            self.timer.stop()
            self.start_pause_button.setText("Start")
            self.happy_button.setEnabled(True)
            self.sad_button.setEnabled(True)
        else:
            self.timer.start(1000)  # Update every second
            self.start_pause_button.setText("Pause")
            self.happy_button.setEnabled(False)
            self.sad_button.setEnabled(False)
        self.is_timer_running = not self.is_timer_running

    def update_countdown(self):
        self.remaining_seconds -= 1
        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.countdown_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.start_pause_button.setText("Start")
            self.is_timer_running = False
            self.happy_button.setEnabled(True)
            self.sad_button.setEnabled(True)
            play_melody()

    def reset_timer(self):
        self.timer.stop()
        self.remaining_seconds = self.initial_seconds
        self.countdown_label.setText("30:00")
        self.start_pause_button.setText("Start")
        self.is_timer_running = False
        self.happy_button.setEnabled(False)
        self.sad_button.setEnabled(False)

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

    def record_feedback(self, feeling):
        if self.start_time:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_pomodoro_session(self.start_time, end_time, feeling)
            self.start_time = None  # Reset start time after recording feedback
