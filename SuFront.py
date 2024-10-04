from multiprocessing import Process, Queue, Lock
import sys
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox, QRadioButton, QCheckBox, QVBoxLayout, QGraphicsObject, QTextEdit
import json
import threading
import tkinter as tk
import logging
import time
import SuParser
import SuVocFrontAgent

voc_agent = None
communicator = None

class SuMainWindow(QMainWindow):
    stop_event = threading.Event()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Su Application")
        self.resize(1400, 900)

        self.inp_text_field = QLineEdit(self)
        self.inp_text_field.move(20, 20)

        self.session = None

        self.read_input_thread = threading.Thread(target=self.read_input_thread_func, args=())
        self.read_input_thread.start()


    def read_input_thread_func(self):
        starting = ""
        while not self.stop_event.wait(1):
            logging.info('read_input_thread_func running')
            cur_text = self.inp_text_field.text()
            if cur_text:
                logging.info(cur_text)
            if starting != cur_text and cur_text != "":
                logging.info('Old "%s" New "%s"', starting, cur_text)
                starting = cur_text
                del self.session
                self.session = VocComSession(self)
                communicator.start_session(starting, self.session)

    def closeEvent(self, event):
        logging.debug('closeEvent called')
        self.stop_event.set()
        voc_agent.send_exit_app_to_voc()

    def __del__(self):
        logging.debug('Main Window deleted')

#=====================================================================================================
class VocComSession():
    def __init__(self, main_window):
        self.mainWindow = main_window
        self.rootManagers = []

    def add_root_managers(self, roots_and_class):
        for root_and_class in roots_and_class:
            new_idx = len(self.rootManagers)
            self.rootManagers.append(RootManager(self.mainWindow, root_and_class[SuParser.ROOT], root_and_class[SuParser.WORD_CLASS], new_idx))

    def set_root_translation(self, idx, trans_word):
        self.rootManagers[idx].set_translation(trans_word)

    def __del__(self):
        for root_manager in self.rootManagers:
            del root_manager
        self.rootManagers.clear()


#=====================================================================================================
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
        voc_agent.get_translation_by_root(root_word, self.get_translation_callback)

    def get_translation_callback(self, trans):
        self.transVocSignal.emit(trans)

    def get_translation_sig_handler(self, trans_word):
        logging.debug('Message "%s" received', trans_word)
        self.currentSession.set_root_translation(self.currentRootTransactionIdx, trans_word)

# ---------------------------------------------------------------------------
    def __del__(self):
        logging.debug('Communicator deleted')


#=====================================================================================================
class RootManager:
    def __init__(self, main_window, root_word, class_word, idx):
        logging.debug('root_word "%s" class_word "%s"', root_word, class_word)
        self.dataGroupBox = None
        self.mainWindow = main_window
        self.rootWord = root_word
        self.index = idx

        self.dataGroupBox = QGroupBox("", self.mainWindow)
        self.dataGroupBox.resize(320, 62)
        self.dataGroupBox.move(20, 100*(idx+1))
        self.dataGroupBox.show()

        self.dataGroupBox.rootTextEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.rootTextEdit.setReadOnly(True)
        self.dataGroupBox.rootTextEdit.setPlainText(root_word)
        self.dataGroupBox.rootTextEdit.resize(130, 30)
        self.dataGroupBox.rootTextEdit.move(0, 5)
        self.dataGroupBox.rootTextEdit.show()

        self.dataGroupBox.classTextEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.classTextEdit.setReadOnly(True)
        self.dataGroupBox.classTextEdit.setFontItalic(True)
        self.dataGroupBox.classTextEdit.setPlainText(class_word)
        self.dataGroupBox.classTextEdit.resize(190, 30)
        self.dataGroupBox.classTextEdit.move(130, 5)
        self.dataGroupBox.classTextEdit.show()

        self.dataGroupBox.translate_button = QPushButton("Translate", self.dataGroupBox)
        self.dataGroupBox.translate_button.move(0, 35)
        self.dataGroupBox.translate_button.show()
        self.dataGroupBox.translate_button.clicked.connect(self.translate_button_click)

        self.dataGroupBox.full_form_button = QPushButton("Get Form", self.dataGroupBox)
        self.dataGroupBox.full_form_button.move(240, 35)
        self.dataGroupBox.full_form_button.show()

        logging.debug('Root manager "%u" created', idx)

    def translate_button_click(self):
        communicator.get_root_translation(self.index, self.rootWord)

    def set_translation(self, trans_word):
        self.dataGroupBox.transTextEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.transTextEdit.setReadOnly(True)
        self.dataGroupBox.transTextEdit.setPlainText(trans_word)
        self.dataGroupBox.classTextEdit.resize(60, 30)
        self.dataGroupBox.classTextEdit.show()
        self.dataGroupBox.transTextEdit.resize(130, 30)
        self.dataGroupBox.transTextEdit.move(190, 5)
        self.dataGroupBox.transTextEdit.show()

    def __del__(self):
        self.dataGroupBox.deleteLater()
        logging.debug('RootManager deleted')


#=====================================================================================================
def su_front_main_func(inp_q, outp_q):

    global voc_agent
    voc_agent = SuVocFrontAgent.SuVocFrontAgent(inp_q, outp_q)
    global communicator
    communicator = VocCommunicator()

    app = QApplication(sys.argv)
    window = SuMainWindow()
    window.show()
    logging.debug('Before exit')
    sys.exit(app.exec_())
    logging.debug('After exit')
