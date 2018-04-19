import adsk
import traceback

from . import adsk_utilities as a_ut
from . import utilities as path_ut
from .. import utils
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
    assem_path = path_ut.abs_path("test_data/test_wheel_box_orig.sat")
    params_path_orig = path_ut.abs_path("test_data/wheel_and_box_orig.yaml")
    params_path_new = path_ut.abs_path("test_data/wheel_and_box.yaml")
    params_path_output = path_ut.abs_path("test_data/new_wheel_and_box.yaml")

    update_args = {
        'root_component': root_component,
    }

    fdoc = a_ut.open_sat_template(assem_path, root_component)
    aide_draw.load_yaml_and_update_params(params_path_new, root_component, update_args)
    aide_draw.save_yaml(params_path_output, root_component)
    assert utils.compare_yamls(params_path_orig, params_path_output) == False

def run_tests():
    basic_test()
