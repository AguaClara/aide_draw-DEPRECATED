################################ DRAW FUNCTIONS ###############################

import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import warnings
import json
from . import aide_gui
import importlib
from . import utilities as ut

try:
    fgen_registry = json.load(open(ut.abs_path("fgen_registry.json")))
    sys.path.append(ut.abs_path("fgens"))
except:
    print(__file__)
    raise FileNotFoundError("The fgen_registry.json is missing from the fgens folder.")


def draw_fdoc(fdoc_dict, fdoc_template, fdoc_target_folder):
    """
    Runs through the fgens defined in the fdoc_dict and passes given args to the
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
    
    
def create_folder_structure(folder_dict, parent_folder):
    """
    Creates the skeleton folder structure specified in the AIDE-compliant 
    JSON and returrns the folder_dict dictionary with added references to the 
    folders where the parent_folder reference is the base. This way, we
    don't need to make server calls whenever needing to walk the directory
    tree. This is a recursive function, so we need to accept the
    folder_refs_dict in the signature, but we don't expect users to enter this
    as this gets created within the first of the recursive calls.
    
    A single call (without recursive) returns the folder_dict of the form,
    where the "ref" keys are added:
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
    
    # Are there no folders? aka folder_dict[folder_name]["folders"]={}
    if len(folder_dict) > 0: 
        for folder_name in folder_dict:
            # make the ref of the passed in parent_folder
            if "ref" not in folder_dict[folder_name]:
                new_folder = parent_folder.dataFolders.add(folder_name)
            else:
                raise ValueError("keyword 'ref' cannot be used within the "
                    "AIDE-JSON")
            folder_dict[folder_name]["ref"] = new_folder
            # If there are children folders, call recursively
            if "folders" in folder_dict[folder_name]:
                folder_dict[folder_name] = \
                    create_folder_structure(folder_dict[folder_name]["folders"], new_folder)
    else:
        return folder_dict
            
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
