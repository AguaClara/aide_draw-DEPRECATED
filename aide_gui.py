######################################### GUI FUNCTIONS #######################

import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import warnings
import aide_draw
import utilities as ut

_handlers = []
json_path = "/Users/ethankeller/git_repos/AguaClara/AIDE/aide_draw/tests/json/test_cube.json"


def get_ui():
    """
    Get the global GUI if it is defined, otherwise get it from the current
    application.
    """
    global _ui
    try:
        return _ui
    except:
        return adsk.core.Application.get().userInterface


def select_json():
    """
    Have user select JSON and return JSON path.
    """
    ui = get_ui()
    # Have the table file selected.
    dialog = ui.createFileDialog()
    dialog.filter = 'json (*.json)'
    dialog.initialDirectory = os.path.dirname(os.path.realpath(__file__))
    if dialog.showOpen() != adsk.core.DialogResults.DialogOK:
        return
    return dialog.filename

def launch_aide_panel():
    """
    Creates a panel in the ui.
    """
    ui = get_ui()
    # Get the existing command definition or create it if it doesn't already exist.
    cmdDef = ui.commandDefinitions.itemById('aideInputs')
    if not cmdDef:
        cmdDef = ui.commandDefinitions.addButtonDefinition('aideInputs', 'AIDE Inputs', 'Select various inputs for aide here.')

    # Connect to the command created event.
    onCommandCreated = AideCreatedHandler()
    cmdDef.commandCreated.add(onCommandCreated)
    _handlers.append(onCommandCreated)
    cmdDef.execute()


# Event handler that reacts to any changes the user makes to any of the command inputs.
class AideInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global json_path
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input
            cid = cmdInput.id
            if cid == 'findJson':
                json_path = select_json()
                cmd_inp = inputs.itemById('jsonPath')
                if cmd_inp:
                    cmd_inp.text = json_path
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. TODO this should
# close and clean up the command dialog.
class AideDestroyHandler(adsk.core.CommandEventHandler):
    """
    This runs the AIDE draw function using the path specified.
    """
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            get_ui().messageBox('running fdoc')
            app = adsk.core.Application.get()
            fdoc_dict = aide_draw._load_json(json_path)
            project = app.data.activeProject
            fdoc_target_folder = project.rootFolder.dataFolders.add(ut.str_time())
            fdoc_template = app.activeDocument
            aide_draw.draw_fdoc(fdoc_dict, fdoc_template, fdoc_target_folder)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class AideCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)
            # Connect to the command destroyed event.
            onDestroy = AideDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
            # Connect to the input changed event.
            onInputChanged = AideInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # Create the full panel if this is the aideInputs box
            if cmd.parentCommandDefinition.id == 'aideInputs':
                # Get the CommandInputs collection associated with the command.
                inputs = cmd.commandInputs
                # Create bool value input with button style that can be clicked.
                inputs.addBoolValueInput('findJson', 'Select Json', False, 'resources/button', True)
                inputs.addTextBoxCommandInput('jsonPath', 'Path of Json selected', 'No json selected', 2, True)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Stopping addin')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
