import os.path
import yaml
import SuWord
import SuCommon
import SuParser
import json
import logging

config_file_name = "./ltr_config.yaml"


class SuVocabulary():

    def read_config(self):
        if not os.path.exists(config_file_name):
            logging.error("Configuration file does not exist")
            return None
        try:
            with open(config_file_name, 'r') as f:
                logging.info(f'Open {config_file_name}')
                config_data = yaml.safe_load(f)
                logging.debug(config_data)
                return config_data
        except:
            logging.error("Not yaml file")
            return None

    def read_voc_data(self, config_data):
        logging.debug(config_data)
        if not os.path.exists(config_data[SuCommon.WORDS_FILE]):
            logging.error("File %s does not exist", config_data[SuCommon.WORDS_FILE])
            return None
        if not os.path.exists(config_data[SuCommon.RULES_FILE]):
            logging.error("File %s does not exist", config_data[SuCommon.RULES_FILE])
            return None
        file_names = [config_data[SuCommon.WORDS_FILE], config_data[SuCommon.RULES_FILE]]
        try:
            with open(config_data[SuCommon.WORDS_FILE], 'r') as words_file:
                logging.info(f'Open {config_data[SuCommon.WORDS_FILE]}')
                words_data = yaml.safe_load(words_file)
        except:
            logging.error("Not yaml file")
            return None
        try:
            with open(config_data[SuCommon.RULES_FILE], 'r') as rules_file:
                logging.info(f'Open {config_data[SuCommon.RULES_FILE]}')
                rules_data = yaml.safe_load(rules_file)
        except:
            logging.error("Not yaml file")
            return None

        return words_data, rules_data

    def build_words(self, data):
        for word in data[SuCommon.WORDS]:
            self.words.append(SuWord.SuWord(word))
            self.roots.append(word[SuCommon.ROOT])

        logging.debug(self.roots)

    def build_rules(self, data):
        logging.debug(data)
        for rule in data[SuCommon.RULES]:
            self.rules[rule[SuCommon.WORD_CLASS]] = rule
        logging.debug(self.rules)

    def validate_config_data(self, config_data):
        return True

#---------------------------------------------------------------------------------------
#   MESSAGE HANDLERS

    def handle_config_response(self, config_data):
        logging.debug(config_data)
        if not self.validate_config_data(config_data):
            return SuCommon.CONFIG_REQ
        else:
            words_data, rules_data = self.read_voc_data(config_data)
            if words_data is not None:
                self.build_words(words_data)
                self.build_rules(rules_data)
            return None

    def handle_get_roots(self, data):
        logging.debug(data)
        roots_list = list(filter(lambda x: x.startswith(data), self.roots))
        logging.debug('roots list: %s', roots_list)
        roots_and_class_list = []
        for root in roots_list:
            idx = self.roots.index(root)
            word_class = self.words[idx].getWordClass()
            roots_and_class_list.append({SuCommon.ROOT: root, SuCommon.WORD_CLASS: word_class})
        logging.debug(roots_and_class_list)
        return roots_and_class_list

    def handle_translate(self, data):
        logging.info(data)
        idx = self.roots.index(data[SuCommon.ROOT])
        trans = self.words[idx].get_translation()
        return trans

    def handle_get_forms(self, data):
        logging.info(data)
        idx = self.roots.index(data[SuCommon.ROOT])
        forms = self.words[idx].get_word_forms(data[SuCommon.MODS_LIST])
        return forms

    def handle_get_mods(self, data):
        logging.info(data)
        idx = self.roots.index(data[SuCommon.ROOT])
        mods = self.words[idx].get_word_mods(data[SuCommon.MODS_LIST])
        logging.debug(mods)
        return mods

    def handle_get_rules(self, data):
        return self.rules

    def handle_save_form(self, data):
        logging.debug(data)
        idx = self.roots.index(data[SuCommon.ROOT])
        self.words[idx].set_word_form(data[SuCommon.NEW_FORM])
        return None

    def handle_new_word(self, data):
        logging.debug(data)
        word_data = {SuCommon.ROOT: data[SuCommon.ROOT], SuCommon.WORD_CLASS: data[SuCommon.WORD_CLASS], SuCommon.TRANSLATION: data[SuCommon.TRANSLATION],
                     SuCommon.WORD_MODS: None}
        logging.debug(word_data)

        self.words.append(SuWord.SuWord(word_data))
        self.roots.append(data[SuCommon.ROOT])

# ---------------------------------------------------------------------------------------
    def __init__(self):

        self.handler_fn = {
            SuCommon.GET_ROOTS: self.handle_get_roots,
            SuCommon.TRANSLATE: self.handle_translate,
            SuCommon.GET_MODS: self.handle_get_mods,
            SuCommon.GET_FORMS: self.handle_get_forms,
            SuCommon.GET_RULES: self.handle_get_rules,
            SuCommon.SAVE_FORM: self.handle_save_form,
            SuCommon.NEW_WORD: self.handle_new_word,
            SuCommon.CONFIG_RESP: self.handle_config_response
        }
        self.res_code = {
            SuCommon.GET_ROOTS: SuCommon.ROOTS_LIST,
            SuCommon.TRANSLATE: SuCommon.TRANSLATION,
            SuCommon.GET_MODS: SuCommon.MODS_LIST,
            SuCommon.GET_FORMS: SuCommon.FORMS_LIST,
            SuCommon.GET_RULES: SuCommon.RULES,
            SuCommon.CONFIG_RESP: SuCommon.VOC_INIT
        }
        self.parser = SuParser.SuParser((SuCommon.GET_ROOTS, SuCommon.GET_MODS, SuCommon.GET_FORMS, SuCommon.TRANSLATE,
                                         SuCommon.GET_RULES, SuCommon.SAVE_FORM, SuCommon.NEW_WORD, SuCommon.CONFIG_RESP, SuCommon.EXIT_APP))

        self.words = []
        self.roots = []
        self.rules = {}

        self.config_changed = False

# ---------------------------------------------------------------------------------------
def su_voc_main_func(inp_q, outp_q):
    voc = SuVocabulary()

    config_data = voc.read_config()
    logging.debug(config_data)
    if config_data is not None:
        words_data, rules_data = voc.read_voc_data(config_data)
        if words_data is not None:
            voc.build_words(words_data)
            voc.build_rules(rules_data)
            outp_q.put(json.dumps({SuCommon.VOC_INIT: SuCommon.SUCCESS}))
        else:
            outp_q.put(json.dumps({SuCommon.VOC_INIT: SuCommon.CONFIG_REQ}))
    else:
        outp_q.put(json.dumps({SuCommon.VOC_INIT: SuCommon.CONFIG_REQ}))

    app_exit = False
    while not app_exit:
        while not inp_q.empty():
            msg = inp_q.get()
#            logging.debug('Message "%s" received', msg)

            key, parsed_data = voc.parser.parse(msg)
            logging.debug(key)
            logging.debug(parsed_data)

            if key == SuCommon.EXIT_APP:
                app_exit = True
                break

            out_data = voc.handler_fn[key](parsed_data)
            if out_data is not None:
                logging.debug('output data: %s', out_data)
                json_out_data = json.dumps({voc.res_code[key]: out_data})
                logging.debug('output data: %s', json_out_data)
                outp_q.put(json.dumps({voc.res_code[key]: out_data}))


