import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QGroupBox, QRadioButton, QCheckBox, QVBoxLayout, QGraphicsObject, QTextEdit
import threading
import logging
import SuCommon
import SuVocConnector
import SuRulesManager

rules_manager = None
connector = None

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
                connector.get_roots_by_starting(starting, self.session.add_root_managers)

    def closeEvent(self, event):
        logging.debug('closeEvent called')
        self.stop_event.set()
        connector.send_exit_app_to_voc()

    def __del__(self):
        logging.debug('Main Window deleted')

#=====================================================================================================
class VocComSession:
    def __init__(self, main_window):
        self.mainWindow = main_window
        self.rootManagers = []
        self.formsManager = None
        self.currentRootTransactionIdx = None
        self.currentHierarchyList = []

    def add_root_managers(self, roots_and_class):
        for root_and_class in roots_and_class:
            new_idx = len(self.rootManagers)
            self.rootManagers.append(RootManager(self, root_and_class[SuCommon.ROOT], root_and_class[SuCommon.WORD_CLASS], new_idx))

    def start_root_transaction(self, trans_idx):
        self.currentHierarchyList = []
        self.currentRootTransactionIdx = trans_idx

    def update_mod_hierarchy(self, mod_name):
        self.currentHierarchyList.append(mod_name)

    def get_mod_hierarchy(self):
        return self.currentHierarchyList

    def set_form_mods(self, mods_list):
        if not self.formsManager:
            logging.debug('Trying to create forms manager')
            self.formsManager = FormsManager(self,
                                             self.rootManagers[self.currentRootTransactionIdx].get_root_word(),
                                             self.rootManagers[self.currentRootTransactionIdx].get_class_word())
        for mod_name in mods_list:
            logging.debug('Adding button %s', mod_name)
            self.formsManager.create_form_button(mod_name, self.get_mod_depth(), mods_list.index(mod_name))

    def set_word_forms(self, forms_list):
        logging.debug('Forms received %s', forms_list)

    def get_mod_depth(self):
        return len(self.currentHierarchyList)

    def delete_form_mods(self):
        logging.debug('delete_form_mods')
        if self.formsManager:
            logging.debug('Trying to delete forms manager')
            self.formsManager.destroy_group_box()
        self.formsManager = None
        self.currentHierarchyList = []

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
        self.currentSession.start_root_transaction(self.index)
        connector.get_root_translation(self.rootWord, self.currentSession.set_root_translation)

    def get_mods_button_click(self):
        self.currentSession.delete_form_mods()
        self.currentSession.start_root_transaction(self.index)
        self.currentSession.update_mod_hierarchy(SuCommon.WORD_MODS)
        mods_hierarchy_list = self.currentSession.get_mod_hierarchy()
        connector.get_mods_by_root(self.rootWord, mods_hierarchy_list, self.currentSession.set_form_mods)

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
class FormsManager:
    horStep = 160
    vertStep = 100

    def __init__(self, session, root_word, class_word):
        self.session = session
        self.rootWord = root_word
        self.classWord = class_word
        self.formsGroupBox = QGroupBox("Forms", self.session.mainWindow)
        self.formsGroupBox.resize(1060, 800)
        self.formsGroupBox.move(400, 30)
        self.formsGroupBox.formButtons = []
        self.formsGroupBox.show()

    class ModButton(QPushButton):
        def __init__(self, manager_instance, title, x_idx, y_idx):
            super().__init__(title, manager_instance.formsGroupBox)
            self.title = title
            self.manager_instance = manager_instance
            self.move(20 + x_idx * manager_instance.horStep, 50 + y_idx * manager_instance.vertStep)
            self.clicked.connect(self.get_mods_button_click)
            self.show()

        def get_mods_button_click(self):
            mod_depth = self.manager_instance.session.get_mod_depth()
            logging.debug('mod_depth "%u"', mod_depth)
            if mod_depth < rules_manager.get_max_depth(self.manager_instance.classWord):
                self.manager_instance.session.update_mod_hierarchy(self.title)
                mods_hierarchy_list = self.manager_instance.session.get_mod_hierarchy()
                logging.debug('mods_hierarchy_list "%s"', mods_hierarchy_list)
                connector.get_mods_by_root(self.manager_instance.rootWord, mods_hierarchy_list, self.manager_instance.session.set_form_mods)
            else:
                mods_hierarchy_list = (self.manager_instance.session.get_mod_hierarchy()).copy()
                mods_hierarchy_list.append(self.title)
                logging.debug('mods_hierarchy_list "%s"', mods_hierarchy_list)
                connector.get_forms_by_root(self.manager_instance.rootWord, mods_hierarchy_list, self.manager_instance.session.set_word_forms)

    def create_form_button(self, title, x_idx, y_idx):
        form_button = self.ModButton(self, title, x_idx, y_idx)
        self.formsGroupBox.formButtons.append(form_button)

    def destroy_group_box(self):
        self.formsGroupBox.deleteLater()

    def __del__(self):
        logging.debug('FormsManager deleted')

#=====================================================================================================
def su_front_main_func(inp_q, outp_q):

    global connector
    connector = SuVocConnector.SuVocConnector(inp_q, outp_q)
    global rules_manager
    rules_manager = SuRulesManager.RulesManager(connector)

    app = QApplication(sys.argv)
    window = SuMainWindow()
    window.show()
    logging.debug('Before exit')
    sys.exit(app.exec_())
    logging.debug('After exit')
