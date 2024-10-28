import logging
import SuCommon
import SuVocConnector

class RulesManager:

    def __init__(self, connector):
        logging.debug('Rules Manager created')
        self.rules = None
        connector.get_rules(self.set_rules)

    def set_rules(self, rules):
        self.rules = rules
        logging.debug('rules "%s"', self.rules)
        for word_class, word_mods in rules.items():
            logging.debug(word_class)
            logging.debug(word_mods)
            tmp_dict = word_mods

    def get_max_depth(self, word_class):
        return 2 #Temporary!!!!