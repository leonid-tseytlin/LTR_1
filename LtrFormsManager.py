import sys
import PyQt5
from PyQt5.QtWidgets import QTextEdit, QPushButton, QGroupBox, QComboBox, QMessageBox
import logging
import LtrFront
import LtrCommon
import SuVocConnector
import LtrRulesManager

#=====================================================================================================
class FormsManager:
    horStep = 160
    vertStep = 80
    horMargin = 20
    vertMargin = 50
    horSize = 1060
    vertSize = 800

    def __init__(self, session, root_word, class_word):
        self.currentSession = session
        self.rootWord = root_word
        self.classWord = class_word
        self.formsTable = None
        self.new_mod_handler = None
        self.formsGroupBox = QGroupBox("Forms", self.currentSession.mainWindow)
        self.formsGroupBox.resize(self.horSize, self.vertSize)
        self.formsGroupBox.move(400, 30)
        self.formsGroupBox.formButtons = []
        self.formsGroupBox.show()

        self.currentHierarchyList = [LtrCommon.WORD_MODS]
        SuVocConnector.connector.get_mods_by_root(self.rootWord, [LtrCommon.WORD_MODS], self.set_form_mods)

    def set_form_mods(self, mods_list):
        for mod_name in mods_list:
            logging.debug('Adding button %s', mod_name)
            form_button = self.ModButton(self, mod_name, len(self.currentHierarchyList), mods_list.index(mod_name), False)
            self.formsGroupBox.formButtons.append(form_button)
        self.new_mod_handler = self.NewModHandler(self, mods_list, self.currentHierarchyList.copy())

    def set_word_forms(self, forms_list):
        logging.debug('Forms received %s', forms_list)
        self.create_new_word_form(forms_list, self.currentHierarchyList)

    def create_new_word_form(self, forms_list, hierarchy_list):
        self.formsTable = FormsTable(self, forms_list, hierarchy_list)

    # =====================================================================================================
    class NewModHandler:
        def __init__(self, manager_instance, mods_list, hierarchy_list):
            self.mod_selector = None
            self.hierarchyList = hierarchy_list
            self.manager_instance = manager_instance
            self.selector_vert_pos = len(mods_list) + 2
            self.button_vert_pos = 0
            self.handle_new_mod(mods_list)

        def handle_new_mod(self, mods_list):
            rules_mods = LtrRulesManager.rules_manager.get_word_mods(self.manager_instance.classWord, self.hierarchyList)
            logging.debug(mods_list)
            logging.debug(rules_mods)

            if rules_mods != mods_list:
                new_mods_list = list(set(rules_mods) - set(mods_list))
                logging.debug(new_mods_list)
                self.button_vert_pos = len(mods_list)
                self.mod_selector = self.manager_instance.NewModSelector(self.manager_instance, new_mods_list,
                                                                         len(self.hierarchyList) - 1, self.selector_vert_pos,
                                                                         self.create_new_mod)

        def create_new_mod(self, new_mod):
            logging.debug("New Mod: " + new_mod)
            logging.debug('currentHierarchyList %s', self.hierarchyList)
            hier_status = LtrRulesManager.rules_manager.get_hierarchy_status(self.manager_instance.classWord, self.hierarchyList)
            logging.debug(hier_status)
            self.mod_selector.setEnabled(False)
            self.manager_instance.ModButton(self.manager_instance, new_mod, len(self.hierarchyList), self.button_vert_pos, True)
            if hier_status == LtrRulesManager.HIER_FINAL:
                logging.debug("Create new form")
                self.manager_instance.create_new_word_form([], self.hierarchyList)
            else:
                self.hierarchyList.append(new_mod)
                logging.debug('currentHierarchyList %s', self.hierarchyList)
                hier_status = LtrRulesManager.rules_manager.get_hierarchy_status(self.manager_instance.classWord, self.hierarchyList)
                logging.debug(hier_status)
                if hier_status == LtrRulesManager.HIER_INTER:
                    self.handle_new_mod([])
                else:
                    logging.debug("Create new form")
                    self.manager_instance.create_new_word_form([], self.hierarchyList)

    # =====================================================================================================
    class NewModSelector(QComboBox):

        def __init__(self, manager_instance, mods_list, x_idx, y_idx, cb_fn):
            logging.debug(mods_list)
            super().__init__(manager_instance.formsGroupBox)
            self.selCb = cb_fn
            self.selection = None
            self.addItems(mods_list)
            hor_position = manager_instance.horMargin + x_idx * manager_instance.horStep
            vert_position = manager_instance.vertMargin + y_idx * manager_instance.vertStep
            self.move(hor_position, vert_position)
            self.textActivated.connect(self.update_label)
            self.show()

        def update_label(self):
            self.selection = self.currentText()
            logging.debug("Selected Item: " + self.selection)
            self.selCb(self.selection)

    # =====================================================================================================
    class ModButton(QPushButton):
        def __init__(self, manager_instance, title, depth, idx, disabled):
            super().__init__(title, manager_instance.formsGroupBox)
            self.title = title
            self.depth = depth
            self.manager_instance = manager_instance
            x_idx = depth - 1
            y_idx = idx
            self.move(manager_instance.horMargin + x_idx * manager_instance.horStep, manager_instance.vertMargin + y_idx * manager_instance.vertStep)
            if not disabled:
                self.clicked.connect(self.get_mods_button_click)
            else:
                self.setEnabled(False)
            self.show()

        def get_mods_button_click(self):
            logging.debug('hierarchy "%s"', self.manager_instance.currentHierarchyList)
            logging.debug('hierarchy length "%u"', len(self.manager_instance.currentHierarchyList))
            logging.debug('self.depth "%u"', self.depth)
            if len(self.manager_instance.currentHierarchyList) > self.depth:
                self.manager_instance.currentHierarchyList[self.depth] = self.title
                del self.manager_instance.currentHierarchyList[(self.depth+1):]
            else:
                self.manager_instance.currentHierarchyList.append(self.title)
            logging.debug('new_hierarchy "%s"', self.manager_instance.currentHierarchyList)

            hier_status = LtrRulesManager.rules_manager.get_hierarchy_status(self.manager_instance.classWord,
                                                                            self.manager_instance.currentHierarchyList)
            if hier_status == LtrRulesManager.HIER_FINAL:
                logging.debug('mods_hierarchy_list "%s"', self.manager_instance.currentHierarchyList)
                SuVocConnector.connector.get_forms_by_root(self.manager_instance.rootWord, self.manager_instance.currentHierarchyList,
                                                           self.manager_instance.set_word_forms)
            else:
                logging.debug('mods_hierarchy_list "%s"', self.manager_instance.currentHierarchyList)
                SuVocConnector.connector.get_mods_by_root(self.manager_instance.rootWord,
                                                          self.manager_instance.currentHierarchyList,
                                                          self.manager_instance.set_form_mods)

    # =====================================================================================================
    def self_destroy(self):
        if self.formsTable:
            self.formsTable.self_destroy()
        self.formsGroupBox.deleteLater()

    def __del__(self):
        logging.debug('FormsManager deleted')


# =====================================================================================================
class FormsTable:
    cell_width = 100
    cell_height = 30

    def __init__(self, manager_instance, forms_list, hierarchy_list):
        self.manager_instance = manager_instance
        self.save_button = None
        self.is_modified = False
        self.save_button_width = 120
        self.save_button_height = 40
        self.form_text = []
        self.dataGroupBox = QGroupBox("", self.manager_instance.formsGroupBox)

        logging.debug(hierarchy_list)
        self.hierarchyList = hierarchy_list
        word_mods_idx = hierarchy_list.index(LtrCommon.WORD_MODS)
        forms_names_list = hierarchy_list[:word_mods_idx] + [LtrCommon.FORM_NAMES] + hierarchy_list[word_mods_idx+1:]
        logging.debug(forms_names_list)
        forms_names_list = forms_names_list[:-1]
        logging.debug(forms_names_list)
        names_list = LtrRulesManager.rules_manager.get_form_names(self.manager_instance.classWord, forms_names_list)
        logging.debug(names_list)


        group_box_width = self.cell_width * 2
        self.dataGroupBox.resize(group_box_width, len(names_list) * self.cell_height)
        self.dataGroupBox.move(self.manager_instance.horSize - group_box_width - self.manager_instance.horMargin, self.manager_instance.vertMargin)
        self.dataGroupBox.show()

        for idx in range(len(names_list)):
            name = names_list[idx]
            if len(forms_list) > 0:
                form = forms_list[idx]
            else:
                form = None
            name_text_edit = QTextEdit(self.dataGroupBox)
            form_text_edit = QTextEdit(self.dataGroupBox)
            name_text_edit.setReadOnly(True)
            name_text_edit.setPlainText(name)
            form_text_edit.setPlainText(form)
            name_text_edit.resize(self.cell_width, self.cell_height)
            form_text_edit.resize(self.cell_width, self.cell_height)
            name_text_edit.move(0, idx * self.cell_height)
            form_text_edit.move(self.cell_width, idx * self.cell_height)
            form_text_edit.textChanged.connect(self.text_changed)
            name_text_edit.show()
            form_text_edit.show()
            self.form_text.append(form_text_edit)

    def text_changed(self):
        logging.debug("Text changed")
        if not self.is_modified:
            self.is_modified = True
            self.save_button = QPushButton("SAVE", self.manager_instance.formsGroupBox)
            self.save_button.resize(120, 40)
            self.save_button.move(self.manager_instance.horSize - self.save_button_width - self.manager_instance.horMargin,
                                  self.manager_instance.vertSize - self.save_button_height - self.manager_instance.vertMargin)
            self.save_button.show()
            self.save_button.clicked.connect(self.save_button_click)

    def save_button_click(self):
        logging.debug("Save button pushed")
        self.save_form()
        self.is_modified = False
        self.save_button.deleteLater()

    def save_form(self):
        form_list = self.manager_instance.formsTable.get_form_text()
        logging.debug(self.manager_instance.rootWord)
        logging.debug(self.hierarchyList)
        logging.debug(form_list)

        value = form_list
        for mod in reversed(self.hierarchyList):
            value = {mod: value}
        logging.debug(value)
        SuVocConnector.connector.set_new_form(self.manager_instance.rootWord, value)


    def get_form_text(self):
        form_text_list = []
        for form_text_edit in self.form_text:
            t_text = form_text_edit.toPlainText()
            if t_text == '':
                t_text = None
            form_text_list.append(t_text)
        return form_text_list

    def self_destroy(self):
        if self.is_modified:
            reply = QMessageBox.question(self.manager_instance.currentSession.mainWindow, 'Title', 'Word form was changed. Do you want to save it?')
            if reply == QMessageBox.Yes:
                logging.debug('User answered yes')
                self.save_form()
            if reply == QMessageBox.No:
                logging.debug('User answered no')
