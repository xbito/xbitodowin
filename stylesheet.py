UI_STYLESHEET = """
QMainWindow {
    background-color: #2E2E2E;
    color: #FFFFFF;
}
QGroupBox {
    border: 1px solid #444444;
    border-radius: 5px;
    margin-top: 0.5em;
    background-color: #3E3E3E;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
    color: #FFFFFF;
}
QLabel {
    color: #FFFFFF;
}
QRadioButton {
    padding: 3px;
    color: #FFFFFF;
}
QRadioButton::indicator {
    width: 13px;
    height: 13px;
}
QRadioButton::indicator::unchecked {
    border: 1px solid #CCCCCC;
    border-radius: 6px;
}
QRadioButton::indicator::checked {
    border: 1px solid #1E90FF;
    background-color: #1E90FF;
}
QLineEdit {
    border: 1px solid #444444;
    border-radius: 5px;
    padding: 5px;
    background-color: #3E3E3E;
    color: #FFFFFF;
}
QTableWidget {
    background-color: #2E2E2E;
    alternate-background-color: #333333;
    gridline-color: #444444;
    color: #FFFFFF;
    border: 1px solid #444444;
    border-radius: 5px;
}
QTableWidget::item {
    border: none;
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #1E90FF;
    color: #FFFFFF;
}
QHeaderView {
    background-color: #2E2E2E;
    border: none;
}
QHeaderView::section {
    background-color: #2E2E2E;
    color: #FFFFFF;
    padding: 5px;
    border: none;
    border-right: 1px solid #444444;
    border-bottom: 1px solid #444444;
}
QHeaderView::section:horizontal {
    border-bottom: 1px solid #444444;
}
QHeaderView::section:vertical {
    border-right: 1px solid #444444;
}
QTableCornerButton::section {
    background-color: #2E2E2E;
    border: none;
    border-right: 1px solid #444444;
    border-bottom: 1px solid #444444;
}
QScrollBar:vertical {
    background-color: #2E2E2E;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #444444;
    border-radius: 6px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QTableWidget {
    border: 1px solid #444444;
    border-radius: 5px;
    background-color: #3E3E3E;
    color: #FFFFFF;
}
QTableWidget QHeaderView::section {
    background-color: #2E2E2E;
    padding: 5px;
    border: 1px solid #444444;
    color: #FFFFFF;
}
QTableWidget QTableCornerButton::section {
    background-color: #2E2E2E;
    border: 1px solid #444444;
}
TaskListSidebar {
    border: 1px solid #444444;
    border-radius: 5px;
    background-color: #3E3E3E;
    color: #FFFFFF;
}
TaskListSidebar::item {
    padding: 5px;
}
TaskListSidebar::item:selected {
    background-color: #1E90FF;
    color: #FFFFFF;
}
QLabel#userAvatar {
    border: 4px solid #1E90FF;
    border-radius: 27px;
    width: 50px;
    height: 50px;
}
QPushButton#refreshButton {
    border-radius: 10px;
    padding: 5px;
    background-color: #1E90FF;
    color: #FFFFFF;
}
QPushButton#refreshButton:disabled {
    background-color: #A9A9A9;
}
QLabel#motivationalPhrase {
    font-size: 16px;
    font-weight: bold;
}
QLabel#userName {
    font-size: 14px;
}
"""
