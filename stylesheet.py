UI_STYLESHEET = """
QMainWindow {
    background-color: #F5F5F5;
}
QGroupBox {
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    margin-top: 0.5em;
    background-color: #FFFFFF;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}
QLabel {
    color: #333333;
}
QRadioButton {
    padding: 3px;
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
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 5px;
    background-color: #FFFFFF;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
QTableWidget {
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    background-color: #FFFFFF;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
QTableWidget QHeaderView::section {
    background-color: #F5F5F5;
    padding: 5px;
    border: 1px solid #E0E0E0;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
QTableWidget QTableCornerButton::section {
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
}
"""
