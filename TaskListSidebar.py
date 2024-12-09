from PySide6.QtCore import Qt
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
        self.window = window

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

        # Iterate through the tasks and add them to the table
        for task in tasks:
            row_position = self.window.task_table.rowCount()
            self.window.task_table.insertRow(row_position)

            # Add title, updated, due date, and notes columns
            title_item = QTableWidgetItem(task["title"])
            self.window.task_table.setItem(row_position, 0, title_item)

            # Store task data
            title_item.setData(Qt.UserRole, task["id"])
            title_item.setData(Qt.UserRole + 1, task.get("task_list_id"))

            # Add updated timestamp
            updated_datetime = datetime.datetime.fromisoformat(task["updated"])
            updated_local_time = updated_datetime.astimezone()
            updated_local_time_str = updated_local_time.strftime("%Y-%m-%d %H:%M:%S")
            self.window.task_table.setItem(
                row_position, 1, QTableWidgetItem(updated_local_time_str)
            )

            # Add due date or completion date
            if "status" in task and task["status"] == "completed":
                completion_date = datetime.datetime.fromisoformat(task["completed"])
                self.window.task_table.setItem(
                    row_position,
                    2,
                    QTableWidgetItem(completion_date.strftime("%Y-%m-%d %H:%M:%S")),
                )
            elif "due" in task:
                due_datetime = datetime.datetime.fromisoformat(task["due"])
                due_local_time = due_datetime.astimezone()
                due_local_time_str = due_local_time.strftime("%Y-%m-%d %H:%M:%S")
                self.window.task_table.setItem(
                    row_position, 2, QTableWidgetItem(due_local_time_str)
                )
            else:
                self.window.task_table.setItem(row_position, 2, QTableWidgetItem(""))

            # Add notes button if notes exist
            task_notes = task.get("notes")
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
        self.window.refresh_button.setEnabled(True)

    def refresh_tasks(self):
        current_item = self.currentItem()
        if current_item:
            self.load_tasks_by_task_list(current_item)
