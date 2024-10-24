import os.path
import yaml
import SuWord
import SuCommon
import SuParser
import json
import logging

file_name = "./su_verbs.yaml"


class SuVocabulary():

    def build(self, data):
        for word in data["words"]:
            self.words.append(SuWord.SuVerb(data["word_class"], word))
            self.roots.append(word["root"])

        self.words.append(SuWord.SuNoun(""))
        logging.debug('%u %s', len(self.words), 'words')
#        for word in self.words:
#            logging.debug(word.getConj(SuCommon.Tenses.PAST))

        logging.debug(self.roots)

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
        trans = self.words[idx].getTrans()
        return trans

    def handle_get_form(self, data):
        logging.info(data)
        idx = self.roots.index(data)
        forms = self.words[idx].get_word_mods()
        return forms

    def handle_get_mods(self, data):
        logging.info(data)
        idx = self.roots.index(data[SuCommon.ROOT])
        forms = self.words[idx].get_word_mods(data[SuCommon.MODS_LIST])
        return forms


    def __init__(self):
        with open(file_name, 'r') as f:
            logging.info(f'Open {file_name}')
            data = yaml.safe_load(f)
            logging.debug(data["rules"])
            logging.debug(data["rules"]["word_mods"])
#            logging.debug(data["rules"]["word_mods"].keys())
#            my_keys = data["words"][0]["conj"].keys()
#            logging.debug(list(my_keys))

        self.handler_fn = {
            SuCommon.GET_ROOTS: self.handle_get_roots,
            SuCommon.TRANSLATE: self.handle_translate,
            SuCommon.GET_MODS: self.handle_get_mods,
         }
        self.res_code = {
            SuCommon.GET_ROOTS: SuCommon.ROOTS_LIST,
            SuCommon.TRANSLATE: SuCommon.TRANSLATION,
            SuCommon.GET_MODS: SuCommon.WORD_MODS,
        }
        self.parser = SuParser.SuParser((SuCommon.GET_ROOTS, SuCommon.GET_MODS, SuCommon.TRANSLATE, SuCommon.EXIT_APP))

        self.words = []
        self.roots = []

        self.build(data)

def su_voc_main_func(inp_q, outp_q):
    voc = SuVocabulary()

    app_exit = False
    while not app_exit:
        while not inp_q.empty():
            msg = inp_q.get()
            logging.debug('Message "%s" received', msg)

            key, parsed_data = voc.parser.parse(msg)
            logging.debug(key)
            logging.debug(parsed_data)

            if key == SuCommon.EXIT_APP:
                app_exit = True
                break

            out_data = voc.handler_fn[key](parsed_data)
            logging.debug('output data: %s', out_data)
            json_out_data = json.dumps({voc.res_code[key]: out_data})
            logging.debug('output data: %s', json_out_data)
            outp_q.put(json.dumps({voc.res_code[key]: out_data}))


