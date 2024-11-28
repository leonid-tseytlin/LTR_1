from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox,
                             QRadioButton, QCheckBox, QTextEdit, QWidget, QComboBox, QLabel,
                             QVBoxLayout, QMenuBar, QToolBar, QAction)
import logging
import SuCommon
import SuVocConnector

class ConfigWindow(QWidget):
    def __init__(self, v_size, h_size):
        super().__init__()
        self.setWindowTitle("Configuration")
        QWidget.setWindowModality(self, QtCore.Qt.ApplicationModal)
        self.resize(v_size, h_size)
#        layout = QVBoxLayout()
#        self.label = QLabel("Configuration Window")
#        layout.addWidget(self.label)
#        self.setLayout(layout)

