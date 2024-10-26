def enum(**enums):
    return type('Enum', (), enums)

ROOT = "root"
WORD_MODS = "word_mods"
WORD_CLASS = "word_class"
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

GET_FULL_FORM = "get_full_form"
EXIT_APP = "exit_app"

