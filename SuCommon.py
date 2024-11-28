def enum(**enums):
    return type('Enum', (), enums)

ROOT = "root"
WORD_MODS = "word_mods"
FORM_NAMES = "form_names"
WORD_CLASS = "word_class"
WORDS = "words"
RULES = "rules"

GET_ROOTS = "get_roots"
ROOTS_LIST = "roots_list"

GET_MODS = "get_mods"
MODS_LIST = "mods_list"

GET_FORMS = "get_forms"
FORMS_LIST = "forms_list"

TRANSLATE = "translate"
TRANSLATION = "translation"

GET_RULES = "get_rules"

SAVE_FORM = "save_form"
NEW_FORM = "new_form"

NEW_WORD = "new_word"

VOC_INIT = "voc_init"
SUCCESS = "success"
CONFIG_REQ = "config_req"

CONFIG_RESP = "config_resp"
VOC_PATH = "voc_path"

GET_FULL_FORM = "get_full_form"
EXIT_APP = "exit_app"

