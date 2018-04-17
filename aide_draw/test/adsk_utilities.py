import os, sys, inspect
import importlib
import pkgutil
import adsk
import json
import utilities

######################## File/Folder Utilities ################################
def find_fdoc_path(file_path: str, root_folder = None):
    """Find a Fusion document using a file path

    Parameters
    ----------
    file_path : str
        A string that specifies either the relative or absolute path of a dataFile in Fusion. Formatted as:
        "folder/inner_folder/inner_inner_folder/../inner_inner_folder_again/dataFile:version_2"
    root_folder : dataFolder
        The Fusion 360 dataFolder that is used for the starting point of the search. Defaults to the project root folder
        for absolute paths and the activeDocuments parent folder for relative paths.

    Returns
    -------
    d : dataFile
        The dataFile at the specified path

    Raises
    ------
    UserWarning
        Raised when the specified path is not correct.

    Notes
    -----
    Takes a `file_path` string and opens the Fusion API dataFile given that file path using
    the defined `root_folder`. If no root_folder is specified AND it is a relative
    path, defaults to the currently active product's parent folder as the root
    folder. If the root_folder is specified AND it is an absolute path, the
    root folder is set to the active project's root folder.
    If the root folder IS set, the file path is treated as a relative path to the
    set root folder.

    This will work much faster the closer the desired file is to the
    root_folder. Therefore you should try as much as possible to give a short
    folder path and a specific root folder. The document object is then returned.

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
        raise UserWarning("Version numbering is ambiguous, {} is not a proper "
        "version name".format(''.join(d_desired[1:])))

    # dig into the final folder before hitting the document
    if len(fp_list) > 1:
       for f_name in fp_list[0:len(fp_list)-1]:
           if f_name == "..":
               root_folder = root_folder.parentFolder
           root_folder = find_dataFolder(root_folder, f_name)

    # search through the datafiles to find the right one.
    d = find_dataFile(root_folder, d_name)

    # if no colens, open the datafile directly to the latest version.
    # Otherwise, open to the version specified
    if d_version:
        d = find_version(d,d_version)

    return d

def find_version(data_file, version_number):
    """Find the version of a dataFile from a version number

    Parameters
    ----------
    data_file : dataFile
        A Fusion 360 dataFile that contains the desired version
    version_number : int
        The version number of the returned dataFile

    Returns
    -------
    d : dataFile
        The dataFile of the particular version specified

    Raises
    ------
    UserWarning
        Raised when cannot find the version.

    """
    versions = data_file.versions
    for i in range(versions.count):
        d_potential = versions.item(i)
        if d_potential:
            if d_potential.versionNumber == version_number:
                return d_potential

def find_dataFile(data_folder, data_file_name):
    """Finds the dataFile in the dataFolder. Will not search within subfolders.

    Parameters
    ----------
    data_folder : dataFolder
        A Fusion 360 dataFolder that contains the desired dataFile
    data_file_name : str
        The name of the returned dataFile

    Returns
    -------
    d : dataFile
        The dataFile of the particular name specified

    Raises
    ------
    UserWarning
        Raised when cannot find the dataFile.

    """
    files = data_folder.dataFiles
    for i in range(files.count):
        df = files.item(i)
        if df.name == data_file_name:
            return df
        else:
            raise UserWarning("The dataFile {} was not found in the folder {}".format(data_file_name, data_folder.name))

def find_dataFolder(parent_dataFolder, dataFolder_name):
    """Finds a dataFolder within a dataFolder. Will not search within subfolders.


    Finds the dataFile in the dataFolder. Will not search within subfolders.

    Parameters
    ----------
    parent_dataFolder : dataFolder
        A Fusion 360 dataFolder that contains the desired dataFolder
    dataFolder_name : str
        The name of the returned dataFolder

    Returns
    -------
    d : dataFolder
        The dataFolder of the particular name specified

    Raises
    ------
    UserWarning
        Raised when cannot find the dataFolder.

    """
    df = parent_dataFolder.dataFolders.itemByName(dataFolder_name)
    if df:
        return df
    else:
        raise UserWarning("The dataFolder {} was not found in the folder {}".format(dataFolder_name, parent_dataFolder.name))



def open_template(file_path:str, target_component=None):
    """Opens an f3d file.

    This will use a file_path to open a Fusion Archive file.

    Parameters
    ----------
    file_path : str
        A string that specifies where on the computer the f3d file lives. A relative path is considered relative to the
        archives folder within the repo. An absolute path is absolute to the root of the computer.
    target_component : Component, optional
        The component that the archive file will be inserted into. Defaults to a new Design

    Returns
    -------
    Returns nothing if failed, Document of new file if target_component not selected, and Component
    of the new component if target_component is selected.

    """
    fp_list = file_path.split("/")

    # location assumed based on relative path rules
    if not fp_list[0] == '':
        file_path = ut.abs_path("archives/"+file_path)

    app = adsk.core.Application.get()
    import_manager = app.importManager
    try:
        import_options = import_manager.createFusionArchiveImportOptions(file_path)
    except:
        raise UserWarning("Unable to find the .f3d archive at {}.".format(file_path))
    if target_component:
        return import_manager.importToTarget(import_options, target_component)
    else:
        return import_manager.importToNewDocument(import_options)


def save_fdoc_online(fdoc, folder, name):
    """
    Saves the fusionDocument fdoc in the specified dataFolder folder with the
    specified name and then opens the modified document and closes the fdoc template
    """
    fdoc.saveAs(name, folder, '', '')
    adsk.doEvents()
