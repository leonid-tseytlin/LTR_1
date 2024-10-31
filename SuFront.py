import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox, QRadioButton, QCheckBox, QTextEdit
import threading
import logging
import SuCommon
import SuVocConnector
import SuRulesManager
import SuFormsManager

class SuMainWindow(QMainWindow):
    stop_event = threading.Event()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Su Application")
        self.resize(1500, 900)

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
            self.rootManagers.append(RootManager(self, root_and_class[SuCommon.ROOT], root_and_class[SuCommon.WORD_CLASS], new_idx))

    def create_form_mods(self, root_idx):
        self.delete_form_mods()
        logging.debug('Trying to create forms manager')
        self.formsManager = SuFormsManager.FormsManager(self,
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
        self.dataGroupBox = None
        self.rootWord = root_word
        self.classWord = class_word
        self.index = idx

        self.dataGroupBox = QGroupBox("", self.currentSession.mainWindow)
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
        self.dataGroupBox.classTextEdit.resize(60, 30)
        self.dataGroupBox.classTextEdit.show()
        self.dataGroupBox.transTextEdit.resize(130, 30)
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
def su_front_main_func(inp_q, outp_q):

    SuVocConnector.init_connector(inp_q, outp_q)
    SuRulesManager.init_rules_manager()

    app = QApplication(sys.argv)
    window = SuMainWindow()
    window.show()
    logging.debug('Before exit')
    sys.exit(app.exec_())
    logging.debug('After exit')
