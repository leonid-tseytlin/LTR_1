import sys
import PyQt5
from PyQt5.QtWidgets import QTextEdit, QPushButton, QGroupBox, QComboBox
import logging
import SuFront
import SuCommon
import SuVocConnector
import SuRulesManager

#=====================================================================================================
class FormsManager:
    horStep = 160
    vertStep = 80
    horMargin = 20
    vertMargin = 50

    def __init__(self, session, root_word, class_word):
        self.currentSession = session
        self.rootWord = root_word
        self.classWord = class_word
        self.formsTable = None
        self.mod_selector = None
        self.formsGroupBox = QGroupBox("Forms", self.currentSession.mainWindow)
        self.formsGroupBox.resize(1060, 800)
        self.formsGroupBox.move(400, 30)
        self.formsGroupBox.formButtons = []
        self.formsGroupBox.show()

        self.currentHierarchyList = [SuCommon.WORD_MODS]
        SuVocConnector.connector.get_mods_by_root(self.rootWord, [SuCommon.WORD_MODS], self.set_form_mods)

    def set_form_mods(self, mods_list):
        for mod_name in mods_list:
            logging.debug('Adding button %s', mod_name)
            self.create_form_button(mod_name, len(self.currentHierarchyList) - 1, mods_list.index(mod_name))

        rules_mods = SuRulesManager.rules_manager.get_word_mods(self.classWord, self.currentHierarchyList)
        logging.debug('currentHierarchyList %s', self.currentHierarchyList)
        logging.debug(mods_list)
        logging.debug(rules_mods)

        if rules_mods != mods_list:
            new_mods_list = list(set(rules_mods) - set(mods_list))
            logging.debug(new_mods_list)
            self.mod_selector = self.NewModSelector(self, new_mods_list, len(self.currentHierarchyList) - 1, len(rules_mods), self.create_new_mod)

    def create_new_mod(self, mod):
        logging.debug("New Mod: " + mod)


    def set_word_forms(self, forms_list):
        logging.debug('Forms received %s', forms_list)
        logging.debug(self.currentHierarchyList)
        word_mods_idx = self.currentHierarchyList.index(SuCommon.WORD_MODS)
        forms_names_list = self.currentHierarchyList[:word_mods_idx] + [SuCommon.FORM_NAMES] + self.currentHierarchyList[word_mods_idx+1:]
        logging.debug(forms_names_list)
        names_list = SuRulesManager.rules_manager.get_form_names(self.classWord, forms_names_list)
        logging.debug(names_list)
        self.formsTable = self.FormsTable(self,names_list, forms_list)

    def create_form_button(self, title, x_idx, y_idx):
        form_button = self.ModButton(self, title, x_idx, y_idx)
        self.formsGroupBox.formButtons.append(form_button)

    # =====================================================================================================
    class NewModSelector:

        def __init__(self, manager_instance, mods_list, x_idx, y_idx, cb_fn):
            logging.debug(mods_list)
            self.selCb = cb_fn
            self.sel_combo_box = None
            self.selection = None
            self.sel_combo_box = QComboBox(manager_instance.formsGroupBox)
            self.sel_combo_box.addItems(mods_list)
            hor_position = manager_instance.horMargin + x_idx * manager_instance.horStep
            vert_position = manager_instance.vertMargin + y_idx * manager_instance.vertStep
            self.sel_combo_box.move(hor_position, vert_position)
            self.sel_combo_box.textActivated.connect(self.update_label)
            self.sel_combo_box.show()

        def update_label(self):
            self.selection = self.sel_combo_box.currentText()
            logging.debug("Selected Item: " + self.selection)
            self.selCb(self.selection)

    # =====================================================================================================
    class ModButton(QPushButton):
        def __init__(self, manager_instance, title, x_idx, y_idx):
            super().__init__(title, manager_instance.formsGroupBox)
            self.title = title
            self.manager_instance = manager_instance
            self.move(manager_instance.horMargin + x_idx * manager_instance.horStep, manager_instance.vertMargin + y_idx * manager_instance.vertStep)
            self.clicked.connect(self.get_mods_button_click)
            self.show()

        def get_mods_button_click(self):
            mod_depth = len(self.manager_instance.currentHierarchyList)
            logging.debug('mod_depth "%u"', mod_depth)
            hierarchy_list = self.manager_instance.currentHierarchyList.copy()
            hierarchy_list.append(self.title)
            logging.debug(hierarchy_list)
            hier_status = SuRulesManager.rules_manager.get_hierarchy_status(self.manager_instance.classWord, hierarchy_list)
            logging.debug(hier_status)

            if hier_status == SuRulesManager.HIER_INTER:
                self.manager_instance.currentHierarchyList.append(self.title)
                logging.debug('mods_hierarchy_list "%s"', hierarchy_list)
                SuVocConnector.connector.get_mods_by_root(self.manager_instance.rootWord, hierarchy_list, self.manager_instance.set_form_mods)
            elif hier_status == SuRulesManager.HIER_FINAL:
                logging.debug('mods_hierarchy_list "%s"', hierarchy_list)
                SuVocConnector.connector.get_forms_by_root(self.manager_instance.rootWord, hierarchy_list, self.manager_instance.set_word_forms)
            else:
                logging.error('wrong mods_hierarchy_list "%s"', hierarchy_list)

    # =====================================================================================================
    class FormsTable:
        cell_width = 100
        cell_height = 30

        def __init__(self, manager_instance, form_names_list, word_forms_list):
            self.manager_instance = manager_instance
            self.dataGroupBox = QGroupBox("", self.manager_instance.formsGroupBox)

            self.dataGroupBox.resize(self.cell_width * 2, len(form_names_list) * self.cell_height)
            self.dataGroupBox.move(self.manager_instance.horStep * len(self.manager_instance.currentHierarchyList), 50)
            self.dataGroupBox.show()

            for idx in range(len(form_names_list)):
                name = form_names_list[idx]
                form = word_forms_list[idx]
                name_text_edit = QTextEdit(self.dataGroupBox)
                form_text_edit = QTextEdit(self.dataGroupBox)
                name_text_edit.setReadOnly(True)
                name_text_edit.setPlainText(name)
                form_text_edit.setPlainText(form)
                name_text_edit.resize(self.cell_width, self.cell_height)
                form_text_edit.resize(self.cell_width, self.cell_height)
                name_text_edit.move(0, idx * self.cell_height)
                form_text_edit.move(self.cell_width, idx * self.cell_height)
                name_text_edit.show()
                form_text_edit.show()

    # =====================================================================================================
    def self_destroy(self):
        self.formsGroupBox.deleteLater()

    def __del__(self):
        logging.debug('FormsManager deleted')
