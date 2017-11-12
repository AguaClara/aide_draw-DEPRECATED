import os, sys, inspect
import importlib
import pkgutil
import adsk
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


######################## File/Folder Utilities ################################
def _load_json(file_path):
    """
    This should safely load jsons, ensuring jsons conform to AIDE standards and throw an error otherwise.
    simplest implementation possible right now:
    """
    return json.load(open(file_path))


def open_fdoc(file_path: str, root_folder = None):
    """
    Takes a file path string and opens the Fusion API dataFile given that file path using
    the defined root_folder. If no root_folder is specified AND it is a relative
    path, defaults to the currently active product's parent folder as the root
    folder. If the root_folder is specified AND it is an absolute path, the
    root folder is set to the active project's root folder.
    If the root folder IS set, the file path is treated as a relative path to the
    set root folder. The root_folder param is a dataFolder


    Note that this will work much faster the closer the desired file is to the
    root_folder. Therefore you should try as much as possible to give a short
    folder path and a specific root folder. The document object is then returned
    """
    fp_list = file_path.split("/")

    # User specified root_folder
    if root_folder:
        root_folder = adsk.fusion.dataFolder.cast(root_folder)
    # root_folder assumed based on absolute path rules
    elif fp_list[0] == '':
        root_folder = adsk.core.Application.get().data.activeProject.rootFolder
        fp_list = fp_list[1:]
    # root_folder assumed based on relative path rules
    else:
        root_folder = adsk.core.Application.get().activeDocument.dataFile.parentFolder

    # Extract the final doc name and version
    d_desired = fp_list[len(fp_list)-1].split(":")
    d_name = d_desired[0]
    d_version = None
    if len(d_desired) == 2:
        d_version = d_desired[1]
    elif len(d_desired) > 2:
        raise ValueError("Version numbering is ambiguous, {} is not a proper "
        "version name".format(''.join(d_desired[1:])))

    # dig into the final folder before hitting the document
    if len(fp_list) > 1:
       for f_name in fp_list[0:len(fp_list)-1]:
           root_folder = find_dataFolder(root_folder, f_name)

    # search through the datafiles to find the right one.
    d = None
    d = find_dataFile(root_folder, d_name)

    # if no colens, open the datafile directly to the latest version.
    # Otherwise, open to the version specified
    if d_version:
        d = find_version(d,d_version)

    adsk.core.Application.get().documents.open(d)

def find_version(dataFile, version_number):
    """
    Opens the specified version_number of the passed in dataFile
    """
    versions = dataFile.versions
    for i in range(versions.count):
        d_potential = versions.item(i)
        if d_potential:
            if d_potential.versionNumber == version_number:
                return d_potential

def find_dataFile(dataFolder, dataFile_name):
    """
    Finds the dataFile in the dataFolder. Will not search within subfolders.
    """
    files = dataFolder.dataFiles
    for i in range(files.count):
        df = files.item(i)
        if df.name == dataFile_name:
            return df
        else:
            raise ValueError("The dataFile {} was not found in the folder {}".format(dataFile_name, dataFolder.name))

def find_dataFolder(parent_dataFolder, dataFolder_name):
    """
    Finds a dataFolder within a dataFolder. Will not search within subfolders.
    """
    df = parent_dataFolder.dataFolders.itemByName(dataFolder_name)
    if df:
        return df
    else:
        raise ValueError("The dataFolder {} was not found in the folder {}".format(dataFolder_name, parent_dataFolder.name))


def str_time():
    """
    Return the current time in a human-readable string
    """
    return strftime("%Y-%m-%d %H_%M_%S", gmtime())


def map_dictionary(f, d):
    """
    Run f(k,v) on every k,v pair in the outermost level of d the dictionary
    """
    for k,v in d:
        f(k,v)
    return d
