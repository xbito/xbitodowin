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
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
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
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
QTableWidget {
    border: 1px solid #444444;
    border-radius: 5px;
    background-color: #3E3E3E;
    color: #FFFFFF;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
QTableWidget QHeaderView::section {
    background-color: #2E2E2E;
    padding: 5px;
    border: 1px solid #444444;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
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
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
TaskListSidebar::item {
    padding: 5px;
}
TaskListSidebar::item:selected {
    background-color: #1E90FF;
    color: #FFFFFF;
}
"""
