import os
import adsk
import traceback

from .. import build_params
from .. import update_params
from . import adsk_utilities as a_ut
from .. import aide_draw

def setup():
    global app, ui, project, fdoc, root_component, progressDialog
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        project = app.data.activeProject
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        root_component = design.rootComponent

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def basic_test():
    setup()
    assem_path = "test_data/test_wheel_box_orig.sat"
    params_path_orig = "test_data/wheel_and_box_orig.yaml"
    params_path_new = "test_data/wheel_and_box.yaml"

    update_args = {
        'root_component': root_component,
    }

    fdoc = a_ut.open_template(assem_path, root_component)
    aide_draw.load_yaml_and_update_params(params_path_new, root_component, update_args)

def run_tests():
    basic_test()
