#Author- Aadil Bhatti, Matan Presberg
#Description- main run file for AIDE_DRAW add-in

#Fusion packages
import adsk.core, adsk.fusion, adsk.cam, traceback

#Packages local to the AIDE_DRAW add-in
from . import build_params
from . import update_params
from . import utils
from . import test
from . import yaml

# Globals
_handlers = [] #store event handlers for buttons

def load_yaml_and_update_params(path, root_component, update_args={}):
    """
    This function takes in a path to a yaml file as well as a root_component, which
    is the fusion component that is being updated. It then updates the component
    by updating the component's parameters with the new data from the yaml.

    Args:
        path: string
        root_component: fusion component being updated. Initially the root component
        of the design.

    Returns:
        None

    Raises:

    Examples:
        ?
    """
    with open(path, "r") as f:
        component_names_to_versions = utils.build_names_to_versions(root_component)
        update_args['component_names_to_versions'] = component_names_to_versions
        update_args['app'] = adsk.core.Application.get()
        update_args['ui'] = update_args['app'].userInterface
        doc = yaml.load(f)

        utils.unlock_assem(root_component)
        update_params.update_user_params(root_component, doc, update_args)
        utils.lock_assem(root_component)

def save_yaml(path, root_component):
    """
    This function takes in a path to a yaml file as well as a root_component, which
    is the fusion component that is being used. It saves the component's
    parameters in the yaml file

    Args:
        path: string
        root_component: ?

    Returns:

    Raises:

    Examples:
        ?
    """
    params = build_params.build_orig_params(root_component)
    with open(path, "w+") as f:
        yaml.dump(params, f, default_flow_style=False)

def run(context):
    """
    Fusion 360 entry point. Called when aide_draw add-in is loaded. This script sets up the aide_draw add-in.
    Sets up 'saveYaml' and 'loadYaml' button.
    'saveYaml' saves all user parameters to a yaml file
    'loadYaml' loads a yaml file and updates all user parameters

    Args:
        context: Fusion 360 context

    Returns:
        None

    Raises:

    Examples:
        ?
    """

    ui = None
    try:

        #variable for Fusion application
        app = adsk.core.Application.get()

        #variable for Fusion 360 user interface
        ui = app.userInterface

        #stores currently open Fusion project into variables
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        if not design:
            ui.messageBox('No active Fusion design', 'No Design')
            return

        ##### Set up gui ####

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = ui.commandDefinitions.addButtonDefinition('saveYaml', 'Save Parameters', 'Save parameters to a yaml', 'icons/saveYaml')
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDEButton = createPanel.controls.addCommand(cmdDef)

        cmdDef2 = ui.commandDefinitions.addButtonDefinition('loadYaml', 'Update Parameters', 'Update parameters from a yaml', 'icons/loadYaml')
        createPanel2 = ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDEButton2 = createPanel2.controls.addCommand(cmdDef2)

        # Connect to the command created event.
        onCommandCreated = saveYamlCreated() #function definition below
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        onCommandCreated2 = loadYamlCreated() #function definition below
        cmdDef2.commandCreated.add(onCommandCreated2)
        _handlers.append(onCommandCreated2)

        if context['IsApplicationStartup'] == False:
            ui.messageBox('The "AIDE DRAW Tool" has been added\nto the CREATE panel of the MODEL workspace.')

        #test.run_tests()

    except:
        print(traceback.format_exc())

def stop(context):
    """
    This function stops the Fusion 360 context. Fusion 360 exit point.
    Called when aide_draw add-in is stopped. Removes aide_draw buttons from the CREATE panel.

    Args:
        context: Fusion 360 context

    Returns:

    Raises:
        None

    Examples:
        ?
    """
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox("aide draw add in no longer active")
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        button = createPanel.controls.itemById('saveYaml')

        #delete aide-draw buttons if they exist
        if button:
            button.deleteMe()
            cmdDef = ui.commandDefinitions.itemById('saveYaml')
            if cmdDef:
                cmdDef.deleteMe()

        button = createPanel.controls.itemById('loadYaml')
        if button:
            button.deleteMe()
            cmdDef = ui.commandDefinitions.itemById('loadYaml')
            if cmdDef:
                cmdDef.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the commandCreated event.
class saveYamlCreated(adsk.core.CommandCreatedEventHandler):
    """
    Called when saveYaml button is created. Connects button to execute handler.

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:

    Raises:
        None

    Examples:
        ?
    """
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False

            # Connect to the command related events.
            onExecute = saveYamlExecute() #function definition below
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class loadYamlCreated(adsk.core.CommandCreatedEventHandler):
    """
    Called when loadYaml button is created. Connects button to execute handler.

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:

    Raises:
        None

    Examples:
        ?
    """
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False

            # Connect to the command related events.
            onExecute = loadYamlExecute() #function definition below
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class saveYamlExecute(adsk.core.CommandEventHandler):
    """
    Called when saveYaml button is pressed. Calls main saveYaml function.

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:
        None

    Raises:

    Examples:
        ?
    """
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)

            root_component = design.rootComponent
            build_params.create_yaml(ui, root_component) #main saveYaml function
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class loadYamlExecute(adsk.core.CommandEventHandler):
    """
    Called when loadYaml button is pressed. Calls main loadYamlfunction.

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:
        None

    Raises:

    Examples:
        ?
    """
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)

            root_component = design.rootComponent
            assembly_params = build_params.build_orig_params(root_component)

            #count = build_params.count_yaml(assembly_params, 0)

#            progressDialog = ui.createProgressDialog()
#            progressDialog.cancelButtonText = 'Cancel'
#            progressDialog.isBackgroundTranslucent = False
#            progressDialog.isCancelButtonShown = True
#            progressDialog.maximumValue = count

            #psuedo-global variables to pass around to functions
            update_args = {
                'root_component': root_component,
                'ui': ui,
                'app': app,
                'progressDialog': None,
                'cur_progress': 0
            }
            update_params.update_fusion(update_args) #main loadYaml function
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
