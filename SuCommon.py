def enum(**enums):
    return type('Enum', (), enums)

ROOT = "root"
WORD_MODS = "word_mods"
WORD_CLASS = "class"

GET_ROOTS = "get_roots"
ROOTS_LIST = "roots_list"

GET_MODS = "get_mods"
MODS_LIST = "mods_list"

TRANSLATE = "translate"
TRANSLATION = "translation"

GET_FORM = "get_form"
EXIT_APP = "exit_app"

