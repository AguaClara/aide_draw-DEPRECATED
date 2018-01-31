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

import time
import adsk.core, adsk.fusion, adsk.cam, traceback
import warnings
import os, sys
import aide_draw, aide_gui, generate_json
import utilities as ut
import json
import importlib
sys.path.append(ut.abs_path("fgens"))
import cylindrical_pattern_feature
import lfom

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
    app = adsk.core.Application.get()
    ui = app.userInterface
    project = app.data.activeProject
    fdoc = app.activeDocument
    root_folder = project.rootFolder
    active_folder = fdoc.dataFile.parentFolder

def test_cylindrical_pattern_feature():
    importlib.reload(cylindrical_pattern_feature)
    setup()
    test_hole_list = [7,4,3]
    cylindrical_pattern_feature.start(test_hole_list, 23, "lfom_hole", fdoc)


def test_lfom():
    importlib.reload(lfom)
    importlib.reload(cylindrical_pattern_feature)
    setup()
    test_hole_list = [8,7,1,5,1]
    lfom.start(test_hole_list, 23, "lfom_hole_1", "lfom_hole_2", "seed_1", "seed_2", fdoc)
