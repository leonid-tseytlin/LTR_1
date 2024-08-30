import os.path
import yaml
import SuWord
import SuCommon
import json
import logging

file_name = "./su_verbs.yaml"


class SuVocabulary():

    def build(self, data):
        for verb in data["verb"]:
            self.words.append(SuWord.SuVerb(verb))
            self.roots.append(verb["root"])

        self.words.append(SuWord.SuNoun(""))
        logging.debug('%u %s', len(self.words), 'words')
        for word in self.words:
            logging.debug(word.getConj(SuCommon.Tenses.PAST))


        logging.debug(self.roots)

    def __init__(self):
        with open(file_name, 'r') as f:
            logging.info(f'Open {file_name}')
            data = yaml.safe_load(f)

        self.words = []
        self.roots = []

        self.build(data)

    def getRootsByKey(self, key):
        return list(filter(lambda x: x.startswith(key), self.roots))

    def getFormsByRoot(self, root):
        idx = self.roots.index(root)
        return json.dumps(self.words[idx].getForms())

def SuVocMainFunc(inp_q, outp_q):
    Voc = SuVocabulary()

    while not inp_q.empty():
        key = inp_q.get()
        logging.debug('key "%s" received', key)

        rootList = Voc.getRootsByKey("ky")

        logging.debug('roots list: %s', rootList)



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
