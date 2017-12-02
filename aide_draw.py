################################ DRAW FUNCTIONS ###############################
"""
All the functions that change Fusion land based on JSON land!
"""

import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import warnings
import json
from . import aide_gui
import importlib
from . import utilities as ut
from . import json_keys as keys

try:
    sys.path.append(ut.abs_path("fgens"))
    fgen_registry = json.load(open(ut.abs_path("fgen_registry.json")))
except:
    print(__file__)
    raise FileNotFoundError("The fgen_registry.json is missing from the fgens folder.")

def parametrize_fdoc(params_desired, fdoc):
    """Adjusts the fusion document's parameters to the desired expressions

    Parameters
    ----------
    params_desired : flat dictionary
        A dictionary without any nesting that has parameter_name:expression key
        -value pairs.
    fdoc : FusionDocument
        A FusionDocument in memory.

    Returns
    -------
    params_changed : list of strings
        A list of all the parameters that were changed in the given
        FusionDocument.

    Raises
    ------
    UserWarning
        Raised when the parameter specified in 'params_desired' is not available
        in the userParameters of the FusionDocument
    """
    params = adsk.fusion.FusionDocument.cast(fdoc).design.allParameters
    params_changed = []
    # Loop through the parameters  dictionary in a single component
    for param_name in params_desired:
        param_desired = params_desired[param_name]
        param_actual = params.itemByName(param_name)
        if param_actual:
            param_actual.expression = str(param_desired)
            params_changed.append(param_name)
        else:
            raise UserWarning(param_name + " is in the json, but not in the"
                " model. All other values were changed.")
    return params_changed


def draw_fdoc(fdoc_dict, fdoc_template, fdoc_target_folder):
    """Runs through the fgens defined in the fdoc_dict and passes given args to the
    relevant fgen
    """
    if 'fgens' in fdoc_dict:
        for fgen_dict in fdoc_dict['fgens']:
            #extract the fgen name/key
            fgen_key = list(fgen_dict.keys())[0]
            # imports are smart so this will not double import.
            if fgen_key in fgen_registry :
                fgen_module = importlib.import_module(fgen_key)
                fgen_module.start(fdoc_template, fgen_dict[fgen_key]['args'])
            else :
                raise ValueError("couldn't find the fgen. Make sure the fgen is"
                    " defined correctly within the fgen_registry")
        # Save the final fdocs
        _save(fdoc_template, fdoc_target_folder, fdoc_dict['name'])


def _save(fdoc, folder, name):
    """
    Saves the fusionDocument fdoc in the specified dataFolder folder with the
    specified name and then opens the modified document and closes the fdoc template
    """
    fdoc.saveAs(name, folder, '', '')
    adsk.doEvents()


def parametrize_recursive(folder_dict_with_refs):
    """
    Takes a AIDE-compliant dictionary and opens and parametrizes all the fdocs to the
    specified sizes.
    """
    for k,v in folder_dict_with_refs.items():
        if k.split(":")[1] == keys.FDOC_TYPE:
            fdoc_dict = folder_dict_with_refs[k]
            app = adsk.core.Application.get()
            fdoc = app.documents.open(fdoc_dict[keys.FILE_REF_KEY])
            parametrize_fdoc(fdoc_dict[keys.PARAMETERS_KEY], fdoc)
        elif k.split(":")[1] == keys.FOLDER_REF_KEY:
            folder_dict = folder_dict_with_refs[k]
            parametrize_recursive(folder_dict, folder_dict[keys.FOLDER_REF_KEY])



def sync_folder_structure(folder_dict, parent_folder):
    """
    This modifies the fusion folders, and DOES NOT TOUCH THE FOLDER_DICT folders
    except to add refs.

    Syncs the folder structure specified in the AIDE-compliant
    JSON and the folder structure in Fusion under the parent_folder. If a folder
    specified in folder_dict doesn't exist, this function will create one.
    Returrns the folder_dict dictionary with added references to the
    folders where the parent_folder reference is the root. This way, we
    don't need to make server calls whenever needing to walk the directory
    tree.

    The folder_dict is of the form:
    {
        <folder_name>:{
            "ref" : <folder_reference>,
            "folders": create_folder_structure(folder_dict, parent_folder)
            }
        }
    }
    """

    # make sure parent_folder is a dataFolder
    try:
        parent_folder = adsk.core.DataFolder.cast(parent_folder)
    except:
        raise TypeError("parent_folder is of type: {}, but needs to be of"
            "type: dataFolder".format(parent_folder.classType()))

    # Are there no folders specified in folder_dict?
    if len(folder_dict) > 0:
        for folder_name in folder_dict:
            # add the ref of the children folders, making the folder if necessary
            if keys.FOLDER_REF_KEY not in folder_dict[folder_name]:
                folder = parent_folder.dataFolders.itemByName(folder_name)
                # if the folder doesn't exist, make it!
                if not folder:
                    folder = parent_folder.dataFolders.add(folder_name)
            else:
                raise ValueError("keyword 'ref' cannot be used within the "
                    "AIDE-JSON")
            folder_dict[folder_name][keys.FOLDER_REF_KEY] = folder
            # If there are children folders specified in folder_dict, call recursively
            if "folders" in folder_dict[folder_name]:
                folder_dict[folder_name]["folders"].update(sync_folder_structure(folder_dict[folder_name]["folders"], folder))

    return folder_dict


def _draw_recursive_json(folder_dict, fdoc_folder, fdoc_target_folder):
    """
    Takes a component AIDE-compliant dictionary and draws
    all child component components. Passed in is the fdoc_folder that the
    current layer in the dictionary is referring to.
    and then re-adds them to parents and saves all
    in an organized folder hierarchy. The first folder is assumed to be the one
    you are in.
    """
    drawn_fdocs = []

    # Create all the child folders and make recursive calls on folders:
    if 'folders' in folder_dict and len(folder_dict['folders']) > 0:
        for name in folder_dict['folders']:
            child_template_folder_dict = folder_dict['folders'][name]
            child_target_folder_dict = fdoc_target_folder.dataFolders.add(name)
            child_template_folder = fdoc_template_folder.dataFolders.itemByName(name)
            if not child_fdoc_folder:
                raise ValueError("The file specified in json doesn't exist.")
    #          # Recursive call with the new fdoc folder
    #         drawn_fdocs = drawn_fdocs.extend(_draw_recursive_json(child_fdoc_dict, child_fdoc_folder,
    #                              child_fdoc_target_folder))
    #
    # # Loop through all the files in the current folder. This takes a while,
    # # so make sure to do it only once.
    # for i in range(fdoc_folder.dataFiles.count):
    #     datafile_potential_template = fdoc_folder.dataFiles.item(i)
    #     # Get all defined fdoc_dicts for fdocs using this template
    #     fdoc_template_dict = {k: v for k, v in folder_dict['fdocs'].items() if v['template'] == datafile_potential_template.name}
    #     if len(fdoc_template_dict) > 0:
    #         # We know to use this template
    #         datafile_template = datafile_potential_template
    #         # Loop through all iterations of this fdoc defined in the dict.
    #         for fdoc_dict in fdoc_template_dict:
    #             # Make sure sizing parameters are found
    #             if 'parameters' in fdoc_dict:
    #                 # Open the fdoc_template for sizing
    #                 fdoc_template = adsk.core.Application.get().documents.open(datafile_template)
    #                 _size(fdoc_template, fdoc_dict['parameters'])
    #                 _save(fdoc_template, fdoc_target_folder, fdoc_dict['name'])
    #                 drawn_fdocs = drawn_fdocs.append(fdoc_dict['name'])
    #             else:
    #                 warnings.warn("Template specified, but no parameters set"
    #                     "in the fdocs' json. Defaulting to copying the fdoc"
    #                     "directly.")
    #
    # # This is the base case, when all that are left are fdocs.
    # if 'fdocs' in folder_dict and len(folder_dict['fdocs']) > 0:
    #     for fdoc in folder_dict['fdocs']:
    #         # need to create the component
    #         if 'create' in fdoc:
    #             _create(fdoc['create'])
    #             drawn_fdocs = drawn_fdocs.append(fdoc['name'])
    #
    # return drawn_fdocs
