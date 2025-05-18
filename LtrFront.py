import sys
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox,
                             QRadioButton, QCheckBox, QTextEdit, QWidget, QComboBox, QLabel,
                             QVBoxLayout, QMenuBar, QToolBar, QAction)
from random import randint
import threading
import logging
import LtrCommon
import SuVocConnector
import SuRulesManager
import LtrFormsManager
import LtrConfig

class SuMainWindow(QtWidgets.QMainWindow):
    stop_event = threading.Event()

    horMargin = 20
    horSize = 1500
    vertSize = 900
    rootVertStep = 100
    rootWidth = 320
    textEditHeight = 30

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LTR Application")
        self.resize(self.horSize, self.vertSize)

        self.session = None
        self.new_button = None
        self.new_word = None
        self.config_window = None
        self.inp_text_field = None
        self.read_input_thread = None

        SuVocConnector.connector.wait_for_voc_ready(self.voc_ready_handler)

    def voc_ready_handler(self, data):
        if data == LtrCommon.SUCCESS:
            self.voc_ready_to_work()
        else:
            if self.config_window is None:
                self.config_window = LtrConfig.ConfigWindow(self.horSize // 2, self.vertSize // 2)
            self.config_window.show()

    def voc_ready_to_work(self):
        SuRulesManager.init_rules_manager()

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)
        button_action = QAction("Configuration", self)
        button_action.setStatusTip("Configuration settings")
        button_action.triggered.connect(self.toolbar_config_button_click)
        toolbar.addAction(button_action)

        self.inp_text_field = QLineEdit(self)
        self.inp_text_field.move(self.horMargin, 40)
        self.inp_text_field.show()

        self.create_new_button()
        self.read_input_thread = threading.Thread(target=self.read_input_thread_func, args=())
        self.read_input_thread.start()

    def toolbar_config_button_click(self, s):
        if self.config_window is None:
            self.config_window = LtrConfig.ConfigWindow(self.horSize//2, self.vertSize//2)
        self.config_window.show()

    def create_new_button(self):
        if not self.session:
            vert_pos = 0
        else:
            vert_pos = len(self.session.rootManagers)

        self.new_button = QPushButton("NEW", self)
        self.new_button.move(self.horMargin, self.rootVertStep * (vert_pos + 1))
        self.new_button.show()
        self.new_button.clicked.connect(self.new_button_click)

    def new_button_click(self):
        if not self.session:
            vert_pos = 0
        else:
            vert_pos = len(self.session.rootManagers)
        self.new_button.hide()
        self.new_word = NewWord(self, vert_pos)

    def read_input_thread_func(self):
        starting = ""
        while not self.stop_event.wait(1):
            logging.debug('read_input_thread_func running')
            cur_text = self.inp_text_field.text()
            if cur_text:
                logging.debug(cur_text)
            if starting != cur_text and cur_text != "":
                logging.debug('Old "%s" New "%s"', starting, cur_text)
                starting = cur_text
                if self.new_word:
                    self.new_word.self_destroy()
                    self.new_word = None
                if self.session:
                    self.session.delete_form_mods()
                    self.session.delete_root_managers()
                    del self.session
                self.session = VocComSession(self)
                SuVocConnector.connector.get_roots_by_starting(starting, self.session.add_root_managers)

    def closeEvent(self, event):
        logging.debug('closeEvent called')
        self.stop_event.set()
        SuVocConnector.connector.send_exit_app_to_voc()

    def __del__(self):
        logging.debug('Main Window deleted')

#=====================================================================================================
class VocComSession:
    def __init__(self, main_window):
        self.mainWindow = main_window
        self.rootManagers = []
        self.formsManager = None
        self.currentRootTransactionIdx = None

    def add_root_managers(self, roots_and_class):
        for root_and_class in roots_and_class:
            new_idx = len(self.rootManagers)
            self.rootManagers.append(RootManager(self, root_and_class[LtrCommon.ROOT], root_and_class[LtrCommon.WORD_CLASS], new_idx))
        self.mainWindow.new_button.deleteLater()
        self.mainWindow.create_new_button()

    def create_form_mods(self, root_idx):
        self.delete_form_mods()
        logging.debug('Trying to create forms manager')
        self.formsManager = LtrFormsManager.FormsManager(self,
                                                        self.rootManagers[root_idx].get_root_word(),
                                                        self.rootManagers[root_idx].get_class_word())

    def delete_form_mods(self):
        logging.debug('delete_form_mods')
        if self.formsManager:
            logging.debug('Trying to delete forms manager')
            self.formsManager.self_destroy()
        self.formsManager = None

    def set_root_translation(self, trans_word):
        self.rootManagers[self.currentRootTransactionIdx].set_translation(trans_word)

    def delete_root_managers(self):
        logging.debug('Trying to delete root managers')
        for root_manager in self.rootManagers:
            root_manager.destroy_group_box()
        self.rootManagers.clear()

    def __del__(self):
        logging.debug('Session deleted')


#=====================================================================================================
class RootManager:
    def __init__(self, session, root_word, class_word, idx):
        logging.debug('root_word "%s" class_word "%s"', root_word, class_word)
        self.currentSession = session
        self.horMargin__ = session.mainWindow.horMargin
        self.textEditHeight = session.mainWindow.textEditHeight
        self.dataGroupBox = None
        self.rootWord = root_word
        self.classWord = class_word
        self.index = idx

        self.dataGroupBox = QGroupBox("", self.currentSession.mainWindow)
        self.dataGroupBox.resize(session.mainWindow.rootWidth, 62)
        self.dataGroupBox.move(self.horMargin__, session.mainWindow.rootVertStep * (idx+1))
        self.dataGroupBox.show()

        self.dataGroupBox.rootTextEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.rootTextEdit.setReadOnly(True)
        self.dataGroupBox.rootTextEdit.setPlainText(root_word)
        self.dataGroupBox.rootTextEdit.resize(130, self.textEditHeight)
        self.dataGroupBox.rootTextEdit.move(0, 5)
        self.dataGroupBox.rootTextEdit.show()

        self.dataGroupBox.classTextEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.classTextEdit.setReadOnly(True)
        self.dataGroupBox.classTextEdit.setFontItalic(True)
        self.dataGroupBox.classTextEdit.setPlainText(class_word)
        self.dataGroupBox.classTextEdit.resize(190, self.textEditHeight)
        self.dataGroupBox.classTextEdit.move(130, 5)
        self.dataGroupBox.classTextEdit.show()

        self.dataGroupBox.translate_button = QPushButton("Translate", self.dataGroupBox)
        self.dataGroupBox.translate_button.move(0, 35)
        self.dataGroupBox.translate_button.show()
        self.dataGroupBox.translate_button.clicked.connect(self.translate_button_click)

        self.dataGroupBox.get_mods_button = QPushButton("Get Mods", self.dataGroupBox)
        self.dataGroupBox.get_mods_button.move(240, 35)
        self.dataGroupBox.get_mods_button.show()
        self.dataGroupBox.get_mods_button.clicked.connect(self.get_mods_button_click)

        logging.debug('Root manager "%u" created', idx)

    def translate_button_click(self):
        self.currentSession.currentRootTransactionIdx = self.index
        logging.debug('currentRootTransactionIdx "%u" set', self.currentSession.currentRootTransactionIdx)
        SuVocConnector.connector.get_root_translation(self.rootWord, self.currentSession.set_root_translation)

    def get_mods_button_click(self):
        self.currentSession.create_form_mods(self.index)

    def set_translation(self, trans_word):
        self.dataGroupBox.transTextEdit = QTextEdit(self.dataGroupBox)
        self.dataGroupBox.transTextEdit.setReadOnly(True)
        self.dataGroupBox.transTextEdit.setPlainText(trans_word)
        self.dataGroupBox.classTextEdit.resize(60, self.textEditHeight)
        self.dataGroupBox.classTextEdit.show()
        self.dataGroupBox.transTextEdit.resize(130, self.textEditHeight)
        self.dataGroupBox.transTextEdit.move(190, 5)
        self.dataGroupBox.transTextEdit.show()

    def get_root_word(self):
        return self.rootWord

    def get_class_word(self):
        return self.classWord

    def destroy_group_box(self):
        self.dataGroupBox.deleteLater()

    def __del__(self):
        logging.debug('RootManager deleted')

#=====================================================================================================
class NewWord:
    def __init__(self, main_window, vert_pos):
        self.mainWindow = main_window
        self.dataGroupBox = QGroupBox("", main_window)
        self.dataGroupBox.resize(main_window.rootWidth, main_window.textEditHeight * 4)
        self.dataGroupBox.move(main_window.horMargin, main_window.rootVertStep * (vert_pos + 1))
        self.dataGroupBox.show()

        self.rootTextEdit = QTextEdit(self.dataGroupBox)
        self.rootTextEdit.setPlaceholderText("root")
        self.rootTextEdit.resize(main_window.rootWidth, main_window.textEditHeight)
        self.rootTextEdit.move(0, 0)
        self.rootTextEdit.show()

        self.transTextEdit = QTextEdit(self.dataGroupBox)
        self.transTextEdit.setPlaceholderText("translation")
        self.transTextEdit.resize(main_window.rootWidth, main_window.textEditHeight)
        self.transTextEdit.move(0, main_window.textEditHeight)
        self.transTextEdit.show()

        self.classBox = QComboBox(self.dataGroupBox)
        self.classBox.addItems(SuRulesManager.rules_manager.get_word_classes())

        self.classBox.resize(main_window.rootWidth, main_window.textEditHeight)
        self.classBox.move(0, main_window.textEditHeight * 2)
        self.classBox.show()

        self.save_button = QPushButton("Save", self.dataGroupBox)
        self.save_button.move(0, main_window.textEditHeight * 3)
        self.save_button.show()
        self.save_button.clicked.connect(self.save_button_click)

    def save_button_click(self):
        root_word = self.rootTextEdit.toPlainText()
        SuVocConnector.connector.set_new_word(root_word, self.classBox.currentText(), self.transTextEdit.toPlainText())
        self.dataGroupBox.deleteLater()
        self.mainWindow.new_word = None
        self.mainWindow.session = VocComSession(self.mainWindow)
        SuVocConnector.connector.get_roots_by_starting(root_word, self.mainWindow.session.add_root_managers)

    def self_destroy(self):
        self.dataGroupBox.deleteLater()


#=====================================================================================================
def su_front_main_func(inp_q, outp_q):

    SuVocConnector.init_connector(inp_q, outp_q)

    app = QApplication(sys.argv)
    window = SuMainWindow()
    window.show()

    logging.debug('Before exit')
    sys.exit(app.exec_())
    logging.debug('After exit')
