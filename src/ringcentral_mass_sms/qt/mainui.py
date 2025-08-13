import csv
import os
import shutil
import threading
import time
import traceback
import requests
from PyQt6 import uic, QtGui
from PyQt6.QtCore import QThread, QDir, Qt, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QHeaderView, QLabel, QPushButton, QProgressBar, QTableWidgetItem, QFileDialog, QRadioButton, QHBoxLayout, QWidget, QColorDialog

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.icon_cache = {}
        QApplication.setStyle("fusion")
        uic.loadUi(os.path.join(self.path, "qtui", "main.ui"), self)
        self.setWindowIcon(self.get_icon('onthespot'))
        #self.centralwidget.setStyleSheet("background-color: #282828; color: white;")
        self.btn_save_config.setIcon(self.get_icon('save'))
        self.toggle_theme_button.setIcon(self.get_icon('light'))
        self.bind_button_inputs()
        self.show()

    def get_icon(self, name):
        if name not in self.icon_cache:
            icon_path = os.path.join(self.path, 'resources', 'icons', f'{name}.png')
            self.icon_cache[name] = QIcon(icon_path)
        return self.icon_cache[name]


    def open_theme_dialog(self):
        colorpicker = QColorDialog(self)
        colorpicker.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        colorpicker.setWindowFlag(Qt.WindowType.Dialog, True)
        colorpicker.setWindowTitle("Ringcentral Mass SMS - Color Picker")

        if colorpicker.exec() == QColorDialog.DialogCode.Accepted:
            color = colorpicker.selectedColor()

            if color.isValid():
                r, g, b = color.red(), color.green(), color.blue()
                luminance = (0.299 * r + 0.587 * g + 0.114 * b)

                if luminance < 128:
                    # Dark color, set light font and progress bar
                    stylesheet = f'background-color: {color.name()}; color: white;'
                else:
                    # Light color, set dark font and progress bar
                    stylesheet = f'background-color: {color.name()}; color: black;'
                self.centralwidget.setStyleSheet(stylesheet)


    def bind_button_inputs(self):
        # Connect button click signals
        self.btn_load_csv.clicked.connect(self.loadCSV)
        self.btn_next_entry.clicked.connect(self.nextRow)
        self.btn_previous_entry.clicked.connect(self.prevRow)
        self.btn_send_sms.clicked.connect(self.sendSMS)
        self.toggle_theme_button.clicked.connect(self.open_theme_dialog)


    def loadCSV(self):
        options = QFileDialog.Option(0)  # No specific options set; can customize if needed  
        filename, _ = QFileDialog.getOpenFileName(
        self,
        "Open CSV File",
        "",
        "CSV Files (*.csv);;All Files (*)",
        options=options  
        )
        if filename:
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                self.headers = next(reader, None)
                self.data = list(reader)
            self.updateTable()
            self.current_row_index = 0  
            self.updateRowDisplay()


    def updateTable(self):
        if not self.headers:
            return
        self.tableWidget.setColumnCount(len(self.headers))
        self.tableWidget.setHorizontalHeaderLabels(self.headers)
        self.tableWidget.setRowCount(len(self.data))
        for row_idx, row_data in enumerate(self.data):
            for col_idx, cell in enumerate(row_data):
                item = QTableWidgetItem(cell)
                self.tableWidget.setItem(row_idx, col_idx, item)

    def updateRowDisplay(self):
        if not self.data:
            self.label_pending_message.setPlainText("No data loaded.")
            return
        row_idx = self.current_row_index
        if 0 <= row_idx < len(self.data):
            row = self.data[row_idx]
            # Concatenate all items in the row
            row_str = ', '.join(row)
            template = self.label_settings_message.toPlainText()
            self.label_pending_phone_number.setText(f"To: {row[1]}")
            self.label_pending_message.setPlainText(template.format(name=row[0], phone_number=row[1]))
            #Row {row_idx + 1}: {row_str} {row} {self.label_settings_message.toPlainText()}")
        else:
            self.label_pending_message.setPlainText("Row index out of range.")


    def nextRow(self):
        try:
            if not self.data:
                return
            self.current_row_index += 1
            if self.current_row_index >= len(self.data):
                self.current_row_index = 0
            self.updateRowDisplay()
        except (IndexError, AttributeError):
            pass

    def prevRow(self):
        try:
            if not self.data:
                return
            self.current_row_index -= 1
            if self.current_row_index < 0:
                self.current_row_index = len(self.data) - 1
            self.updateRowDisplay()
        except (IndexError, AttributeError):
            pass

    def sendSMS(self):
        token = self.label_settings_token.text()
        fromphonenumber = f'{self.label_settings_personal_telus_number.text()}'.replace('-', '')
        tophonenumber = self.data[self.current_row_index][1].replace('-', '')
        text = self.label_pending_message.toPlainText()

        headers = {}
        headers['accept'] = 'application/json, text/plain, */*'
        headers['accept-language'] = 'en-US,en;q=0.9'
        headers['authorization'] = f'Bearer {token}'
        headers['cache-control'] = 'no-cache'
        headers['content-type'] = 'application/json'
        headers['origin'] = 'https://app.businessconnect.telus.com'
        headers['pragma'] = 'no-cache'
        headers['priority'] = 'u=1, i'
        headers['referer'] = 'https://app.businessconnect.telus.com/'
        headers['sec-ch-ua'] = '"Not)A;Brand";v="8", "Chromium";v="138"'
        headers['sec-ch-ua-mobile'] = '?0'
        headers['sec-ch-ua-platform'] = '"Linux"'
        headers['sec-fetch-dest'] = 'empty'
        headers['sec-fetch-mode'] = 'cors'
        headers['sec-fetch-site'] = 'cross-site'
        headers['user-agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        headers['x-user-agent'] = 'BusinessConnectWeb/25.2.20 (BusinessConnect; Linux/x86_64; build.3599; rev.c8fba4c5d)'

        data = {
            "from": {"phoneNumber": f"+1{fromphonenumber}"},
            "to": [{"phoneNumber": f"+1{tophonenumber}"}],
            "text": f"{text}"
        }

        response = requests.post(
            'https://api-ucc.ringcentral.com/restapi/v1.0/account/~/extension/~/sms',
            headers=headers,
            json=data
        )

        print(response.status_code)
        print(response.json())
