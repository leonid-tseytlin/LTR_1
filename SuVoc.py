import os.path
import yaml
import SuWord
import SuCommon
import json

class SuVocabulary():

    def build(self, data):
        for verb in data["verb"]:
            self.words.append(SuWord.SuVerb(verb))
            self.roots.append(verb["root"])

        self.words.append(SuWord.SuNoun(""))

        print(len(self.words))
        for word in self.words:
#            print(word.getRoot())
            print(word.getConj(SuCommon.Tenses.PAST))

        print(self.roots)

    def __init__(self):
        file_name = "./su_verbs.yaml"
        with open(file_name, 'r') as f:
            print(f'Open {file_name}')
            data = yaml.safe_load(f)

        self.words = []
        self.roots = []

        self.build(data)

    def getRootsByKey(self, key):
        return list(filter(lambda x: x.startswith(key), self.roots))

    def getFormsByRoot(self, root):
        idx = self.roots.index(root)
        return json.dumps(self.words[idx].getForms())

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
