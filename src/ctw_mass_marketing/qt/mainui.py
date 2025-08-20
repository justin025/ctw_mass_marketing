import re
import csv
import os
import shutil
import threading
import time
import traceback
import requests
import calendar
from datetime import datetime
from PyQt6 import uic, QtGui
from PyQt6.QtCore import QThread, QDir, Qt, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QFileDialog, QColorDialog, QMainWindow, QMessageBox, QAbstractItemView
from .settings import load_config, save_config, reset_config
from ..api.ringcentral import ringcentral_get_token, ringcentral_send_sms
from ..api.smtp import smtp_send_email
from ..runtimedata import app_path

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.icon_cache = {}
        uic.loadUi(os.path.join(app_path, "qt", "qtui", "main.ui"), self)
        self.setWindowIcon(self.get_icon('phone'))
        load_config(self)
        self.btn_save_config.setIcon(self.get_icon('save'))
        self.btn_reset_config.setIcon(self.get_icon('trash'))
        self.toggle_theme_button.setIcon(self.get_icon('light'))
        self.bind_button_inputs()
        self.show()

    def get_icon(self, name):
        if name not in self.icon_cache:
            icon_path = os.path.join(app_path, 'resources', 'icons', f'{name}.png')
            print(icon_path)
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
        self.btn_send_sms.clicked.connect(self.send)
        self.btn_save_config.clicked.connect(lambda: save_config(self))
        self.btn_reset_config.clicked.connect(lambda: reset_config(self))
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
        self.csv_table.setColumnCount(len(self.headers))
        self.csv_table.setHorizontalHeaderLabels(self.headers)
        self.csv_table.setRowCount(len(self.data))
        for row_idx, row_data in enumerate(self.data):
            for col_idx, cell in enumerate(row_data):
                item = QTableWidgetItem(cell)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                self.csv_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.CurrentChanged)
                self.csv_table.setItem(row_idx, col_idx, item)

    def updateRowDisplay(self):
        if self.current_row_index == 0:
            self.btn_previous_entry.setDisabled(True)
        else:
            self.btn_previous_entry.setDisabled(False)

        if self.current_row_index >= len(self.data) - 1:
            self.btn_next_entry.setDisabled(True)
        else:
            self.btn_next_entry.setDisabled(False)

        if not self.data:
            self.input_pending_message.setPlainText("No data loaded.")
            return


        pattern = re.compile(r'^(?:(?:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}))')
        if not pattern.match(self.csv_table.item(self.current_row_index, 1).text()):
            # Phone Number
            tophonenumber = self.csv_table.item(self.current_row_index, 1).text()
            fromphonenumber = self.input_ringcentral_phone_number.text()
            for char in ['+1', '+', '(', ')', ' ', '-']:
                tophonenumber = tophonenumber.replace(char, '')
                fromphonenumber = fromphonenumber.replace(char, '')
            self.current_type = 'ringcentral'
            self.tophonenumber = tophonenumber
            self.fromphonenumber = fromphonenumber
            contact_info = tophonenumber

        else:
            # Email
            self.current_type = 'smtp'
            self.toemail = self.csv_table.item(self.current_row_index, 1).text().replace(' ', '')
            contact_info = self.csv_table.item(self.current_row_index, 1).text().replace(' ', '')

        self.name = self.csv_table.item(self.current_row_index, 0).text()
        self.label_pending_recipient.setText(f"To: {contact_info}")


        if self.current_type == 'smtp':
            self.input_pending_subject.show()
            template_subject = self.input_template_subject.text()
            self.input_pending_subject.setText(template_subject.format(name=self.name, contact_info=contact_info, year=datetime.now().year, month=datetime.now().month, weekday=calendar.day_name[datetime.now().weekday()]))
        else:
            self.input_pending_subject.hide()
        template_message = self.input_template_message.toPlainText()
        self.input_pending_message.setPlainText(template_message.format(name=self.name, contact_info=contact_info, year=datetime.now().year, month=datetime.now().month, weekday=calendar.day_name[datetime.now().weekday()]))


    def nextRow(self):
        try:
            if not self.data:
                return
            self.current_row_index += 1
            self.btn_send_sms.setDisabled(False)
            self.updateRowDisplay()
        except (IndexError, AttributeError):
            pass

    def prevRow(self):
        try:
            if not self.data:
                return
            self.current_row_index -= 1
            self.updateRowDisplay()
        except (IndexError, AttributeError):
            pass

    def send(self):
        self.btn_send_sms.setDisabled(True)
        try:
            if self.current_type == 'ringcentral':
                token = None
                if self.input_ringcentral_token.text():
                    token = self.input_ringcentral_token.text()
                for number in [self.tophonenumber, self.fromphonenumber]:
                    if len(number) != 10:
                        raise Exception(f'Invalid Phone Number {number}')
                ringcentral_send_sms(self.tophonenumber, self.fromphonenumber, self.input_pending_message.toPlainText(), token=token)
            elif self.current_type == 'smtp':
                smtp_send_email(self.input_smtp_email.text(), self.input_smtp_password.text(), self.input_smtp_server_url.text(), self.input_smtp_server_port.text(), self.toemail, self.input_pending_subject.text(), self.input_pending_message.toPlainText())

        except Exception as e:
            print(e)
            msg = QMessageBox(self)
            msg.setWindowTitle("ERROR")
            msg.setText(f"Report the following to your aadministrator: {e}")
            msg.show()



