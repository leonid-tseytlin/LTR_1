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

    def on_button_click(self):
        logging.debug("Button clicked!")
        logging.debug("Text field value: %s", self.text_field.text())

        self.vocComm = VocCommunicator(self)


class VocCommunicator(QGraphicsObject):
    vocSignal = PyQt5.QtCore.pyqtSignal(list)

    def __init__(self, MainWindow):
        super().__init__()
        self.dataGroupBox = None
        self.mainWindow = MainWindow
        self.vocSignal.connect(self.get_roots_sig_handler)
        self.mainWindow.vocAgent.getRootsByStarting(self.mainWindow.text_field.text(), self.get_roots_callback)

    def get_roots_callback(self, roots):
        self.vocSignal.emit(roots)

    def get_roots_sig_handler(self, roots):
        logging.debug('Message "%s" received', roots)
        self.dataGroupBox = QGroupBox("", self.mainWindow)
        self.dataGroupBox.resize(400, 300)
        self.dataGroupBox.move(200, 100)
        self.dataGroupBox.show()

        self.dataGroupBox.textEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.textEdit.setPlainText(roots[0])
        self.dataGroupBox.textEdit.resize(200, 30)
        self.dataGroupBox.textEdit.move(30, 30)
        self.dataGroupBox.textEdit.show()

        self.dataGroupBox.button2 = QPushButton("Full Form", self.dataGroupBox)
        self.dataGroupBox.button2.move(30, 60)
        self.dataGroupBox.button2.show()




def SuFrontMainFunc(inp_q, outp_q):

    voc_agent = SuVocFrontAgent.SuVocFrontAgent(inp_q, outp_q)

    app = QApplication(sys.argv)
    window = SuMainWindow(voc_agent)
    window.show()
    sys.exit(app.exec_())