"""Menu management for the Xbitodowin application."""

from PySide6.QtGui import QAction
from exports import export_tasks_to_csv, export_tasks_to_excel, export_tasks_to_gsheet


class TaskListMenu:
    """Handles menu creation and management for the main window."""

    def __init__(self, window):
        """
        Initialize the menu manager.

        Args:
            window: The main window instance that will contain the menus
        """
        self.window = window
        self.menu_bar = window.menuBar()
        self.create_menus()

    def create_menus(self):
        """Create and populate all menu items."""
        self._create_help_menu()
        self._create_export_menu()

    def _create_help_menu(self):
        """Create the Help menu with About action."""
        help_menu = self.menu_bar.addMenu("Help")
        help_action = QAction("About", self.window)
        help_action.triggered.connect(self.window.show_about_popup)
        help_menu.addAction(help_action)

    def _create_export_menu(self):
        """Create the Export menu with various export options."""
        export_menu = self.menu_bar.addMenu("Export")

        # CSV export action
        export_csv_action = QAction("Export to CSV", self.window)
        export_csv_action.triggered.connect(
            lambda: self.export_tasks_to_csv(
                tasks=self.window.fetch_non_completed_tasks()
            )
        )
        export_menu.addAction(export_csv_action)

        # Excel export action
        export_excel_action = QAction("Export to Excel", self.window)
        export_excel_action.triggered.connect(
            lambda: self.export_tasks_to_excel(
                tasks=self.window.fetch_non_completed_tasks()
            )
        )
        export_menu.addAction(export_excel_action)

        # Google Sheets export action
        export_gsheet_action = QAction("Export to Google Sheets", self.window)
        export_gsheet_action.triggered.connect(
            lambda: self.export_tasks_to_gsheet(
                tasks=self.window.fetch_non_completed_tasks(),
                service=self.window.sheets_service,
            )
        )
        export_menu.addAction(export_gsheet_action)

    def export_tasks_to_csv(self, tasks):
        """Export tasks to CSV format."""
        export_tasks_to_csv(tasks=tasks)

    def export_tasks_to_excel(self, tasks):
        """Export tasks to Excel format."""
        export_tasks_to_excel(tasks=tasks)

    def export_tasks_to_gsheet(self, tasks, service):
        """Export tasks to Google Sheets."""
        export_tasks_to_gsheet(tasks=tasks, service=service)
