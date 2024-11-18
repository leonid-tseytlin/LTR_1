import os.path
import yaml
import SuWord
import SuCommon
import SuParser
import json
import logging

file_name = "./su_verbs.yaml" #Temporary. Should be defined by configuration


class SuVocabulary():

    def build_words(self, data):
        for word in data["words"]:
            self.words.append(SuWord.SuVerb(data[SuCommon.WORD_CLASS], word))
            self.roots.append(word[SuCommon.ROOT])

        logging.debug(self.roots)

    def build_rules(self, data):
        self.rules[data[SuCommon.WORD_CLASS]] = data["rules"]
        logging.debug(self.rules)
        #            logging.debug(data["rules"]["word_mods"])


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
        word_data = {SuCommon.ROOT: data[SuCommon.ROOT], SuCommon.TRANSLATION: data[SuCommon.TRANSLATION],
                     SuCommon.WORD_MODS: None}
        logging.debug(word_data)

        self.words.append(SuWord.SuVerb(data[SuCommon.WORD_CLASS], word_data))
        self.roots.append(data[SuCommon.ROOT])

    def __init__(self):

        self.handler_fn = {
            SuCommon.GET_ROOTS: self.handle_get_roots,
            SuCommon.TRANSLATE: self.handle_translate,
            SuCommon.GET_MODS: self.handle_get_mods,
            SuCommon.GET_FORMS: self.handle_get_forms,
            SuCommon.GET_RULES: self.handle_get_rules,
            SuCommon.SAVE_FORM: self.handle_save_form,
            SuCommon.NEW_WORD: self.handle_new_word,
        }
        self.res_code = {
            SuCommon.GET_ROOTS: SuCommon.ROOTS_LIST,
            SuCommon.TRANSLATE: SuCommon.TRANSLATION,
            SuCommon.GET_MODS: SuCommon.MODS_LIST,
            SuCommon.GET_FORMS: SuCommon.FORMS_LIST,
            SuCommon.GET_RULES: SuCommon.RULES,
        }
        self.parser = SuParser.SuParser((SuCommon.GET_ROOTS, SuCommon.GET_MODS, SuCommon.GET_FORMS, SuCommon.TRANSLATE,
                                         SuCommon.GET_RULES, SuCommon.SAVE_FORM, SuCommon.NEW_WORD, SuCommon.EXIT_APP))

        self.words = []
        self.roots = []
        self.rules = {}

        with open(file_name, 'r') as f:
            logging.info(f'Open {file_name}')
            data = yaml.safe_load(f)

            self.build_words(data)
            self.build_rules(data)

def su_voc_main_func(inp_q, outp_q):
    voc = SuVocabulary()

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


