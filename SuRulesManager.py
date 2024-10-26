import logging
import SuCommon
import SuVocConnector

class RulesManager:

    def __init__(self, connector):
        logging.debug('Rules Manager created')

    def get_max_depth(self, word_class):
        return 2 #Temporary!!!!