import SuCommon
import logging

class SuWord():
    def __init__(self, word_class):
        self.wordClass = word_class

    def getWordClass(self):
        return self.wordClass

    def getRoot(self):
        return None

#######################################################################
class SuNoun(SuWord):

    def __init__(self, data):
        self.root = "Not implemented"
        self.conj = "Not implemented"

    def getRoot(self):
        return self.root

    def getConj(self, key):
        return "Noun still not implemented"

#######################################################################
class SuVerb(SuWord):

    def __init__(self, word_class, data):
        super().__init__(word_class)
        self.root = data["root"]
        self.trans = data["trans"]
        key_list = list(data["word_mods"])
        self.word_mods = {}
        for key in key_list:
            self.word_mods[key] = data["word_mods"][key]
#        logging.debug(self.word_mods)

    def getRoot(self):
        return self.root

    def getForms(self):
        return self.word_mods

    def getTrans(self):
        return self.trans

    def getConj(self, key):
        return self.word_mods[key]

#######################################################################


