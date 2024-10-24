import json
import logging
import threading
import SuCommon
import SuParser


class SuVocFrontAgent():
    def __init__(self, inp_q, outp_q):
        self.inp_q = inp_q
        self.outp_q = outp_q

        self.parser = SuParser.SuParser((SuCommon.ROOTS_LIST, SuCommon.WORD_MODS, SuCommon.TRANSLATION))

    def listen_thread_func(self, inp_q, cbFn):
        logging.info('Thread running')
        msg = inp_q.get()
        logging.debug('Message "%s" received', msg)
        key, parsed_data = self.parser.parse(msg)
        logging.debug(key)
        logging.debug(parsed_data)
        cbFn(parsed_data)

    def get_roots_by_starting(self, starting, cbFn):
        self.createListener(cbFn)
        self.outp_q.put(json.dumps({SuCommon.GET_ROOTS: starting}))

    def get_translation_by_root(self, root, cb_fn):
        self.createListener(cb_fn)
        self.outp_q.put(json.dumps({SuCommon.TRANSLATE: {SuCommon.ROOT: root}}))

    def get_mods_by_root(self, root, mods_list, cb_fn):
        self.createListener(cb_fn)
        self.outp_q.put(json.dumps({SuCommon.GET_MODS: {SuCommon.ROOT: root, SuCommon.MODS_LIST: mods_list}}))

    def get_full_form_by_root(self, root):
        self.outp_q.put(json.dumps({SuCommon.GET_FORM: root}))

    def send_exit_app_to_voc(self):
        self.outp_q.put(json.dumps({SuCommon.EXIT_APP: ""}))

    def createListener(self, cbFn):
        listen_thread = threading.Thread(target=self.listen_thread_func, args=(self.inp_q, cbFn))
        listen_thread.start()
