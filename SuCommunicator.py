import PyQt5
from PyQt5.QtWidgets import QGraphicsObject
import logging
import SuCommon
import SuVocFrontAgent

#=====================================================================================================
class VocCommunicator(QGraphicsObject):
    rootsVocSignal = PyQt5.QtCore.pyqtSignal(list)
    transVocSignal = PyQt5.QtCore.pyqtSignal(str)
    modsVocSignal = PyQt5.QtCore.pyqtSignal(list)

    def __init__(self, voc_agent):
        super().__init__()
        self.rootsVocSignal.connect(self.get_roots_sig_handler)
        self.transVocSignal.connect(self.get_translation_sig_handler)
        self.modsVocSignal.connect(self.get_mods_sig_handler)

        self.voc_agent = voc_agent
        self.currentSession = None
        self.currentModDepth = None
        logging.debug('Communicator created')

    def start_session(self, starting, session):
        self.currentSession = session
        self.voc_agent.get_roots_by_starting(starting, self.get_roots_callback)

    def get_roots_callback(self, roots):
        self.rootsVocSignal.emit(roots)

    def get_roots_sig_handler(self, roots):
        logging.debug('Message "%s" received', roots)
        self.currentSession.add_root_managers(roots)

#---------------------------------------------------------------------------
    def get_root_translation(self, root_word):
        self.voc_agent.get_translation_by_root(root_word, self.get_translation_callback)

    def get_translation_callback(self, trans):
        self.transVocSignal.emit(trans)

    def get_translation_sig_handler(self, trans_word):
        logging.debug('Message "%s" received', trans_word)
        self.currentSession.set_root_translation(trans_word)

# ---------------------------------------------------------------------------
    def get_root_mods(self, root_word, mod_word):
        self.currentModDepth = self.currentSession.get_mod_depth()
        mods_hierarchy_list = self.currentSession.update_mod_hierarchy(mod_word)
        self.voc_agent.get_mods_by_root(root_word, mods_hierarchy_list, self.get_mods_callback)

    def get_mods_callback(self, trans):
        self.modsVocSignal.emit(trans)

    def get_mods_sig_handler(self, mods_list):
        logging.debug('Message "%s" received', mods_list)
        self.currentSession.set_form_mods(mods_list, self.currentModDepth)

# ---------------------------------------------------------------------------

    def __del__(self):
        logging.debug('Communicator deleted')


