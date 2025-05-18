from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox,
                             QRadioButton, QCheckBox, QTextEdit, QWidget, QComboBox, QLabel,
                             QVBoxLayout, QMenuBar, QToolBar, QAction, QGridLayout)
import logging
import LtrCommon
import LtrVocConnector

class ConfigWindow(QWidget):
    def __init__(self, h_size, v_size):
        super().__init__()
        self.setWindowTitle("Configuration")
        QWidget.setWindowModality(self, QtCore.Qt.ApplicationModal)
        self.resize(h_size, v_size)

        layout = QGridLayout(self)
        self.top_label = QLabel("Configuration is not found. Please define the following parameters:")
        layout.addWidget(self.top_label, 0, 0, 7, 1, QtCore.Qt.AlignTop)

        self.rules_file_label = QLabel("Rules file location")
        layout.addWidget(self.rules_file_label, 1, 0, 1, 1)
        self.rules_file_edit = QLineEdit()
        layout.addWidget(self.rules_file_edit, 2, 0, 1, 1)

        self.words_file_label = QLabel("Words file location")
        layout.addWidget(self.words_file_label, 4, 0, 1, 1)
        self.words_file_edit = QLineEdit()
        layout.addWidget(self.words_file_edit, 5, 0, 1, 1)

        self.save_button = QPushButton("SAVE")
        layout.addWidget(self.save_button, 6, 0, 3, 1, QtCore.Qt.AlignRight)
        self.save_button.clicked.connect(self.save_button_click)

        self.setLayout(layout)

    def save_button_click(self):
        logging.debug("Save button pushed")
        rules_file_name = self.rules_file_edit.text()
        words_file_name = self.words_file_edit.text()
        logging.debug('rules_file "%s" words_file "%s"', rules_file_name, words_file_name)
        LtrVocConnector.connector.send_configuration({LtrCommon.RULES_FILE: rules_file_name, LtrCommon.WORDS_FILE: words_file_name})

        self.deleteLater()

