#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

from . import build_params
from . import update_params
from . import utils
from . import test
from . import yaml

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

_handlers = []

def load_yaml_and_update_params(path, root_component, update_args={}):
    """
    This function takes in a path to a yaml file as well as a root_component, which
    is the fusion component that is being updated. It then updates the component
    by updating the component's parameters with the new data from the yaml.

    Args:
        path: string
        root_component: ?

    Returns:

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
    Fusion 360 entry point. This script updates the user parameters
    of a Fusion 360 assembly using the structure specified in the yaml file
    located at the hard-coded file path.

    Args:
        context: Fusion 360 context

    Returns:

    Raises:

    Examples:
        ?
    """

    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('No active Fusion design', 'No Design')
            return
        # Set up gui

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = ui.commandDefinitions.addButtonDefinition('saveYaml', 'Save Parameters', 'Save parameters to a yaml', 'icons/saveYaml')
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDEButton = createPanel.controls.addCommand(cmdDef)

        cmdDef2 = ui.commandDefinitions.addButtonDefinition('loadYaml', 'Update Parameters', 'Update parameters from a yaml', 'icons/loadYaml')

        createPanel2 = ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDEButton2 = createPanel2.controls.addCommand(cmdDef2)

        # Connect to the command created event.
        onCommandCreated = saveYamlCreated()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        onCommandCreated2 = loadYamlCreated()
        cmdDef2.commandCreated.add(onCommandCreated2)
        _handlers.append(onCommandCreated2)

        if context['IsApplicationStartup'] == False:
            ui.messageBox('The "AIDE DRAW Tool" has been added\nto the CREATE panel of the MODEL workspace.')

        test.run_tests()

    except:
        print(traceback.format_exc())

def stop(context):
        """
        This function stops the Fusion 360 context.

        Args:
            context: Fusion 360 context

        Returns:

        Raises:

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
    Saves the Yaml that's created?

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:

    Raises:

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
            onExecute = saveYamlExecute()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class loadYamlCreated(adsk.core.CommandCreatedEventHandler):
    """
    Loads the Yaml that's created?

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:

    Raises:

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
            onExecute = loadYamlExecute()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class saveYamlExecute(adsk.core.CommandEventHandler):
    """
    Saves the Yaml that's executed?

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:

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
            build_params.create_yaml(ui, root_component)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class loadYamlExecute(adsk.core.CommandEventHandler):
    """
    Loads the Yaml that's executed?

    Args:
        adsk.core.CommandCreatedEventHandler: ?

    Returns:

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

            count = build_params.count_yaml(assembly_params, 0)

            progressDialog = ui.createProgressDialog()
            progressDialog.cancelButtonText = 'Cancel'
            progressDialog.isBackgroundTranslucent = False
            progressDialog.isCancelButtonShown = True
            progressDialog.maximumValue = count

            update_args = {
                'root_component': root_component,
                'ui': ui,
                'app': app,
                'progressDialog': progressDialog,
                'cur_progress': 0
            }
            update_params.update_fusion(update_args)
            print("HELLO WORLD")
            progressDialog.show('Progress Dialog', 'Percentage: %p, Current Value: %v, Total steps: %m', 0, count, 1)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
