# Standard library imports
import os
import webbrowser
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any

# Third-party imports
import pytz
import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QGuiApplication,
    QIcon,
    QPixmap,
    QPainter,
    QBrush,
    QColor,
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QSizePolicy,
    QHeaderView,
    QGraphicsDropShadowEffect,
)
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Local imports
from task_list_sidebar import TaskListSidebar
from motivation import get_motivational_phrase
from stylesheet import UI_STYLESHEET
from menu import TaskListMenu
from task_details_panel import TaskDetailsPanel

SCOPES = [
    "https://www.googleapis.com/auth/tasks", 
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


class TaskListWindow(QMainWindow):
    """Main window to display and manage user tasks."""

    def __init__(self, app):
        """
        Initialize the TaskListWindow.

        :param app: The QApplication reference.
        """
        self.app = app
        self.is_fetching_tasks = False  # Add a flag to track task fetching
        # Load Google Tasks API
        if os.path.exists("credentials/token.json"):
            self.creds = Credentials.from_authorized_user_file(
                "credentials/token.json", SCOPES
            )
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", SCOPES
            )
            self.creds = flow.run_local_server(port=0)
            with open("credentials/token.json", "w") as token:
                token.write(self.creds.to_json())

        self.tasks_service = build("tasks", "v1", credentials=self.creds)
        # Load Google Sheets API
        self.sheets_service = build("sheets", "v4", credentials=self.creds)
        # Load User Profile API
        self.profile_service = build("oauth2", "v2", credentials=self.creds)
        super().__init__()
        self.initUI()
        self.apply_shadows()  # Add this line

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
        """Initialize the user interface components."""
        self.setWindowTitle("Xbitodowin | Google Tasks Viewer")
        self.setWindowIcon(QIcon("output.ico.32x32.png"))
        self.center_window()
        self.create_filter_group_box()
        self.create_sidebar()
        self.create_main_layout()
        self.create_search_bar()
        self.create_task_table()
        self.create_horizontal_layout()
        self.create_vertical_layout()
        self.menu = TaskListMenu(self)  # Replace create_menu() with this line
        self.create_refresh_button()
        self.setStyleSheet(UI_STYLESHEET)

    def center_window(self) -> None:
        """Centers the window on the primary screen."""
        # Get the resolution of the screen
        screenRect = QGuiApplication.primaryScreen().availableGeometry()
        # Calculate the center position of the screen
        centerPositionX = (screenRect.width() - 1280) // 2
        centerPositionY = (screenRect.height() - 800) // 2
        # Set the geometry of your application to the calculated center position
        self.setGeometry(centerPositionX, centerPositionY, 1280, 800)

    def create_sidebar(self):
        """Create the sidebar layout which includes the user info and task list."""
        # Create a sidebar for task lists
        self.task_list_sidebar = TaskListSidebar(window=self)
        # Fetch user info, email
        user_info = self.get_user_info()
        self.user_avatar_label = QLabel()
        self.user_avatar_label.setObjectName("userAvatar")
        # Fetch the image data from the URL
        image_url = self.profile_service.userinfo().get().execute()["picture"]
        response = requests.get(image_url)
        image_data = response.content  # Get the image data as bytes

        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Create a circular mask
        mask = QPixmap(pixmap.size())
        mask.fill(Qt.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, pixmap.width(), pixmap.height())
        painter.end()

        # Apply the mask to the pixmap
        pixmap.setMask(mask.mask())

        self.user_avatar_label.setPixmap(
            pixmap.scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.user_avatar_label.setFixedSize(
            54, 54
        )  # Ensure the label is a square and accounts for the border
        self.user_avatar_label.setStyleSheet("")  # Remove inline style

        self.user_name_label = QLabel(user_info["name"])
        self.user_name_label.setObjectName("userName")  # Add object name for styling
        self.user_name_label.setWordWrap(False)
        self.user_name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.user_name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.user_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.user_name_label.setToolTip(user_info["name"])  # Show full name on hover

        # Create a layout for the user info
        self.user_info_layout = QHBoxLayout()
        self.user_info_layout.addWidget(self.user_avatar_label)
        self.user_info_layout.addWidget(self.user_name_label)
        self.user_info_layout.setSpacing(10)  # Add spacing between avatar and name
        self.user_info_layout.addStretch()  # Push the name to the left

        # Create a vertical layout for the sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.addLayout(self.user_info_layout)
        sidebar_layout.addWidget(self.filter_group_box)
        sidebar_layout.addWidget(self.task_list_sidebar)

        # Create a widget for the sidebar and set the layout
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(sidebar_layout)

        self.filter_group_box.setStyleSheet(
            "QGroupBox { border: 1px solid #ccc; border-radius: 4px; }"
        )
        self.filter_group_box.setFixedWidth(220)
        self.task_list_sidebar.setStyleSheet(
            "border: 1px solid #ccc; border-radius: 4px;"
        )
        self.task_list_sidebar.setFixedWidth(220)

        # Connect the currentItemChanged signal to the uncheck_radio_buttons method
        self.task_list_sidebar.currentItemChanged.connect(self.uncheck_radio_buttons)
        # Connect the currentItemChanged signal to the refresh_tasks method
        self.task_list_sidebar.currentItemChanged.connect(self.refresh_tasks)

    def create_filter_group_box(self):
        """Create and configure a group box containing radio buttons for filtering."""
        # Create a group box for filter options
        self.filter_group_box = QGroupBox("Filter tasks")
        self.filter_layout = QVBoxLayout()
        self.create_radio_buttons()
        # Set the filter layout to the group box
        self.filter_group_box.setLayout(self.filter_layout)

    def create_radio_buttons(self):
        """Create and connect radio buttons for different filtering modes."""
        # Create radio buttons for filter options
        self.today_radio_button = QRadioButton("Today")
        self.next_days_radio_button = QRadioButton("Next 7 Days")
        self.overdue_radio_button = QRadioButton("Overdue")
        self.recently_completed_radio_button = QRadioButton("Recently completed")
        self.all_radio_button = QRadioButton("All")  # Add new radio button

        # Connect the toggled signal to the filter_tasks method
        self.today_radio_button.toggled.connect(self.filter_tasks)
        self.next_days_radio_button.toggled.connect(self.filter_tasks)
        self.overdue_radio_button.toggled.connect(self.filter_tasks)
        self.recently_completed_radio_button.toggled.connect(self.filter_tasks)
        self.all_radio_button.toggled.connect(self.filter_tasks)  # Add new connection
        # Create a button group for the radio buttons
        self.radio_button_group = QButtonGroup()
        self.radio_button_group.addButton(self.today_radio_button)
        self.radio_button_group.addButton(self.next_days_radio_button)
        self.radio_button_group.addButton(self.overdue_radio_button)
        self.radio_button_group.addButton(self.recently_completed_radio_button)
        self.radio_button_group.addButton(
            self.all_radio_button
        )  # Add new button to group
        # Connect the buttonClicked signal to the deselect_task_list method
        self.radio_button_group.buttonClicked.connect(self.deselect_task_list)

        # Add radio buttons to the filter layout
        self.filter_layout.addWidget(self.today_radio_button)
        self.filter_layout.addWidget(self.next_days_radio_button)
        self.filter_layout.addWidget(self.overdue_radio_button)
        self.filter_layout.addWidget(self.recently_completed_radio_button)
        self.filter_layout.addWidget(self.all_radio_button)  # Add new button to layout

    def create_main_layout(self):
        """Create the main vertical layout for search bar, table, etc."""
        # Create a main layout for the content
        self.main_layout = QVBoxLayout()

    def create_search_bar(self):
        """Set up the QLineEdit for searching tasks."""
        # Create a search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tasks...")
        self.search_bar.textChanged.connect(self.search_tasks)
        self.main_layout.addWidget(self.search_bar)

    def create_task_table(self) -> None:
        """Creates and configures the main task table widget."""
        self.task_table = QTableWidget()
        self.task_table.setRowCount(0)
        # Only two columns now: Title and Due Date
        self.task_table.setColumnCount(2)
        headers = ["Title", "Last Updated"]
        self.task_table.setHorizontalHeaderLabels(headers)
        self.task_table.setAlternatingRowColors(True)
        self._configure_table_headers()
        self.main_layout.addWidget(self.task_table)

    def _configure_table_headers(self) -> None:
        """Configures the table headers and sizing."""
        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        vertical_header = self.task_table.verticalHeader()
        vertical_header.setDefaultSectionSize(30)

    def create_horizontal_layout(self):
        """Lay out the sidebar, the main vertical layout, and the new details panel."""
        # Create a horizontal layout for the sidebar and main content
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.sidebar_widget)
        horizontal_layout.addLayout(self.main_layout)

        # Create the details panel and add it to the layout
        self.details_panel = TaskDetailsPanel(table=self.task_table)
        horizontal_layout.addWidget(self.details_panel)

        # Create a central widget and set the main layout
        # Set the horizontal layout as the central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(horizontal_layout)

    def create_vertical_layout(self):
        """Place the motivational phrase and central content vertically."""
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

    def show_motivational_phrase(self):
        self.phrase = get_motivational_phrase()
        self.motivational_phrase_label = QLabel(self.phrase)
        self.motivational_phrase_label.setAlignment(Qt.AlignCenter)
        # Remove inline style, using id selector instead
        self.motivational_phrase_label.setObjectName("motivationalPhrase")
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
        self.task_table.setColumnWidth(1, due_date_width)

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
        """Uncheck any checked radio buttons in the filter group."""
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
        if self.is_fetching_tasks:
            print("Task fetching is already in progress. Skipping this request.")
            return

        self.is_fetching_tasks = True
        self.set_waiting_cursor()
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
        elif (
            self.all_radio_button.isChecked()
            or self.today_radio_button.isChecked()
            or self.next_days_radio_button.isChecked()
            or self.overdue_radio_button.isChecked()
        ):
            all_tasks = self.fetch_all_tasks()
            # Reset table headers for other filters
            self.task_table.setHorizontalHeaderLabels(
                ["Title", "Updated", "Due Date", "Notes", "Priority"]
            )
        # Filter tasks based on the selected filter
        if self.all_radio_button.isChecked():  # Add new condition for All filter
            filtered_tasks = all_tasks  # Show all tasks without filtering
        elif self.today_radio_button.isChecked():
            filtered_tasks = [
                task
                for task in all_tasks
                if "due" in task
                and datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                == current_date
            ]
        elif self.next_days_radio_button.isChecked():
            seven_days_from_now = current_date + timedelta(days=7)
            filtered_tasks = [
                task
                for task in all_tasks
                if "due" in task
                and current_date
                <= datetime.strptime(task["due"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                <= seven_days_from_now
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
            not self.all_radio_button.isChecked()  # Add new button to check
            and not self.today_radio_button.isChecked()
            and not self.next_days_radio_button.isChecked()
            and not self.overdue_radio_button.isChecked()
            and not self.recently_completed_radio_button.isChecked()
        ):
            # If no radio button is checked, do nothing
            self.reset_cursor()
            self.is_fetching_tasks = False
            return

        # Get the selected radio button
        selected_button = self.radio_button_group.checkedButton()

        if selected_button == self.next_days_radio_button:
            filtered_tasks = self.order_tasks_by_due_date(
                filtered_tasks, ascending=True
            )
        elif selected_button == self.overdue_radio_button:
            filtered_tasks = self.order_tasks_by_due_date(
                filtered_tasks, ascending=False
            )
        elif selected_button == self.recently_completed_radio_button:
            filtered_tasks = self.order_tasks_by_completed_date(
                filtered_tasks, ascending=False
            )

        self.task_list_sidebar.render_tasks(filtered_tasks)

        self.reset_cursor()
        self.is_fetching_tasks = False

    def order_tasks_by_due_date(self, tasks, ascending):
        """
        Sorts the given tasks by their 'due' field, returning the ordered list.
        Tasks with no due date are placed at the end.
        """
        tasks_with_due = [t for t in tasks if "due" in t and t["due"]]
        tasks_without_due = [t for t in tasks if not ("due" in t and t["due"])]
        tasks_with_due.sort(
            key=lambda t: datetime.strptime(t["due"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            reverse=not ascending,
        )
        return tasks_with_due + tasks_without_due

    def order_tasks_by_completed_date(self, tasks, ascending):
        """
        Sorts the given tasks by their completion date (in 'completed'),
        returning the ordered list. Tasks with no completed date are last.
        """
        tasks_with_completed = [t for t in tasks if "completed" in t and t["completed"]]
        tasks_without_completed = [
            t for t in tasks if not ("completed" in t and t["completed"])
        ]
        tasks_with_completed.sort(
            key=lambda t: datetime.strptime(t["completed"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            reverse=not ascending,
        )
        return tasks_with_completed + tasks_without_completed

    def refresh_tasks(self, current_item: Optional[QListWidgetItem] = None) -> None:
        """
        Refreshes the tasks associated with the currently selected task list.

        Args:
            current_item (Optional[QListWidgetItem]): The currently selected item
        """
        self.set_waiting_cursor()
        if current_item:
            # Get the ID of the task list associated with the current item
            task_list_id = current_item.data(Qt.UserRole)
        else:
            task_list_id = self.task_list_sidebar.current_tasklist_id
        # Refresh the tasks associated with this task list
        self.task_list_sidebar.load_tasks_by_task_list(task_list_id)
        self.reset_cursor()

    def create_refresh_button(self):
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setEnabled(False)
        # Remove inline style, using id selector instead
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_tasks)
        self.main_layout.addWidget(self.refresh_button)

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
                    self.tasks_service.tasklists().list(pageToken=page_token).execute()
                )
            except RefreshError as e:
                # If the token has expired, refresh it and retry the request
                print("Token has expired: {}".format(e))
                self.refresh_token()
                tasklists_response = (
                    self.tasks_service.tasklists().list(pageToken=page_token).execute()
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

    def fetch_non_completed_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetches all non-completed tasks from all task lists.

        Returns:
            List[Dict[str, Any]]: A list of task dictionaries containing task details
        """
        print("Fetching non-completed tasks...")
        all_tasks = []
        task_lists = self.tasks_service.tasklists().list().execute().get("items", [])

        def fetch_non_completed_tasks_for_list(task_list):
            tasks = []
            page_token = None
            while True:
                try:
                    response = (
                        self.tasks_service.tasks()
                        .list(tasklist=task_list["id"], pageToken=page_token)
                        .execute()
                    )
                    non_completed_tasks = [
                        {
                            "tasklist_name": task_list["title"],
                            "id": task["id"],
                            "title": task["title"],
                            "updated": task["updated"],
                            "due": task["due"] if "due" in task else "",
                            "status": task["status"],
                            "notes": task.get("notes"),
                            "webViewLink": task.get("webViewLink", ""),
                            "task_list_id": task_list["id"],  # Add this line
                        }
                        for task in response.get("items", [])
                        if task["status"] != "completed"
                    ]
                    tasks.extend(non_completed_tasks)
                    page_token = response.get("nextPageToken")
                    if not page_token:
                        break
                except Exception as e:
                    print(
                        f"Error fetching non-completed tasks for list {task_list['title']}: {e}"
                    )
                    break
            return tasks

        with ThreadPoolExecutor(max_workers=1) as executor:  # Use a single thread
            futures = [
                executor.submit(fetch_non_completed_tasks_for_list, task_list)
                for task_list in task_lists
            ]
            for future in futures:
                try:
                    all_tasks.extend(future.result())
                except Exception as e:
                    print(f"Error in future result: {e}")

        print(f"Total non-completed tasks fetched: {len(all_tasks)}")
        return all_tasks

    def fetch_all_tasks(self, completed: bool = False) -> List[Dict[str, Any]]:
        """
        Fetches all tasks from all task lists.

        Args:
            completed (bool): If True, fetches only completed tasks from the last week

        Returns:
            List[Dict[str, Any]]: A list of task dictionaries containing task details
        """
        print("Fetching all tasks...")
        all_tasks = []
        task_lists = self.tasks_service.tasklists().list().execute().get("items", [])

        def fetch_tasks_for_list(task_list):
            tasks = []
            page_token = None
            while True:
                try:
                    if completed:
                        one_week_ago = datetime.now() - timedelta(days=7)
                        one_week_ago_rfc3339 = one_week_ago.isoformat() + "Z"
                        response = (
                            self.tasks_service.tasks()
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
                            self.tasks_service.tasks()
                            .list(tasklist=task_list["id"], pageToken=page_token)
                            .execute()
                        )
                    # Enrich tasks with task list information
                    for task in response.get("items", []):
                        task["task_list_id"] = task_list["id"]  # Add task list ID
                        task["tasklist_name"] = task_list["title"]  # Add task list name
                        tasks.append(task)
                    page_token = response.get("nextPageToken")
                    if not page_token:
                        break
                except Exception as e:
                    print(f"Error fetching tasks for list {task_list['title']}: {e}")
                    break
            return tasks

        with ThreadPoolExecutor(max_workers=1) as executor:  # Use a single thread
            futures = [
                executor.submit(fetch_tasks_for_list, task_list)
                for task_list in task_lists
            ]
            for future in futures:
                try:
                    all_tasks.extend(future.result())
                except Exception as e:
                    print(f"Error in future result: {e}")

        print(f"Total tasks fetched: {len(all_tasks)}")
        return all_tasks

    def start(self):
        self.load_task_lists()
        # Connect selection change to update details panel
        self.task_table.itemSelectionChanged.connect(
            self.details_panel.update_details_panel
        )

    def handle_title_click(self, row, column):
        if column == 0:
            item = self.task_table.item(row, 0)
            if item:
                # Get the task ID from the data stored in the item
                task_id = item.data(Qt.UserRole)
                # Use the task ID to fetch the task details
                task_details = (
                    self.tasks_service.tasks()
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

                # After fetching the web_view_link, store it so update_details_panel can display it
                if web_view_link:
                    # We'll encode the link in one of the data roles for the row.
                    item.setData(Qt.UserRole + 4, web_view_link)

    def set_waiting_cursor(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def reset_cursor(self):
        QApplication.restoreOverrideCursor()

    def apply_shadow(self, widget: QWidget, radius: int = 8, offset: int = 2) -> None:
        """
        Applies a drop shadow effect to a widget.

        Args:
            widget (QWidget): The widget to apply the shadow to
            radius (int): The blur radius of the shadow
            offset (int): The vertical offset of the shadow
        """
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(radius)
        shadow.setXOffset(0)
        shadow.setYOffset(offset)
        shadow.setColor(QColor(0, 0, 0, 80))
        widget.setGraphicsEffect(shadow)

    def apply_shadows(self):
        """Apply drop shadows to key widgets in the UI."""
        # Apply shadows to main UI elements
        self.apply_shadow(self.filter_group_box)
        self.apply_shadow(self.search_bar)
        self.apply_shadow(self.task_table)
        self.apply_shadow(self.task_list_sidebar)
        self.apply_shadow(self.sidebar_widget)

        # Reduce shadow size for smaller elements
        self.apply_shadow(self.refresh_button, radius=4, offset=1)
        self.apply_shadow(self.refresh_button, radius=4, offset=1)
