#Author-Ethan Keller
#Description-aide is a simple implementation of the aide_ecosystem program
"""
This is the entry point to the AIDE add in. This will be part of the aide_gui
system and will setup the aide_gui object. That object is a singleton that
will in turn point directly to the fusion ui and provide additional features
such as nested template creation monitoring and reporting.

Any imported libraries need to be imported with relative
imports like: `from . import aide_draw` where aide_draw is within the addin path.
Therefore we can only use custom libraries with relative imports.
"""

import adsk.core, adsk.fusion, adsk.cam, traceback
import warnings
from . import aide_draw, aide_gui
from . import utilities as ut


# Global variables:
_app = None
_ui  = None

def run(context):
    """
    This function runs when the plugin is started. It's only use is to
    import necessary files and create the button that is the entry point to the
    aide ecosystem.
    """

    try:

        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        aide_gui.launch_aide_panel()
        #aide_draw.open_fdoc("/tests/folder1/folder2/folder3/test_cube")
        json_path = "/Users/ethankeller/git_repos/AguaClara/AIDE/aide_draw/tests/json/test_cube.json"
        app = adsk.core.Application.get()
        fdoc_dict = ut._load_json(json_path)
        project = app.data.activeProject
        name = list(fdoc_dict.keys())[0]
        fdoc_target_folder = project.rootFolder.dataFolders.add(name + " " + ut.str_time())
        fdoc_template = app.activeDocument
        aide_draw.draw_fdoc(fdoc_dict[name], fdoc_template, fdoc_target_folder)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
