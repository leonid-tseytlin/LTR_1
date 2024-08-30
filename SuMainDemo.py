import SuVoc
import json

if __name__ == '__main__':
    print('SuVerb')
    Voc = SuVoc.SuVocabulary()

    rootList = Voc.getRootsByKey("ky")

    print(rootList)

    for root in rootList:
        print(json.loads(Voc.getFormsByRoot(root)))
