import sys
import PyQt5
from PyQt5.QtWidgets import QTextEdit, QPushButton, QGroupBox
import logging
import SuFront
import SuCommon
import SuVocConnector
import SuRulesManager

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
            hierarchy_list = (self.manager_instance.session.get_mod_hierarchy()).copy()
            hierarchy_list.append(self.title)
            logging.debug(hierarchy_list)
            hier_status = SuRulesManager.rules_manager.get_hierarchy_status(self.manager_instance.classWord, hierarchy_list)
            logging.debug(hier_status)

            if hier_status == SuRulesManager.HIER_INTER:
                self.manager_instance.session.update_mod_hierarchy(self.title)
                logging.debug('mods_hierarchy_list "%s"', hierarchy_list)
                SuVocConnector.connector.get_mods_by_root(self.manager_instance.rootWord, hierarchy_list, self.manager_instance.session.set_form_mods)
            elif hier_status == SuRulesManager.HIER_FINAL:
                logging.debug('mods_hierarchy_list "%s"', hierarchy_list)
                SuVocConnector.connector.get_forms_by_root(self.manager_instance.rootWord, hierarchy_list, self.manager_instance.session.set_word_forms)

                rootTextEdit = QTextEdit(self.manager_instance.formsGroupBox)
                rootTextEdit.setReadOnly(True)
                rootTextEdit.setPlainText("test")
                rootTextEdit.resize(130, 30)
                rootTextEdit.move(600, 50)
                rootTextEdit.show()

            else:
                logging.error('wrong mods_hierarchy_list "%s"', hierarchy_list)

    def create_form_button(self, title, x_idx, y_idx):
        form_button = self.ModButton(self, title, x_idx, y_idx)
        self.formsGroupBox.formButtons.append(form_button)

    def destroy_group_box(self):
        self.formsGroupBox.deleteLater()

    def __del__(self):
        logging.debug('FormsManager deleted')

