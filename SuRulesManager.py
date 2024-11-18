import logging
import SuCommon
import SuVocConnector

HIER_FINAL = 10
HIER_INTER = 20
HIER_WRONG = 0

rules_manager = None;

class RulesManager:

    def __init__(self):
        logging.debug('Rules Manager created')
        self.rules = None
        SuVocConnector.connector.get_rules(self.set_rules)

    def set_rules(self, rules):
        self.rules = rules
        logging.debug('rules "%s"', self.rules)
        key_list = list(self.rules.keys())
        logging.debug(key_list)
        for word_class, word_mods in rules.items():
            logging.debug(word_class)
            logging.debug(word_mods)
            tmp_dict = word_mods

    def get_hierarchy_status(self, word_class, hier_list):
        word_mods_tmp = self.rules[word_class]
        for word_mod in hier_list:
            logging.debug(word_mod)
            if not word_mod in word_mods_tmp:
                return HIER_WRONG
            word_mods_tmp = word_mods_tmp[word_mod]
            logging.debug(word_mods_tmp)
            if not word_mods_tmp:
                return HIER_FINAL

        return HIER_INTER

    def get_word_mods(self, word_class, hierarchy):
        word_mods_tmp = self.rules[word_class]
        for word_mod in hierarchy:
            logging.debug(word_mod)
            word_mods_tmp = word_mods_tmp[word_mod]

        return list(word_mods_tmp)

    def get_form_names(self, word_class, form_list):
        form_names_tmp = self.rules[word_class]
        for form_name in form_list:
            logging.debug(form_name)
            form_names_tmp = form_names_tmp[form_name]

        return form_names_tmp

    def get_word_classes(self):
        return list(self.rules.keys())

def init_rules_manager():
    global rules_manager
    rules_manager = RulesManager()