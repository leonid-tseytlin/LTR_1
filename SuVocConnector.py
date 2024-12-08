import json
import logging
import threading
import SuCommon
import SuParser
import PyQt5
from PyQt5.QtWidgets import QGraphicsObject

connector = None

class SuVocConnector(QGraphicsObject):
    strSignal = PyQt5.QtCore.pyqtSignal(str)
    listSignal = PyQt5.QtCore.pyqtSignal(list)
    dictSignal = PyQt5.QtCore.pyqtSignal(dict)

    def __init__(self, inp_q, outp_q):
        super().__init__()
        self.strSignal.connect(self.str_sig_handler)
        self.listSignal.connect(self.list_sig_handler)
        self.dictSignal.connect(self.dict_sig_handler)

        self.inp_q = inp_q
        self.outp_q = outp_q

        self.parser = SuParser.SuParser((SuCommon.VOC_INIT, SuCommon.ROOTS_LIST, SuCommon.MODS_LIST, SuCommon.FORMS_LIST, SuCommon.TRANSLATION, SuCommon.RULES))
        self.ctxCb = None

        self.resp_type_fn = {
            str: self.str_sig_emit,
            list: self.list_sig_emit,
            dict: self.dict_sig_emit,
        }

    def str_sig_emit(self, str_resp):
        self.strSignal.emit(str_resp)

    def list_sig_emit(self, list_resp):
        self.listSignal.emit(list_resp)

    def dict_sig_emit(self, dict_resp):
        self.dictSignal.emit(dict_resp)

    def listen_thread_func(self, inp_q, resp_type):
        logging.info('Thread running')
        msg = inp_q.get()
        logging.debug('Message "%s" received', msg)
        key, parsed_data = self.parser.parse(msg)
        logging.debug(key)
        logging.debug(parsed_data)
        self.resp_type_fn[resp_type](parsed_data)

    def create_listener(self, resp_type):
        listen_thread = threading.Thread(target=self.listen_thread_func, args=(self.inp_q, resp_type))
        listen_thread.start()

# ---------------------------------------------------------------------------
    def str_sig_handler(self, str_resp):
        logging.debug('Message "%s" received', str_resp)
        self.ctxCb(str_resp)

    def list_sig_handler(self, list_resp):
        logging.debug('Message "%s" received', list_resp)
        self.ctxCb(list_resp)

    def dict_sig_handler(self, dict_resp):
        logging.debug('Message "%s" received', dict_resp)
        self.ctxCb(dict_resp)

# ---------------------------------------------------------------------------
    def wait_for_voc_ready(self, cb_fn):
        self.ctxCb = cb_fn
        self.create_listener(str)

    def get_roots_by_starting(self, starting, cb_fn):
        self.ctxCb = cb_fn
        self.create_listener(list)
        self.outp_q.put(json.dumps({SuCommon.GET_ROOTS: starting}))

    def get_root_translation(self, root_word, cb_fn):
        self.ctxCb = cb_fn
        self.create_listener(str)
        self.outp_q.put(json.dumps({SuCommon.TRANSLATE: {SuCommon.ROOT: root_word}}))

    def get_mods_by_root(self, root, mods_list, cb_fn):
        self.ctxCb = cb_fn
        self.create_listener(list)
        self.outp_q.put(json.dumps({SuCommon.GET_MODS: {SuCommon.ROOT: root, SuCommon.MODS_LIST: mods_list}}))

    def get_forms_by_root(self, root, mods_list, cb_fn):
        self.ctxCb = cb_fn
        self.create_listener(list)
        self.outp_q.put(json.dumps({SuCommon.GET_FORMS: {SuCommon.ROOT: root, SuCommon.MODS_LIST: mods_list}}))

    def get_rules(self, cb_fn):
        self.ctxCb = cb_fn
        self.create_listener(dict)
        self.outp_q.put(json.dumps({SuCommon.GET_RULES: ""}))

    def set_new_form(self, root, new_form):
        self.outp_q.put(json.dumps({SuCommon.SAVE_FORM: {SuCommon.ROOT: root, SuCommon.NEW_FORM: new_form}}))

    def set_new_word(self, root, word_class, translation):
        self.outp_q.put(json.dumps({SuCommon.NEW_WORD: {SuCommon.ROOT: root, SuCommon.WORD_CLASS: word_class, SuCommon.TRANSLATION: translation}}))

    def send_configuration(self, config_data):
        self.outp_q.put(json.dumps({SuCommon.CONFIG_RESP: config_data}))

    def send_exit_app_to_voc(self):
        self.outp_q.put(json.dumps({SuCommon.EXIT_APP: ""}))

def init_connector(inp_q, outp_q):
    global connector
    connector = SuVocConnector(inp_q, outp_q)
