import csv
import datetime

from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import Qt
from openpyxl import Workbook

HEADER = [
    "Number",
    "Task List",
    "ID",
    "Title",
    "Updated",
    "Due",
    "Status",
    "Notes",
    "Web Link",
]


def export_tasks_to_excel(tasks, filename="tasks.xlsx"):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    wb = Workbook()
    ws = wb.active
    # Add a header row
    ws.append(HEADER)
    # Append task data
    sequence_number = 1
    for task in tasks:
        ws.append(
            [
                sequence_number,
                task["tasklist_name"],
                task["id"],
                task["title"],
                task["updated"],
                task["due"],
                task["status"],
                task["notes"],
                task["webViewLink"],
            ]
        )
        sequence_number += 1
    wb.save(filename)
    QApplication.restoreOverrideCursor()
    print(f"Tasks exported to {filename}")
    show_file_location_dialog(filename)


def export_tasks_to_csv(tasks, filename="tasks.csv"):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "number",
            "tasklist_name",
            "id",
            "title",
            "updated",
            "due",
            "status",
            "notes",
            "webViewLink",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")

        # Write the header
        writer.writeheader()

        # Write the task data
        sequence_number = 1
        for task in tasks:
            writer.writerow({**{"number": sequence_number}, **task})
            sequence_number += 1
    QApplication.restoreOverrideCursor()
    print(f"Tasks exported to {filename}")
    show_file_location_dialog(filename)


def export_tasks_to_gsheet(tasks, service):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    # Create a new Google Spreadsheet with a name based on the current timestamp
    spreadsheet = {
        "properties": {
            "title": "tasks-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        }
    }
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )

    # Prepare the data to be written to the new spreadsheet
    data = [HEADER]
    sequence_number = 1
    for task in tasks:
        data.append(
            [
                sequence_number,
                task["tasklist_name"],
                task["id"],
                task["title"],
                task["updated"],
                task["due"],
                task["status"],
                task["notes"],
                task["webViewLink"],
            ]
        )
        sequence_number += 1

    # Write the data to the new spreadsheet
    body = {"values": data}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet["spreadsheetId"],
            range="A1:I" + str(len(data)),  # Updated here
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )
    QApplication.restoreOverrideCursor()


def show_file_location_dialog(file_path):
    dialog = QMessageBox()
    dialog.setWindowTitle("Xbitodowin")
    dialog.setText("Export Successful!")
    dialog.setInformativeText(f"File exported to {file_path}.")

    # Play the OS default bell/ring sound
    QApplication.beep()

    dialog.exec_()
