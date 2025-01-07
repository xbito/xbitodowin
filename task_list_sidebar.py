from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QTableWidgetItem,
)


class TaskListSidebar(QListWidget):
    """A sidebar widget for displaying multiple Google Task lists."""

    def __init__(self, parent=None, window=None):
        """
        Initialize the TaskListSidebar.

        :param parent: Optional parent widget.
        :param window: Reference to the main application window.
        """
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemClicked.connect(self.load_tasks_by_task_list)
        self.window = window

    def fetch_tasks_by_task_list(self, item):
        """
        Fetch tasks for the given task list item.

        :param item: A QListWidgetItem containing task list info.
        :return: List of tasks from the selected task list.
        """
        if isinstance(item, str):
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
        """
        Clear and reload the main task table with the given tasks.

        :param tasks: List of task dictionaries to display.
        """
        self.window.task_table.setRowCount(0)

        for task in tasks:
            row_position = self.window.task_table.rowCount()
            self.window.task_table.insertRow(row_position)

            # Title column (index 0)
            title_item = QTableWidgetItem(task["title"] or "")
            self.window.task_table.setItem(row_position, 0, title_item)

            # Store all task data in user roles
            title_item.setData(Qt.UserRole, task["id"])
            title_item.setData(Qt.UserRole + 1, task.get("task_list_id"))
            title_item.setData(Qt.UserRole + 2, task.get("updated", ""))
            title_item.setData(Qt.UserRole + 3, task.get("notes", ""))
            title_item.setData(Qt.UserRole + 4, task.get("webViewLink", ""))
            title_item.setData(Qt.UserRole + 5, task.get("due", ""))
            title_item.setData(Qt.UserRole + 6, task.get("completed", ""))
            title_item.setData(Qt.UserRole + 7, task.get("status", ""))

            # Display date column (index 1)
            display_date = ""
            if task.get("status") == "completed" and "completed" in task:
                display_date = task["completed"].split("T")[0]  # Just the date part
            elif "updated" in task:
                display_date = task["updated"].split("T")[0]  # Just the date part

            self.window.task_table.setItem(
                row_position, 1, QTableWidgetItem(display_date)
            )

        self.window.task_table.clearSelection()  # Clear table selection to hide details pane when none is selected

    def load_tasks_by_task_list(self, item):
        """
        Load tasks for the given item and render them.

        :param item: A QListWidgetItem containing task list info.
        """
        tasks = self.fetch_tasks_by_task_list(item)
        self.render_tasks(tasks)
        self.window.refresh_button.setEnabled(True)

    def refresh_tasks(self):
        """Refresh tasks by reloading for the currently selected item."""
        current_item = self.currentItem()
        if current_item:
            self.load_tasks_by_task_list(current_item)
