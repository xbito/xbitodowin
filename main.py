import sys

from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QApplication

from TaskListWindow import TaskListWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskListWindow(app)
    window.start()
    window.show()
    sys.exit(app.exec())
