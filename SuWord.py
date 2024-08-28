import SuCommon

class SuWord():

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
        return "Not implemented"

#######################################################################
class SuVerb(SuWord):

    def __init__(self, data):
        self.root = data["root"]
        self.conj = data["conj"]

    def getRoot(self):
        return self.root

    def getForms(self):
        return self.conj

    def getConj(self, key):
        return self.conj[key]

#######################################################################


