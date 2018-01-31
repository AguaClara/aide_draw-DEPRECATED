"""
This is a script that takes the current design, and builds a referenced
json tree from all the various document references.
"""
import adsk
import json_keys as keys
import utilities as ut

def sync_dict(folder_dict, parent_folder):
    """
    This modifies the folder_dict, and DOES NOT TOUCH THE FUSION folders.

    This updates the json (or makes one if necessary) with the current folder
    structure to generate a structure such as, where the folder is the root:
    The folder_dict produced is of the form:
    {
        <folder_name>:{
            "ref" : <folder_reference>,
            "folders": sync_dict(folder_dict, parent_folder)
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

    # Add all files in the current folder if there are any:
    file_count = parent_folder.dataFiles.count
    if file_count >  0:
        for i in range(file_count):
            data_file = parent_folder.dataFiles.item(i)
            if not data_file.name + ":" + keys.FDOC_TYPE in folder_dict:
                folder_dict[data_file.name + ":" + keys.FDOC_TYPE] = {}
            folder_dict[data_file.name + ":" + keys.FDOC_TYPE] = sync_fdoc_dict(data_file, folder_dict[data_file.name + ":" + keys.FDOC_TYPE])

    # Are there no folders in parent_folder?
    folder_count = parent_folder.dataFolders.count
    if  folder_count >  0:
        for i in range(folder_count):
            # Add the folder_dict if necessary
            folder = parent_folder.dataFolders.item(i)
            if folder.name not in folder_dict:
                folder_dict[folder.name] = {}
            # Add the ref if necessary
            if keys.DATA_FOLDER_KEY not in folder_dict[folder.name]:
                folder_dict[folder.name][keys.DATA_FOLDER_KEY] = folder
            else:
                raise ValueError("keyword 'ref' cannot be used within the "
                    "AIDE-JSON")

            # If there are children folders, call recursively
            if folder.dataFolders.count > 0:
                if "folders" not in folder_dict[folder.name]:
                    folder_dict[folder.name]["folders"] = {}
                child_folder_dict = folder_dict[folder.name]["folders"]
                folder_dict[folder.name]["folders"].update(sync_dict(child_folder_dict, folder))

    return folder_dict


def sync_fdoc_dict(data_file, fdoc_dict):
    # Add the file_dict if necessary
    if keys.DATA_FILE_KEY not in fdoc_dict:
        fdoc_dict[keys.DATA_FILE_KEY] = data_file
    else:
        raise ValueError("keyword 'ref' cannot be used within the "
                         "AIDE-JSON")
    # Add the parameters if necessary
    if not "parameters" in fdoc_dict:
        fdoc_dict[keys.PARAMETERS_KEY]= get_parameter_dictionary(data_file)
    return fdoc_dict


def get_parameter_dictionary(data_file):
    """
    Opens the dataFile if necessary and returns a dictionary with all the
    parameters filled in.
    """
    app = adsk.core.Application.get()
    fdoc = app.documents.open(data_file)
    params = adsk.fusion.FusionDocument.cast(fdoc).design.userParameters
    param_d = {}
    if params:
        param_count = params.count
        if param_count > 0:
            for i in range(param_count):
                param = params.item(i)
                param_d[param.name] = param.expression
    return param_d
