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
from . import tests
import sys
from . import fgen_tests


# Global variables:
app = None
ui  = None
show_trace = True

def run(context):
    """
    This function runs when the plugin is started. It's only use is to
    import necessary files and create the button that is the entry point to the
    aide ecosystem.
    """

    try:
        global ui
        ui = adsk.core.Application.get().userInterface

        # Tests
        #aide_gui.launch_aide_panel()
        #aide_draw.open_fdoc("/tests/folder1/folder2/folder3/test_cube")
        #tests.test_parametrize_fdoc_cube()
        #tests.test_sync_folder_structure()
        #tests.test_holding_folder_refs_in_dictionaries()
        #tests.test_sync_dict_with_empty_dict()
        #tests.test_sync_dict_with_one_level_dict()
        #tests.test_parametrize_recursive_with_one_level_dict()
        #tests.test_open_template()

        # fgen tests
        # fgen_tests.test_cylindrical_pattern_feature()
        fgen_tests.test_lfom()()

    except BaseException as e:
        if ui:
            e = str(e)
            if show_trace:
                e = str(traceback.format_exc()) + e
            ui.messageBox(e)
