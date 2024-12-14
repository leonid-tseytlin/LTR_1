import SuCommon
import logging

class SuWord():
    def __init__(self, data):
        self.__dict__.update(data)
#        logging.debug(self.word)
    """
        self.forms = {}
        self.root = data[SuCommon.ROOT]
        self.trans = data[SuCommon.TRANSLATION]
        #        key_list = list(data[SuCommon.WORD_MODS])
        self.forms[SuCommon.WORD_MODS] = data[SuCommon.WORD_MODS]
        #        for key in key_list:
        #            self.word_mods[key] = data["word_mods"][key]
        logging.debug(self.forms[SuCommon.WORD_MODS])
        self.wordClass = data[SuCommon.WORD_CLASS]
"""

    def getWordClass(self):
        return self.__dict__[SuCommon.WORD_CLASS]

    def get_root(self):
        return self.__dict__[SuCommon.ROOT]

    def get_word_forms(self, mods_list):
        logging.debug(mods_list)
        word_forms_tmp = self.__dict__
        for mod in mods_list:
#            logging.debug(mod)
#            logging.debug(word_forms_tmp)
            word_forms_tmp = word_forms_tmp[mod]
        logging.debug(word_forms_tmp)
        return word_forms_tmp

    def get_translation(self):
        return self.__dict__[SuCommon.TRANSLATION]

    def get_word_mods(self, mods_list):
        logging.debug(mods_list)
        word_mods_tmp = self.__dict__
        for mod in mods_list:
            logging.debug(mod)
            logging.debug(word_mods_tmp)
            word_mods_tmp = word_mods_tmp[mod]
        if not word_mods_tmp:
            return []
        key_list = list(word_mods_tmp.keys())
        logging.debug(key_list)
        return key_list

    def update_form(self, src_dict, dst_dict):
        if dst_dict is None:
            dst_dict = {}
        for key, value in src_dict.items():
            logging.debug('key: %s, value %s', key, value)
            if key not in dst_dict:
                logging.debug('adding key: %s', key)
                dst_dict.update({key: value})
                logging.debug(dst_dict)
            elif type(value) != dict:
                logging.debug('replacing value of key: %s', key)
                dst_dict[key] = src_dict[key]
                logging.debug(dst_dict)
            else:
                logging.debug('next level')
                dst_dict[key] = self.update_form(value, dst_dict[key])
                logging.debug(dst_dict)
        return dst_dict

    def set_word_form(self, new_form):
        logging.debug(new_form)
        logging.debug(self.__dict__[SuCommon.WORD_MODS])
        self.__dict__[SuCommon.WORD_MODS] = self.update_form(new_form[SuCommon.WORD_MODS], self.__dict__[SuCommon.WORD_MODS])
        logging.debug(self.__dict__[SuCommon.WORD_MODS])


        #######################################################################


