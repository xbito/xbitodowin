from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QPushButton,
    QTableWidgetItem,
)


import datetime


class TaskListSidebar(QListWidget):
    def __init__(self, parent=None, window=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemClicked.connect(self.load_tasks_by_task_list)
        self.icon_path = "output.ico.32x32.png"
        self.window = window

    def set_title_icon(self, icon_path):
        self.icon_path = icon_path

    def fetch_tasks_by_task_list(self, item):
        if type(item) is str:
            task_list_id = item  # Set the current task list ID
        else:
            task_list_id = item.data(Qt.UserRole)

        self.current_tasklist_id = task_list_id  # Set the current task list ID

        # Fetch tasks for the selected task list
        tasks_response = (
            self.window.service.tasks()
            .list(tasklist=task_list_id, maxResults=1000)
            .execute()
        )
        tasks = tasks_response.get("items", [])
        return tasks

    def render_tasks(self, tasks):
        # Clear the table before loading new tasks
        self.window.task_table.setRowCount(0)

        # Set the icon for the title column
        self.window.task_table.horizontalHeaderItem(0).setIcon(QIcon(self.icon_path))

        # Iterate through the tasks and add them to the table
        for task in tasks:
            row_position = self.window.task_table.rowCount()
            self.window.task_table.insertRow(row_position)
            self.window.task_table.setItem(
                row_position, 0, QTableWidgetItem(task["title"])
            )
            # Convert the updated timestamp to local time
            updated_datetime = datetime.datetime.fromisoformat(task["updated"])
            updated_local_time = updated_datetime.astimezone()
            updated_local_time_str = updated_local_time.strftime("%Y-%m-%d %H:%M:%S")
            self.window.task_table.setItem(
                row_position, 1, QTableWidgetItem(updated_local_time_str)
            )
            if "due" in task:
                due_datetime = datetime.datetime.fromisoformat(task["due"])
                due_local_time = due_datetime.astimezone()
                due_local_time_str = due_local_time.strftime("%Y-%m-%d %H:%M:%S")
                # Set the due timestamp in the table
                self.window.task_table.setItem(
                    row_position, 2, QTableWidgetItem(due_local_time_str)
                )
            else:
                self.window.task_table.setItem(row_position, 2, QTableWidgetItem(""))
            # Store the task's notes
            task_notes = task.get("notes")
            # Add a button to view more notes
            if task_notes:
                notes_button = QPushButton("View More")
                notes_button.clicked.connect(
                    lambda checked, notes=task_notes: self.window.show_notes(notes)
                )
                self.window.task_table.setCellWidget(row_position, 3, notes_button)
            # Add priority column
            priority_item = QTableWidgetItem(task.get("priority", "None"))
            self.window.task_table.setItem(row_position, 4, priority_item)
            # Store the task ID as data for the item
            item = self.window.task_table.item(row_position, 0)
            item.setData(Qt.UserRole, task["id"])

    def load_tasks_by_task_list(self, item):
        tasks = self.fetch_tasks_by_task_list(item)
        self.render_tasks(tasks)
