import re
import webbrowser
import requests
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtWidgets import (
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QHBoxLayout,
)
from youtube import get_youtube_video_info


class TaskDetailsPanel(QGroupBox):
    """
    A panel for displaying and editing task details. Handles
    YouTube info, web links, and basic metadata.
    """

    def __init__(self, table):
        """
        :param table: The QTableWidget used to get the selected items.
        """
        super().__init__("Task Details")
        self._table = table
        self.setFixedWidth(500)
        self.setVisible(False)
        self._create_ui()

    def _create_ui(self):
        """
        Set up the form layout, fields, and buttons for the task panel.
        """
        layout = QFormLayout()
        self.detail_title_field = QLineEdit()
        self.detail_updated_field = QLineEdit()
        self.detail_due_field = QLineEdit()
        self.detail_notes_field = QTextEdit()

        self.view_task_in_browser_button = QPushButton("Open Task in Browser")
        self.view_task_in_browser_button.setEnabled(False)
        self.view_task_in_browser_button.clicked.connect(self.open_selected_task_link)
        
        # Create action buttons layout
        action_buttons_layout = QHBoxLayout()
        
        # Add Mark as Complete button
        self.complete_task_button = QPushButton("Mark as Complete")
        self.complete_task_button.setEnabled(False)
        self.complete_task_button.clicked.connect(self.mark_task_complete)
        
        # Add Delete Task button
        self.delete_task_button = QPushButton("Delete Task")
        self.delete_task_button.setEnabled(False)
        self.delete_task_button.setStyleSheet("background-color: #8B0000; color: white;")
        self.delete_task_button.clicked.connect(self.delete_task)
        
        # Add buttons to action layout
        action_buttons_layout.addWidget(self.complete_task_button)
        action_buttons_layout.addWidget(self.delete_task_button)

        layout.addRow("Title:", self.detail_title_field)
        layout.addRow("Updated:", self.detail_updated_field)
        layout.addRow("Due:", self.detail_due_field)
        layout.addRow("Notes:", self.detail_notes_field)
        layout.addRow("Link:", self.view_task_in_browser_button)
        layout.addRow(action_buttons_layout)  # Add the action buttons layout

        self.youtube_info_group_box = QGroupBox("YouTube Video")
        youtube_layout = QVBoxLayout(self.youtube_info_group_box)
        self.youtube_thumbnail_label = QLabel()
        self.youtube_thumbnail_label.setFixedSize(160, 90)
        youtube_layout.addWidget(self.youtube_thumbnail_label)
        self.youtube_title_label = QLabel()
        youtube_layout.addWidget(self.youtube_title_label)
        self.youtube_channel_label = QLabel()
        youtube_layout.addWidget(self.youtube_channel_label)
        self.youtube_duration_label = QLabel()
        youtube_layout.addWidget(self.youtube_duration_label)
        self.youtube_open_button = QPushButton("Open Video in Browser")
        self.youtube_open_button.setEnabled(False)
        youtube_layout.addWidget(self.youtube_open_button)
        self.youtube_info_group_box.setVisible(False)
        layout.addRow(self.youtube_info_group_box)

        self.web_group_box = QGroupBox("Web Page")
        web_layout = QVBoxLayout(self.web_group_box)
        self.open_web_link_button = QPushButton("Open Web Page in Browser")
        self.open_web_link_button.setEnabled(False)
        self.open_web_link_button.setVisible(False)
        web_layout.addWidget(self.open_web_link_button)
        self.web_group_box.setVisible(False)
        layout.addRow(self.web_group_box)

        self.setLayout(layout)
        self.setStyleSheet(
            "QGroupBox { background-color: #3E3E3E; margin: 10px; padding: 10px; border: 1px solid #2E2E2E; }"
        )
        layout.setSpacing(8)

    def update_details_panel(self):
        """
        Populate the panel from the current table selection.
        Hide if nothing is selected.
        """
        selected_items = self._table.selectedItems()
        if not selected_items:
            self.clear_details_panel()
            self.setVisible(False)
            return

        self.setVisible(True)
        row = selected_items[0].row()
        title_item = self._table.item(row, 0)
        if not title_item:
            return

        # Get task data from item
        self.current_task_id = title_item.data(Qt.UserRole)  # Store task ID
        self.current_task_list_id = title_item.data(Qt.UserRole + 1)  # Store task list ID
        updated = title_item.data(Qt.UserRole + 2)
        notes = title_item.data(Qt.UserRole + 3)
        web_link = title_item.data(Qt.UserRole + 4)
        due_date = title_item.data(Qt.UserRole + 5)
        completed_date = title_item.data(Qt.UserRole + 6)
        status = title_item.data(Qt.UserRole + 7)

        self.detail_title_field.setText(title_item.text())
        self.detail_updated_field.setText(updated)
        self.detail_notes_field.setPlainText(notes or "")
        self.selected_task_link = web_link or ""
        self.view_task_in_browser_button.setEnabled(bool(self.selected_task_link))
        
        # Enable/disable action buttons based on status
        self.complete_task_button.setEnabled(status != "completed")
        self.delete_task_button.setEnabled(True)  # Always enable delete button

        if status == "completed":
            self.detail_due_field.setText(completed_date or "")
        else:
            self.detail_due_field.setText(due_date or "")

        combined_text = title_item.text() + " " + (notes or "")
        video_info = get_youtube_video_info(combined_text)
        if video_info:
            self._show_youtube_info(video_info)
        else:
            self.youtube_info_group_box.setVisible(False)
            self.youtube_open_button.setEnabled(False)

        match = re.search(r"https?://[^\s]+", combined_text)
        if (
            match
            and "youtube.com" not in match.group(0)
            and "youtu.be" not in match.group(0)
        ):
            self._show_web_link(match.group(0))
        else:
            self.web_group_box.setVisible(False)
            self.open_web_link_button.setVisible(False)
            self.open_web_link_button.setEnabled(False)

    def _show_youtube_info(self, info):
        """Display YouTube thumbnail and metadata."""
        self.youtube_info_group_box.setVisible(True)
        self.youtube_title_label.setText(f"Title: {info['title']}")
        self.youtube_channel_label.setText(f"Channel: {info['channel']}")
        self.youtube_duration_label.setText(f"Duration: {info['duration']}")
        thumb_data = requests.get(info["thumbnail"]).content
        pixmap = QPixmap()
        pixmap.loadFromData(thumb_data)
        self.youtube_thumbnail_label.setPixmap(
            pixmap.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        youtube_url = f"https://www.youtube.com/watch?v={info['video_id']}"
        try:
            self.youtube_open_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.youtube_open_button.setEnabled(True)
        self.youtube_open_button.clicked.connect(lambda: webbrowser.open(youtube_url))

    def _show_web_link(self, link):
        """Display a button to open external web links."""
        self.web_group_box.setVisible(True)
        self.open_web_link_button.setVisible(True)
        self.open_web_link_button.setEnabled(True)
        try:
            self.open_web_link_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.open_web_link_button.clicked.connect(lambda: webbrowser.open(link))

    def open_selected_task_link(self):
        """Open the task link in a browser if any."""
        if hasattr(self, "selected_task_link") and self.selected_task_link:
            QDesktopServices.openUrl(QUrl(self.selected_task_link))

    def mark_task_complete(self):
        """Mark the current task as complete and refresh the view."""
        if not hasattr(self, 'current_task_id') or not hasattr(self, 'current_task_list_id'):
            return

        try:
            # Get parent window reference
            parent_window = self.window()
            
            # Get current task
            task = parent_window.tasks_service.tasks().get(
                tasklist=self.current_task_list_id,
                task=self.current_task_id
            ).execute()
            
            # Update task status to completed
            task['status'] = 'completed'
            parent_window.tasks_service.tasks().update(
                tasklist=self.current_task_list_id,
                task=self.current_task_id,
                body=task
            ).execute()
            
            # Disable the complete button
            self.complete_task_button.setEnabled(False)
            
            # Refresh the task list
            parent_window.refresh_tasks()
            
        except Exception as e:
            print(f"Error marking task as complete: {e}")

    def delete_task(self):
        """Delete the current task after confirmation."""
        if not hasattr(self, 'current_task_id') or not hasattr(self, 'current_task_list_id'):
            print("Missing task ID or task list ID")
            return

        print(f"Task ID: {self.current_task_id}")
        print(f"Task List ID: {self.current_task_list_id}")

        # Show confirmation dialog
        confirm = QMessageBox()
        confirm.setWindowTitle("Delete Task")
        confirm.setText("Are you sure you want to delete this task?")
        confirm.setIcon(QMessageBox.Warning)
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.setDefaultButton(QMessageBox.No)
        
        if confirm.exec() == QMessageBox.Yes:
            try:
                # Get parent window reference
                parent_window = self.window()
                
                # Delete the task
                parent_window.tasks_service.tasks().delete(
                    tasklist=self.current_task_list_id,
                    task=self.current_task_id
                ).execute()
                
                # Show success message
                success = QMessageBox()
                success.setWindowTitle("Success")
                success.setText("Task deleted successfully!")
                success.setIcon(QMessageBox.Information)
                success.exec()
                
                # Refresh the task list
                parent_window.refresh_tasks()
                
                # Clear and hide the details panel
                self.clear_details_panel()
                self.setVisible(False)
                
            except Exception as e:
                # Show error message with detailed error info
                error = QMessageBox()
                error.setWindowTitle("Error")
                error.setText(f"Error deleting task:\n{str(e)}\nTask ID: {self.current_task_id}\nList ID: {self.current_task_list_id}")
                error.setIcon(QMessageBox.Critical)
                error.exec()

    def clear_details_panel(self):
        """Clear all detail fields and disable relevant buttons."""
        self.detail_title_field.clear()
        self.detail_due_field.clear()
        self.detail_updated_field.clear()
        self.detail_notes_field.clear()
        self.view_task_in_browser_button.setEnabled(False)
        self.complete_task_button.setEnabled(False)
        self.delete_task_button.setEnabled(False)
        self.selected_task_link = ""
