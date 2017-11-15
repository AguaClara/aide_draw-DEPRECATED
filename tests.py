"""
This is the testing module. In it, you will find functions to put directly in
the "run" function of the aide app. You'll need to comment out everything else
in the "run" function, and just paste the function call of the test you are
performing directly in it. Each test includes instructions in it's docstring

**Note**
Because this library involves the Fusion API, it is
difficult to use a unit testing framework (the setup and teardown would be
prohibitively extensive.) There must be some better way to test this, but not
yet.
"""

import adsk.core, adsk.fusion, adsk.cam, traceback
import warnings
import os, sys
from . import aide_draw, aide_gui
from . import utilities as ut
import json

def setup():
    """
    responsible for doing the mundane job of setting up the module's global
    namespace with useful items for easy reference by the various tests.
    This function has the various assignments:
    app : the application
    ui : the ui
    fdoc : the active fusion document
    root_folder : the root folder of the project
    active_folder : the folder containing the active fdocs
    """
    global app, ui, project, fdoc, root_folder, active_folder
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        project = app.data.activeProject
        fdoc = app.activeDocument
        root_folder = project.rootFolder
        active_folder = fdoc.dataFile.parentFolder
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def test_cube():
    """
    Import tests (from . import tests.tests) into the main aide.py module,
    put test_cube() within the run function, open the test_cube.f3d from the
    tests/templates folder, and run the aide add-in. The cube should be changed
    according to the parameters specified within test_cube.json in tests/json
    """
    setup()
    json_path = "test_data/json/test_cube.json"
    fdoc_dict = ut._load_json(ut.abs_path(json_path))
    name = list(fdoc_dict.keys())[0]
    fdoc_target_folder = project.rootFolder.dataFolders.add(name + " " + ut.str_time())
    aide_draw.draw_fdoc(fdoc_dict[name], fdoc, fdoc_target_folder)
    ui.messageBox("The test passed if a newly sized cube is now open and saved"
        " to a new folder within the root folder of the project. The parameters"
        " should be: {}".format(fdoc_dict[name]["fgens"][0]["parametrize_template"]["args"]))


def test_folder_creation():
    try:
        setup()
        json_path = "test_data/json/test_folder_creation.json"
        folder_dict = ut._load_json(ut.abs_path(json_path))
        folder_name = ut.str_time()
        folder_dict_with_refs = \
            aide_draw.create_folder_structure(folder_dict, root_folder.dataFolders.add(folder_name))
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))        
    
    
def test_holding_folder_refs_in_dictionaries():
    """
    Tests the idea of holding a ref to a dataFolder within a dictionary. This 
    creates a folder, puts it in the dictionary, and then attempts to open 
    that folder.
    """
    setup()
    folder = root_folder.dataFolders.add("This is a dictionary folder! "+ ut.str_time())
    d = {folder.name:folder}
    ui.messageBox(d[folder.name].classType())