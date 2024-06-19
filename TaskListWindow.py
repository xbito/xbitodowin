from TaskListSidebar import TaskListSidebar
from exports import export_tasks_to_csv, export_tasks_to_excel, export_tasks_to_gsheet
from motivation import get_motivational_phrase
from stylesheet import UI_STYLESHEET

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QTableWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
)
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os
import webbrowser
from datetime import datetime, timedelta
import pytz

SCOPES = [
    "https://www.googleapis.com/auth/tasks.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


class TaskListWindow(QMainWindow):
    def __init__(self, app):
        self.app = app
        # Load Google Tasks API
        if os.path.exists("credentials/token.json"):
            self.creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)
            if not self.creds or not self.creds.valid:
                print("Creds invalid")
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("Refreshing token")
                    self.creds.refresh(Request())
                else:
                    print("Getting new token")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials/credentials.json", SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("credentials/token.json", "w") as token:
                    token.write(self.creds.to_json())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials/credentials.json", SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open("credentials/token.json", "w") as token:
                token.write(self.creds.to_json())

        self.service = build("tasks", "v1", credentials=self.creds)
        # Load Google Sheets API
        self.sheets_service = build("sheets", "v4", credentials=self.creds)
        # Load User Profile API
        self.profile_service = build("oauth2", "v2", credentials=self.creds)
        super().__init__()
        self.about_popup = None
        self.initUI()

    def get_user_info(self):
        user_info = self.profile_service.userinfo().get().execute()
        return user_info

    def refresh_token(self):
        # Check if the token has expired
        if not self.creds.valid:
            # Refresh the token
            try:
                self.creds.refresh_grant(Request())
            except RefreshError as e:
                # Token has expired, refresh it
                print(f"Token has expired: {e}")
                self.creds.refresh_grant(Request())
            with open("credentials/token.json", "w") as token:
                token.write(self.creds.to_json())

    def initUI(self):
        self.setWindowTitle(
            "Xbitodowin | Google Tasks Viewer"
        )  # Set the icon for the application
        icon_path = "output.ico.32x32.png"
        self.app.setWindowIcon(QIcon(icon_path))
        # Get the resolution of the screen
        screenRect = QGuiApplication.primaryScreen().availableGeometry()

        # Calculate the center position of the screen
        centerPositionX = (screenRect.width() - 1280) // 2
        centerPositionY = (screenRect.height() - 800) // 2

        # Set the geometry of your application to the calculated center position
        self.setGeometry(centerPositionX, centerPositionY, 1280, 800)

        # Create a sidebar for task lists
        self.task_list_sidebar = TaskListSidebar(window=self)

        # Create a group box for filter options
        self.filter_group_box = QGroupBox("Filter tasks")
        self.filter_layout = QVBoxLayout()

        # Create a main layout for the content
        main_layout = QVBoxLayout()

        # Fetch user info, email
        self.user_email_label = QLabel(self.get_user_info()["email"])
        main_layout.addWidget(self.user_email_label)

        # Create radio buttons for filter options
        self.today_radio_button = QRadioButton("Today")
        self.next_days_radio_button = QRadioButton("Next Days")
        self.overdue_radio_button = QRadioButton("Overdue")
        self.recently_completed_radio_button = QRadioButton("Recently completed")

        # Connect the toggled signal to the filter_tasks method
        self.today_radio_button.toggled.connect(self.filter_tasks)
        self.next_days_radio_button.toggled.connect(self.filter_tasks)
        self.overdue_radio_button.toggled.connect(self.filter_tasks)
        self.recently_completed_radio_button.toggled.connect(self.filter_tasks)

        # Create a button group for the radio buttons
        self.radio_button_group = QButtonGroup()
        self.radio_button_group.addButton(self.today_radio_button)
        self.radio_button_group.addButton(self.next_days_radio_button)
        self.radio_button_group.addButton(self.overdue_radio_button)
        self.radio_button_group.addButton(self.recently_completed_radio_button)

        # Connect the buttonClicked signal to the deselect_task_list method
        self.radio_button_group.buttonClicked.connect(self.deselect_task_list)

        # Connect the currentItemChanged signal to the uncheck_radio_buttons method
        self.task_list_sidebar.currentItemChanged.connect(self.uncheck_radio_buttons)

        # Add radio buttons to the filter layout
        self.filter_layout.addWidget(self.today_radio_button)
        self.filter_layout.addWidget(self.next_days_radio_button)
        self.filter_layout.addWidget(self.overdue_radio_button)
        self.filter_layout.addWidget(self.recently_completed_radio_button)

        # Set the filter layout to the group box
        self.filter_group_box.setLayout(self.filter_layout)

        # Create a vertical layout for the sidebar and filter group box
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.filter_group_box)
        sidebar_layout.addWidget(self.task_list_sidebar)

        # Create a widget for the sidebar and set the layout
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(sidebar_layout)

        # Create a search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tasks...")
        self.search_bar.textChanged.connect(self.search_tasks)
        main_layout.addWidget(self.search_bar)

        self.task_table = QTableWidget()
        self.task_table.setRowCount(0)
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(
            ["Title", "Updated", "Due Date", "Notes", "Priority"]
        )
        # Add the table to the main layout
        main_layout.addWidget(self.task_table)

        # Create a horizontal layout for the sidebar and main content
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.sidebar_widget)
        horizontal_layout.addLayout(main_layout)

        # Create a central widget and set the main layout
        # Set the horizontal layout as the central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(horizontal_layout)

        # Create a new QVBoxLayout
        vertical_layout = QVBoxLayout()

        # Create the motivational_phrase_label and add it to the vertical layout
        self.show_motivational_phrase()
        vertical_layout.addWidget(self.motivational_phrase_label)

        # Add the central_widget to the vertical layout
        vertical_layout.addWidget(self.central_widget)

        # Create a new central widget and set the vertical layout as its layout
        new_central_widget = QWidget()
        new_central_widget.setLayout(vertical_layout)
        self.setCentralWidget(new_central_widget)

        # Create a menu bar
        self.create_menu()

        # Connect the cellClicked signal to the handle_title_click method
        self.task_table.cellClicked.connect(self.handle_title_click)

        # Connect the currentItemChanged signal to the refresh_tasks method
        self.task_list_sidebar.currentItemChanged.connect(self.refresh_tasks)

        # Set a flat stylesheet for the window
        self.setStyleSheet(UI_STYLESHEET)

    def show_motivational_phrase(self):
        phrase = get_motivational_phrase()
        # Display the Phrase at the top of the UI
        self.motivational_phrase_label = QLabel(phrase)
        self.motivational_phrase_label.setAlignment(Qt.AlignCenter)
        self.motivational_phrase_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        self.central_widget.layout().insertWidget(0, self.motivational_phrase_label)

    def resizeEvent(self, event):
        # Get the total number of columns
        column_count = self.task_table.columnCount()

        # Calculate the width for the title column (30% of the main content area)
        main_content_width = event.size().width() - 200  # Adjust the sidebar width
        title_column_width = int(main_content_width * 0.4)

        # Set the width for the title column
        self.task_table.setColumnWidth(0, title_column_width)

        # Calculate the remaining width for the other columns
        remaining_width = main_content_width - title_column_width

        # Calculate the width for the Notes, Due Date, and Updated columns
        notes_width = int(remaining_width * 0.2)  # Adjust the percentage as needed
        due_date_width = int(remaining_width * 0.2)
        updated_width = int(remaining_width * 0.2)

        # Set the width for the Notes, Due Date, and Updated columns
        self.task_table.setColumnWidth(1, updated_width)
        self.task_table.setColumnWidth(2, due_date_width)
        self.task_table.setColumnWidth(3, notes_width)

        # Adjust the width of the sidebar and main content area
        sidebar_width = 200  # Set the desired width for the sidebar
        main_content_width = event.size().width() - sidebar_width
        self.task_list_sidebar.setFixedWidth(sidebar_width)
        # Set the maximum width of the filter group box to the width of the task list sidebar
        self.filter_group_box.setMaximumWidth(self.task_list_sidebar.width())
        self.sidebar_widget.setMaximumWidth(self.task_list_sidebar.width() + 10)

        super(self.__class__, self).resizeEvent(event)

    def deselect_task_list(self):
        # Deselect any selected item in the task list sidebar
        self.task_list_sidebar.clearSelection()

    def uncheck_radio_buttons(self):
        # Uncheck any checked radio button
        self.radio_button_group.setExclusive(False)
        self.today_radio_button.setChecked(False)
        self.next_days_radio_button.setChecked(False)
        self.overdue_radio_button.setChecked(False)
        self.radio_button_group.setExclusive(True)

    def search_tasks(self, text):
        """
        Filters the tasks based on the entered criteria.
        Args:
            text (str): The criteria to filter the tasks by.
        """
        text = text.lower()  # Convert the search text to lowercase
        for row in range(self.task_table.rowCount()):
            title = (
                self.task_table.item(row, 0).text().lower()
            )  # Convert the title to lowercase
            if text not in title:
                self.task_table.hideRow(row)
            else:
                self.task_table.showRow(row)

    def filter_tasks(self):
        """
        Filters the tasks based on the selected filter.
        """
        # Get the current date in the user's timezone
        user_tz = pytz.timezone("America/New_York")  # Replace with your timezone
        current_date = datetime.now(user_tz).date()

        # Filter tasks based on the selected filter
        # Do it separately because we are changing the headers
        if self.recently_completed_radio_button.isChecked():
            all_tasks = self.fetch_all_tasks(completed=True)
            filtered_tasks = [
                task for task in all_tasks if task["status"] == "completed"
            ]
            print(f"Filtered {len(filtered_tasks)} completed tasks")
            # Update table headers for completed tasks
            self.task_table.setHorizontalHeaderLabels(
                ["Title", "Updated", "Completed", "Notes", "Priority"]
            )
        else:
            all_tasks = self.fetch_all_tasks()
            # Reset table headers for other filters
            self.task_table.setHorizontalHeaderLabels(
                ["Title", "Updated", "Due Date", "Notes", "Priority"]
            )
        # Filter tasks based on the selected filter
        if self.today_radio_button.isChecked():
            filtered_tasks = [
                task
                for task in all_tasks
                if "due" in task
                and datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                == current_date
            ]
        elif self.next_days_radio_button.isChecked():
            filtered_tasks = [
                task
                for task in all_tasks
                if "due" in task
                and datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                > current_date
            ]
        elif self.overdue_radio_button.isChecked():
            filtered_tasks = [
                task
                for task in all_tasks
                if "due" in task
                and datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                < current_date
            ]
            pass
        elif (
            not self.today_radio_button.isChecked()
            and not self.next_days_radio_button.isChecked()
            and not self.overdue_radio_button.isChecked()
            and not self.recently_completed_radio_button.isChecked()
        ):
            # If no radio button is checked, do nothing
            return

        self.task_list_sidebar.render_tasks(filtered_tasks)

        # Get the selected radio button
        selected_button = self.radio_button_group.checkedButton()

        if selected_button == self.next_days_radio_button:
            # Order by due date with the closest day to today first
            self.order_tasks_by_due_date(ascending=True)
        elif selected_button == self.overdue_radio_button:
            # Order by due date, with the oldest day first
            self.order_tasks_by_due_date(ascending=False)
        elif selected_button == self.recently_completed_radio_button:
            # Order by Completed, most recently completed first and going to the past
            self.order_tasks_by_completed_date(ascending=False)

    def order_tasks_by_due_date(self, ascending):
        # Implement logic to order tasks by due date
        # Assuming the due date is in the 3rd column (index 2)
        # Debug: Print what ordering it is applying:
        print(
            "Ordering by due date {0}".format(
                "ascending" if ascending else "descending"
            )
        )
        self.task_table.sortItems(
            2, Qt.AscendingOrder if ascending else Qt.DescendingOrder
        )

    def order_tasks_by_completed_date(self, ascending):
        # Implement logic to order tasks by completed date, this replaced due date when displaying completed tasks
        # Assuming the completed date is in the 3rd column (index 2)
        # Debug: Print what ordering it is applying:
        print(
            "Ordering by completed date {0}".format(
                "ascending" if ascending else "descending"
            )
        )
        self.task_table.sortItems(
            2, Qt.AscendingOrder if ascending else Qt.DescendingOrder
        )

    def refresh_tasks(self, current_item, previous_item):
        """
        Refreshes the tasks associated with the currently selected task list.

        Args:
            current_item (QListWidgetItem): The currently selected item.
            previous_item (QListWidgetItem): The previously selected item.
        """
        # Get the ID of the task list associated with the current item
        task_list_id = current_item.data(Qt.UserRole)

        # Refresh the tasks associated with this task list
        # (Assuming you have a method to do this)
        self.task_list_sidebar.load_tasks_by_task_list(task_list_id)

    def create_menu(self):
        self.menu_bar = self.menuBar()
        help_menu = self.menu_bar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_popup)
        help_menu.addAction(help_action)

        export_menu = self.menuBar().addMenu("Export")
        export_csv_action = QAction("Export to CSV", self)
        export_csv_action.triggered.connect(
            lambda: export_tasks_to_csv(tasks=self.fetch_non_completed_tasks())
        )
        export_menu.addAction(export_csv_action)

        export_excel_action = QAction("Export to Excel", self)
        export_excel_action.triggered.connect(
            lambda: export_tasks_to_excel(tasks=self.fetch_non_completed_tasks())
        )
        export_menu.addAction(export_excel_action)

        export_gsheet_action = QAction("Export to Google Sheets", self)
        export_gsheet_action.triggered.connect(
            lambda: export_tasks_to_gsheet(
                tasks=self.fetch_non_completed_tasks(), service=self.sheets_service
            )
        )
        export_menu.addAction(export_gsheet_action)

    def show_about_popup(self):
        if self.about_popup is not None:
            self.about_popup.close()
        self.about_popup = QWidget()
        self.about_popup.setWindowTitle("About")
        self.about_popup.setGeometry(100, 100, 200, 100)
        label = QLabel(
            "Author: Fernando (Xbito) Gutierrez with the help of multiple AIs: Llama, qwen, gpt and Gemini"
        )
        self.about_popup.setLayout(QVBoxLayout())
        self.about_popup.layout().addWidget(label)
        self.about_popup.show()

    def close_about_popup(self):
        if self.about_popup is not None:
            self.about_popup.close()
            self.about_popup = None

    def show_notes(self, task_notes):
        # Create a new window to display the notes
        notes_dialog = QDialog()
        notes_dialog.setWindowTitle("Task Notes")
        # Add a text browser to display the notes
        notes_browser = QTextBrowser(notes_dialog)
        notes_browser.setReadOnly(True)
        notes_browser.setText(task_notes)
        # Get the size of the notes browser
        browser_size = notes_browser.sizeHint()
        # Resize the dialog to fit the notes browser
        notes_dialog.resize(browser_size.width(), browser_size.height())
        # Set the dialog to be modal (block until closed)
        notes_dialog.setModal(True)
        # Show the notes window
        notes_dialog.exec_()

    def load_task_lists(self):
        """
        Loads the task lists from the Google Tasks API and displays them in the sidebar.

        This method fetches the task lists from the API, handles any refresh errors,
        and then adds each task list as an item to the sidebar. The ID of each task list
        is stored as the item's data using the `Qt.UserRole` role.
        """
        page_token = None
        while True:
            try:
                # Attempt to fetch the task lists from the API
                tasklists_response = (
                    self.service.tasklists().list(pageToken=page_token).execute()
                )
            except RefreshError as e:
                # If the token has expired, refresh it and retry the request
                print("Token has expired: {}".format(e))
                self.refresh_token()
                tasklists_response = (
                    self.service.tasklists().list(pageToken=page_token).execute()
                )

            # Extract the list of task lists from the response
            task_lists = tasklists_response.get("items", [])
            for task_list in task_lists:
                # Create a new list item for the task list
                item = QListWidgetItem(task_list["title"])

                # Store the task list ID as the item's data using Qt.UserRole
                item.setData(Qt.UserRole, task_list["id"])

                # Add the item to the sidebar
                self.task_list_sidebar.addItem(item)

            page_token = tasklists_response.get("nextPageToken")
            if not page_token:
                break

    def fetch_non_completed_tasks(self):
        try:
            tasklists = self.service.tasklists().list().execute()
            all_tasks = []
            for tasklist in tasklists["items"]:
                # Initial call to fetch the first page of tasks
                request = self.service.tasks().list(tasklist=tasklist["id"])
                while request:
                    tasks_response = request.execute()
                    non_completed_tasks = [
                        {
                            "tasklist_name": tasklist[
                                "title"
                            ],  # Include the task list name
                            "id": task["id"],
                            "title": task["title"],
                            "updated": task["updated"],
                            "due": task["due"] if "due" in task else "",
                            "status": task["status"],
                            "notes": task.get("notes"),
                            "webViewLink": (
                                task["webViewLink"] if "webViewLink" in task else ""
                            ),
                        }
                        for task in tasks_response.get("items", [])
                        if task["status"] != "completed"
                    ]
                    all_tasks.extend(non_completed_tasks)
                    # Get the next page token and make the next request
                    request = self.service.tasks().list_next(
                        previous_request=request, previous_response=tasks_response
                    )

            return all_tasks
        except Exception as e:
            print("Failed to fetch tasks:", e)
            return []

    def fetch_all_tasks(self, completed=False):
        """Fetch all tasks from all task lists."""
        all_tasks = []
        task_lists = self.service.tasklists().list().execute().get("items", [])
        for task_list in task_lists:
            page_token = None
            while True:
                if completed:
                    one_week_ago = datetime.now() - timedelta(days=7)
                    one_week_ago_rfc3339 = one_week_ago.isoformat() + "Z"
                    response = (
                        self.service.tasks()
                        .list(
                            tasklist=task_list["id"],
                            showHidden=True,
                            completedMin=one_week_ago_rfc3339,
                            pageToken=page_token,
                        )
                        .execute()
                    )
                else:
                    response = (
                        self.service.tasks()
                        .list(tasklist=task_list["id"], pageToken=page_token)
                        .execute()
                    )
                tasks = response.get("items", [])
                print(f"Fetched {len(tasks)} tasks for task list {task_list['title']}")
                all_tasks.extend(tasks)
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        print(f"Total tasks fetched: {len(all_tasks)}")
        return all_tasks

    def start(self):
        self.load_task_lists()

    def closeEvent(self, event):
        self.close_about_popup()
        event.accept()

    def handle_title_click(self, row, column):
        if column == 0:
            item = self.task_table.item(row, 0)
            if item:
                # Get the task ID from the data stored in the item
                task_id = item.data(Qt.UserRole)
                # Use the task ID to fetch the task details
                task_details = (
                    self.service.tasks()
                    .get(
                        tasklist=self.task_list_sidebar.current_tasklist_id,
                        task=task_id,
                    )
                    .execute()
                )

                # Extract the webViewLink from the task details
                web_view_link = task_details.get("webViewLink")

                # Open the web view link in the browser
                if web_view_link:
                    webbrowser.open(web_view_link)
