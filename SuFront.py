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

voc_agent = None
communicator = None

class SuMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Su Application")
        self.resize(1200, 900)

        self.text_field = QLineEdit(self)
        self.text_field.move(20, 20)

        self.button = QPushButton("Temp. get", self)
        self.button.move(20, 60)
        self.button.clicked.connect(self.on_button_click)

        self.session = None

    def on_button_click(self):
        logging.debug("Button clicked!")
        logging.debug("Text field value: %s", self.text_field.text())

        del self.session
        self.session = VocComSession(self)
        communicator.start_session(self.text_field.text(), self.session)


class VocComSession():
    def __init__(self, main_window):
        self.mainWindow = main_window
        self.rootManagers = []

    def add_root_managers(self, roots):
        for root in roots:
            new_idx = len(self.rootManagers)
            self.rootManagers.append(RootManager(self.mainWindow, root, new_idx))

    def set_root_translation(self, idx, trans_word):
        self.rootManagers[idx].set_translation(trans_word)

    def __del__(self):
        for root_manager in self.rootManagers:
            del root_manager
        self.rootManagers.clear()


class VocCommunicator(QGraphicsObject):
    rootsVocSignal = PyQt5.QtCore.pyqtSignal(list)
    transVocSignal = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.rootsVocSignal.connect(self.get_roots_sig_handler)
        self.transVocSignal.connect(self.get_translation_sig_handler)
        self.currentSession = None
        self.currentRootTransactionIdx = None
        logging.debug('Communicator created')

    def start_session(self, starting, session):
        self.currentSession = session
        voc_agent.get_roots_by_starting(starting, self.get_roots_callback)

    def get_roots_callback(self, roots):
        self.rootsVocSignal.emit(roots)

    def get_roots_sig_handler(self, roots):
        logging.debug('Message "%s" received', roots)
        self.currentSession.add_root_managers(roots)

#---------------------------------------------------------------------------
    def get_root_translation(self, root_idx, root_word):
        self.currentRootTransactionIdx = root_idx
        voc_agent.get_root_translation(root_word, self.get_translation_callback)

    def get_translation_callback(self, trans):
        self.transVocSignal.emit(trans)

    def get_translation_sig_handler(self, trans_word):
        logging.debug('Message "%s" received', trans_word)
        self.currentSession.set_root_translation(self.currentRootTransactionIdx, trans_word)

# ---------------------------------------------------------------------------
    def __del__(self):
        logging.debug('Communicator deleted')


class RootManager:
    def __init__(self, main_window, root_word, idx):
        self.dataGroupBox = None
        self.mainWindow = main_window
        self.rootWord = root_word
        self.index = idx

        self.dataGroupBox = QGroupBox("", self.mainWindow)
        self.dataGroupBox.resize(200, 62)
        self.dataGroupBox.move(20, 100*(idx+1))
        self.dataGroupBox.show()

        self.dataGroupBox.textEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.textEdit.setReadOnly(True)
        self.dataGroupBox.textEdit.setPlainText(root_word)
        self.dataGroupBox.textEdit.resize(200, 30)
        self.dataGroupBox.textEdit.move(0, 5)
        self.dataGroupBox.textEdit.show()

        self.dataGroupBox.translate_button = QPushButton("Translate", self.dataGroupBox)
        self.dataGroupBox.translate_button.move(0, 35)
        self.dataGroupBox.translate_button.show()
        self.dataGroupBox.translate_button.clicked.connect(self.translate_button_click)

        self.dataGroupBox.full_form_button = QPushButton("Full Form", self.dataGroupBox)
        self.dataGroupBox.full_form_button.move(80, 35)
        self.dataGroupBox.full_form_button.show()

        logging.debug('Root manager "%u" created', idx)

    def translate_button_click(self):
        communicator.get_root_translation(self.index, self.rootWord)

    def set_translation(self, trans_word):
        self.dataGroupBox.textEdit.setPlainText(self.rootWord + "  " + trans_word)

    def __del__(self):
        self.dataGroupBox.deleteLater()
        logging.debug('RootManager deleted')


def su_front_main_func(inp_q, outp_q):

    global voc_agent
    voc_agent = SuVocFrontAgent.SuVocFrontAgent(inp_q, outp_q)
    global communicator
    communicator = VocCommunicator()

    app = QApplication(sys.argv)
    window = SuMainWindow()
    window.show()
    sys.exit(app.exec_())