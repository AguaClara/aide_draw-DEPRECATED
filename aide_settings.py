import json
import utilities as ut

GLOBAL_FGEN_LIST_KEY = "global_fgen_list"

settings_dict = json.load(open(ut.abs_path("config.json")))


def get_global_fgen_list():
    return settings_dict[GLOBAL_FGEN_LIST_KEY]
