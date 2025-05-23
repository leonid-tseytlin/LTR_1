import os.path
import yaml
import LtrWord
import LtrCommon
import LtrParser
import json
import logging
from datetime import datetime

config_file_name = "./ltr_config.yaml"


class LtrVocabulary():

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
        if not os.path.exists(config_data[LtrCommon.WORDS_FILE]):
            logging.error("File %s does not exist", config_data[LtrCommon.WORDS_FILE])
            return None
        if not os.path.exists(config_data[LtrCommon.RULES_FILE]):
            logging.error("File %s does not exist", config_data[LtrCommon.RULES_FILE])
            return None
        try:
            with open(config_data[LtrCommon.WORDS_FILE], 'r') as words_file:
                logging.info(f'Open {config_data[LtrCommon.WORDS_FILE]}')
                words_data = yaml.safe_load(words_file)
                self.words_file = config_data[LtrCommon.WORDS_FILE]
        except:
            logging.error("Not yaml file")
            return None
        try:
            with open(config_data[LtrCommon.RULES_FILE], 'r') as rules_file:
                logging.info(f'Open {config_data[LtrCommon.RULES_FILE]}')
                rules_data = yaml.safe_load(rules_file)
                self.rules_file = config_data[LtrCommon.RULES_FILE]
        except:
            logging.error("Not yaml file")
            return None

        return words_data, rules_data

    def build_words(self, data):
        for word in data:
#            logging.debug(word)
            self.words.append(LtrWord.LtrWord(word))
            self.roots.append(word[LtrCommon.ROOT])

        logging.debug(self.roots)
        logging.debug(self.words)

    def build_rules(self, data):
        logging.debug(data)
        for rule in data[LtrCommon.RULES]:
            self.rules[rule[LtrCommon.WORD_CLASS]] = rule
        logging.debug(self.rules)

    def validate_config_data(self, config_data):
        return True

#---------------------------------------------------------------------------------------
#   MESSAGE HANDLERS

    def handle_config_response(self, config_data):
        logging.debug(config_data)
        if not self.validate_config_data(config_data):
            return LtrCommon.CONFIG_REQ
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
            roots_and_class_list.append({LtrCommon.ROOT: root, LtrCommon.WORD_CLASS: word_class})
        logging.debug(roots_and_class_list)
        return roots_and_class_list

    def handle_translate(self, data):
        logging.info(data)
        idx = self.roots.index(data[LtrCommon.ROOT])
        trans = self.words[idx].get_translation()
        return trans

    def handle_get_forms(self, data):
        logging.info(data)
        idx = self.roots.index(data[LtrCommon.ROOT])
        forms = self.words[idx].get_word_forms(data[LtrCommon.MODS_LIST])
        return forms

    def handle_get_mods(self, data):
        logging.info(data)
        idx = self.roots.index(data[LtrCommon.ROOT])
        mods = self.words[idx].get_word_mods(data[LtrCommon.MODS_LIST])
        logging.debug(mods)
        return mods

    def handle_get_rules(self, data):
        return self.rules

    def handle_save_form(self, data):
        logging.debug(data)
        idx = self.roots.index(data[LtrCommon.ROOT])
        self.words[idx].set_word_form(data[LtrCommon.NEW_FORM])
        self.voc_updated = True
        return None

    def handle_new_word(self, data):
        logging.debug(data)
        word_data = {LtrCommon.ROOT: data[LtrCommon.ROOT], LtrCommon.WORD_CLASS: data[LtrCommon.WORD_CLASS], LtrCommon.TRANSLATION: data[LtrCommon.TRANSLATION],
                     LtrCommon.WORD_MODS: None}
        logging.debug(word_data)

        self.words.append(LtrWord.LtrWord(word_data))
        self.roots.append(data[LtrCommon.ROOT])
        self.voc_updated = True

    def handle_exit(self, data):
        logging.debug("Handle EXIT signal")

        if self.voc_updated:
            backup_words_file = os.path.splitext(os.path.basename(self.words_file))[0] + "_" + datetime.now().strftime("%Y_%m_%d-%H_%M_%S") + ".yaml"
            logging.debug(backup_words_file)

            logging.info("File %s was changed. Save backup file %s", self.words_file, backup_words_file)
            os.rename(self.words_file, backup_words_file)

            with open(self.words_file, 'w') as outfile:
                yaml.emitter.Emitter.prepare_tag = lambda self, tag: ''
                yaml.Dumper.add_representer(type(None), lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '~'))

                yaml.dump(self.words, outfile, sort_keys=False, explicit_start=True, allow_unicode=True)

        return None

# ---------------------------------------------------------------------------------------
    def __init__(self):

        self.handler_fn = {
            LtrCommon.GET_ROOTS: self.handle_get_roots,
            LtrCommon.TRANSLATE: self.handle_translate,
            LtrCommon.GET_MODS: self.handle_get_mods,
            LtrCommon.GET_FORMS: self.handle_get_forms,
            LtrCommon.GET_RULES: self.handle_get_rules,
            LtrCommon.SAVE_FORM: self.handle_save_form,
            LtrCommon.NEW_WORD: self.handle_new_word,
            LtrCommon.CONFIG_RESP: self.handle_config_response,
            LtrCommon.EXIT_APP: self.handle_exit
        }
        self.res_code = {
            LtrCommon.GET_ROOTS: LtrCommon.ROOTS_LIST,
            LtrCommon.TRANSLATE: LtrCommon.TRANSLATION,
            LtrCommon.GET_MODS: LtrCommon.MODS_LIST,
            LtrCommon.GET_FORMS: LtrCommon.FORMS_LIST,
            LtrCommon.GET_RULES: LtrCommon.RULES,
            LtrCommon.CONFIG_RESP: LtrCommon.VOC_INIT
        }
        self.parser = LtrParser.LtrParser((LtrCommon.GET_ROOTS, LtrCommon.GET_MODS, LtrCommon.GET_FORMS, LtrCommon.TRANSLATE,
                                         LtrCommon.GET_RULES, LtrCommon.SAVE_FORM, LtrCommon.NEW_WORD, LtrCommon.CONFIG_RESP, LtrCommon.EXIT_APP))

        self.words = []
        self.roots = []
        self.rules = {}

        self.words_file = None
        self.rules_file = None

        self.voc_updated = False

        self.config_changed = False

# ---------------------------------------------------------------------------------------
def su_voc_main_func(inp_q, outp_q):
    voc = LtrVocabulary()

    config_data = voc.read_config()
    logging.debug(config_data)
    if config_data is not None:
        words_data, rules_data = voc.read_voc_data(config_data)
        if words_data is not None:
            voc.build_words(words_data)
            voc.build_rules(rules_data)
            outp_q.put(json.dumps({LtrCommon.VOC_INIT: LtrCommon.SUCCESS}))
        else:
            outp_q.put(json.dumps({LtrCommon.VOC_INIT: LtrCommon.CONFIG_REQ}))
    else:
        outp_q.put(json.dumps({LtrCommon.VOC_INIT: LtrCommon.CONFIG_REQ}))

    app_exit = False
    while not app_exit:
        while not inp_q.empty():
            msg = inp_q.get()
#            logging.debug('Message "%s" received', msg)

            key, parsed_data = voc.parser.parse(msg)
            logging.debug(key)
            logging.debug(parsed_data)

            if key == LtrCommon.EXIT_APP:
                app_exit = True

            out_data = voc.handler_fn[key](parsed_data)
            if out_data is not None:
                logging.debug('output data: %s', out_data)
                json_out_data = json.dumps({voc.res_code[key]: out_data})
                logging.debug('output data: %s', json_out_data)
                outp_q.put(json.dumps({voc.res_code[key]: out_data}))


