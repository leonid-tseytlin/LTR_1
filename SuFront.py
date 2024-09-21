from multiprocessing import Process, Queue, Lock
import sys
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox, QRadioButton, QCheckBox, QVBoxLayout, QGraphicsObject, QTextEdit
import json
import tkinter as tk
import logging
import SuParser
import SuVocFrontAgent


class SuMainWindow(QMainWindow):
    def __init__(self, voc_agent):
        super().__init__()
        self.vocComm = None
        self.setWindowTitle("Su Application")
        self.resize(1200, 900)

        self.text_field = QLineEdit(self)
        self.text_field.move(20, 20)

        self.button = QPushButton("Temp. get", self)
        self.button.move(20, 60)
        self.button.clicked.connect(self.on_button_click)

        self.vocAgent = voc_agent
        self.rootManagers = []

    def on_button_click(self):
        logging.debug("Button clicked!")
        logging.debug("Text field value: %s", self.text_field.text())

        self.vocComm = VocCommunicator(self)

    def add_root_manager(self, root_word):
        new_idx = len(self.rootManagers)
        self.rootManagers.append(RootManager(self, root_word, new_idx))

    def clear_root_managers(self):
        for root_manager in self.rootManagers:
            del root_manager
        self.rootManagers.clear()

class VocCommunicator(QGraphicsObject):
    vocSignal = PyQt5.QtCore.pyqtSignal(list)

    def __init__(self, main_window):
        super().__init__()
        self.mainWindow = main_window
        self.vocSignal.connect(self.get_roots_sig_handler)
        self.mainWindow.vocAgent.getRootsByStarting(self.mainWindow.text_field.text(), self.get_roots_callback)
        logging.debug('Communicator created')

    def get_roots_callback(self, roots):
        self.vocSignal.emit(roots)

    def get_roots_sig_handler(self, roots):
        logging.debug('Message "%s" received', roots)
        self.mainWindow.clear_root_managers()
        for root in roots:
            self.mainWindow.add_root_manager(root)

    def __del__(self):
        logging.debug('Communicator deleted')

class RootManager:
    def __init__(self, main_window, root_word, idx):
        self.dataGroupBox = None
        self.mainWindow = main_window

        self.dataGroupBox = QGroupBox("", self.mainWindow)
        self.dataGroupBox.resize(200, 62)
        self.dataGroupBox.move(20, 100*(idx+1))
        self.dataGroupBox.show()

        self.dataGroupBox.textEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.textEdit.setPlainText(root_word)
        self.dataGroupBox.textEdit.resize(200, 30)
        self.dataGroupBox.textEdit.move(0, 5)
        self.dataGroupBox.textEdit.show()

        self.dataGroupBox.full_form_button = QPushButton("Full Form", self.dataGroupBox)
        self.dataGroupBox.full_form_button.move(0, 35)
        self.dataGroupBox.full_form_button.show()

        logging.debug('Root manager "%u" created', idx)

    def __del__(self):
#        self.dataGroupBox.hide()
        self.dataGroupBox.deleteLater()
        logging.debug('RootManager deleted')


def su_front_main_func(inp_q, outp_q):

    voc_agent = SuVocFrontAgent.SuVocFrontAgent(inp_q, outp_q)

    app = QApplication(sys.argv)
    window = SuMainWindow(voc_agent)
    window.show()
    sys.exit(app.exec_())