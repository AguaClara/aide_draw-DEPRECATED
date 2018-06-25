import os, sys, inspect
import importlib
import pkgutil
import json
from time import gmtime, strftime

def abs_path(file_path):
    """
    Takes a relative file path to the calling file and returns the correct
    absolute path.

    Needed because the Fusion 360 environment doesn't resolve relative paths
    well.
    """
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

def str_time():
    """
    Return the current time in a human-readable string
    """
    return strftime("%Y-%m-%d_%H_%M_%S", gmtime())

def add_ref(d:dict, fusion_object):
    """
    adds a reference to the dictionary with a key of "ref"
    """
    d["ref"] = fusion_object
    return d

def save_aide_json(d:dict, file_path:str):
    """
    Saves the dict as a JSON for long-term storage. This deletes all currently
    refs and saves this to a JSON file at the file_path given. Will create the
    file path if it doesn't exist. If it is relative, it is relative to This
    __file__ path
    """
    #strip the dictionary of all refs:
    return 0


###################### FUNCTIONS TODO ####################################


def strip_dictionary(d, t):
    """
    TODO: return a new dictionary that is stripped of a certain type. make this
    work with a list of types.
    """
    new_d = {}
    for k,v in d.items():
        if not k.split(":")[0] == t:
            if isinstance(v,dict):
                new_d[k] = strip_dictionary(d, t)
            else:
                new_d[k] = v
    return new_d


def map_dictionary(f, d):
    """
    TODO: Applies f(k, v) to all dictionary values and returns the resulting dictionary.
    Works with nested dictionaries
    """
    for k, v in d.items():
        if isinstance(v, dict):
            map_dictionary(f, d)
        else:
            todo = 0

def _load_json(file_path):
    """
    This should safely load jsons, ensuring jsons conform to AIDE standards and throw an error otherwise.
    simplest implementation possible right now:
    """
    try:
        d = json.load(open(file_path))
    except:
        raise
    else:
        return json.load(open(file_path))
