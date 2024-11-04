import SuCommon
import logging

class SuWord():
    def __init__(self, word_class):
        self.root = None
        self.wordClass = word_class
        self.forms = {}

    def getWordClass(self):
        return self.wordClass

    def get_root(self):
        return self.root

#######################################################################
class SuNoun(SuWord):

    def __init__(self, data):
        self.root = "Not implemented"
        self.conj = "Not implemented"

    def getConj(self, key):
        return "Noun still not implemented"

#######################################################################
class SuVerb(SuWord):

    def __init__(self, word_class, data):
        super().__init__(word_class)
        self.root = data[SuCommon.ROOT]
        self.trans = data[SuCommon.TRANSLATION]
#        key_list = list(data[SuCommon.WORD_MODS])
        self.forms[SuCommon.WORD_MODS] = data[SuCommon.WORD_MODS]
#        for key in key_list:
#            self.word_mods[key] = data["word_mods"][key]
        logging.debug(self.forms[SuCommon.WORD_MODS])

    def get_word_forms(self, mods_list):
        logging.debug(mods_list)
        word_forms_tmp = self.forms
        for mod in mods_list:
#            logging.debug(mod)
#            logging.debug(word_forms_tmp)
            word_forms_tmp = word_forms_tmp[mod]
        logging.debug(word_forms_tmp)
        return word_forms_tmp

    def get_translation(self):
        return self.trans

    def get_word_mods(self, mods_list):
        logging.debug(mods_list)
        word_mods_tmp = self.forms
        for mod in mods_list:
            logging.debug(mod)
            logging.debug(word_mods_tmp)
            word_mods_tmp = word_mods_tmp[mod]
        if not word_mods_tmp:
            return []
        key_list = list(word_mods_tmp.keys())
        logging.debug(key_list)
        return key_list

#######################################################################


