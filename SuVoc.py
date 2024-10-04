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
#        rootsList = self.getRootsByKey(data)
        roots_list = list(filter(lambda x: x.startswith(data), self.roots))
        logging.debug('roots list: %s', roots_list)
        roots_and_class_list = []
        for root in roots_list:
            idx = self.roots.index(root)
            word_class = self.words[idx].getWordClass()
            roots_and_class_list.append({SuParser.ROOT: root, SuParser.WORD_CLASS: word_class})
        logging.debug(roots_and_class_list)
        return roots_and_class_list

    def handle_translate(self, data):
        logging.info(data)
        idx = self.roots.index(data)
        trans = self.words[idx].getTrans()
        return trans

    def handle_get_form(self, data):
        logging.info(data)
        idx = self.roots.index(data)
        forms = self.words[idx].getForms()
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
            SuParser.GET_ROOTS: self.handle_get_roots,
            SuParser.TRANSLATE: self.handle_translate,
            SuParser.GET_FORM: self.handle_get_form,
        }
        self.res_code = {
            SuParser.GET_ROOTS: SuParser.ROOTS_LIST,
            SuParser.TRANSLATE: SuParser.TRANS_RESULT,
            SuParser.GET_FORM: SuParser.FULL_FORM,
        }
        self.parser = SuParser.SuParser((SuParser.GET_ROOTS, SuParser.GET_FORM, SuParser.TRANSLATE, SuParser.EXIT_APP))

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

            if key == SuParser.EXIT_APP:
                app_exit = True
                break

            out_data = voc.handler_fn[key](parsed_data)
            logging.debug('output data: %s', out_data)
            json_out_data = json.dumps({voc.res_code[key]: out_data})
            logging.debug('output data: %s', json_out_data)
            outp_q.put(json.dumps({voc.res_code[key]: out_data}))




"""
    def myFunc(self, word):
        print(word.getRoot())
        print(self.key)
        if word.getRoot().startswith(self.key):
            return True
        else:
            return False

    def findRoot(self, key):
        self.key = key
        return list(filter(self.myFunc, self.words))
"""
