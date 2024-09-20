import json
import logging
import threading
import SuParser


class SuVocFrontAgent():
    def __init__(self, inp_q, outp_q):
        self.inp_q = inp_q
        self.outp_q = outp_q

        self.parser = SuParser.SuParser((SuParser.ROOTS_LIST, SuParser.FULL_FORM))

    def listenThreadFunc(self, inp_q, cbFn):
        logging.info('Thread running')
        msg = inp_q.get()
        logging.debug('Message "%s" received', msg)
        key, parsed_data = self.parser.parse(msg)
        logging.debug(key)
        logging.debug(parsed_data)
        cbFn(parsed_data)

    def getRootsByStarting(self, starting, cbFn):
        self.createListener(cbFn)
        self.outp_q.put(json.dumps({SuParser.STARTING: starting}))

    def getFullFormByRoot(self, root):
        self.outp_q.put(json.dumps({SuParser.ROOT: root}))

    def createListener(self, cbFn):
        t1 = threading.Thread(target=self.listenThreadFunc, args=(self.inp_q, cbFn))
        t1.start()
