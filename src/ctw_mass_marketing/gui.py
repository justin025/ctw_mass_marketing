import os
import sys
import threading
from PyQt6.QtCore import QTranslator
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from .qt.mainui import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = MainWindow()
    app.exec()
    os._exit(0)


if __name__ == '__main__':
    main()
