#Author-Ethan Keller
#Description-aide is a simple implementation of the aide_ecosystem program
"""
This is the entry point to the AIDE add in. This will be part of the aide_gui
system and will setup the aide_gui object. That object is a singleton that
will in turn point directly to the fusion ui and provide additional features
such as nested template creation monitoring and reporting. 

Unfortunately, any imported libraries need to be imported locally according 
to this detailed post:
https://forums.autodesk.com/t5/fusion-360-api-and-scripts/to-install-python-modules/td-p/5777176
Therefore we can only use custom libraries with relative imports.
"""

import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import warnings
import json
import html
from time import gmtime, strftime

# We have to manually add the plugin folder to the path so we can import the 
# various files used in the plugin.
#my_addin_path = os.path.dirname(os.path.realpath(__file__))
#if not my_addin_path in sys.path:
#    sys.path.append(my_addin_path) 
#import aide_draw as draw


# Global variables:
_app = None
_ui  = None
_handlers = []
json_path = "/Users/ethankeller/git_repos/AguaClara/AIDE/aide_draw/tests/json/test_cube.json"

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
        launch_aide_panel()
    
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



######################################### GUI FUNCTIONS #######################

def get_ui():
    """
    Get the global GUI if it is defined, otherwise get it from the current 
    application.
    """
    global _ui
    if _ui:
        return _ui
    else:
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
    
def test_aide_panel():
    """
    opens a testing panel that allows you to type and execute any python code/
    function calls directly within this environment. Just replace the call to 
    launch_aide_panel() with test_aide_panel() in the run function.
    
    """
    ui = get_ui()
    # Get the existing command definition or create it if it doesn't already exist.
    cmdDef = ui.commandDefinitions.itemById('testInputs')
    if not cmdDef:
        cmdDef = ui.commandDefinitions.addButtonDefinition('testInputs', 'Test Inputs', 'Type in a python command and execute it')

    # Connect to the command created event.
    onCommandCreated = TestCreatedHandler()
    cmdDef.commandCreated.add(onCommandCreated)
    _handlers.append(onCommandCreated)    
    cmdDef.execute()
    
# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class TestCreatedHandler(adsk.core.CommandCreatedEventHandler):
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
            testKeyUp = TestKeyUpHandler()
            cmd.keyUp.add(testKeyUp)
            #cmd.inputChanged.add(onInputChanged)
            _handlers.append(testKeyUp) 
    
            if cmd.parentCommandDefinition.id == 'testInputs':
                # Get the CommandInputs collection associated with the command.
                inputs = cmd.commandInputs
                # Create an editable textbox input.
                inputs.addTextBoxCommandInput('test_textBox', 'Test statement', 'Type in a valid python command and hit enter', 2, False)   
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
class TestKeyUpHandler(adsk.core.KeyboardEventHandler):
    """
    This is run when the enter key is hit on the keyboard. The idea is to 
    run whatever you type in simply by hitting enter.
    """
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.KeyboardEventArgs.cast(args)
            cmd = adsk.core.Command.cast(eventArgs.firingEvent.sender)
            if eventArgs.keyCode == 16777220:
                textBox = adsk.core.TextBoxCommandInput.cast(cmd.commandInputs.itemById('test_textBox'))
                to_run = html.unescape(textBox.text)
                get_ui().messageBox('Going to run: ' + str(to_run))
                eval(to_run)
                
        except:
            get_ui().messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
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
            fdoc_dict = _load_json(json_path)
            project = app.data.activeProject 
            fdoc_target_folder = project.rootFolder.dataFolders.add(str_time())
            fdoc_template = app.activeDocument
            draw_fdoc(fdoc_dict, fdoc_template, fdoc_target_folder)
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
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
            
def str_time():
    """
    Return the current time in a human-readable string
    """
    return strftime("%Y-%m-%d %H_%M_%S", gmtime())
    
def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Stopping addin')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
            

################################ DRAW FUNCTIONS ###############################

def _save(fdoc, folder, name):
    """
    Saves the fusionDocument fdoc in the specified dataFolder folder with the 
    specified name and then opens the modified document and closes the fdoc template
    """
    fdoc.saveAs(name, folder, '', '')
    adsk.doEvents()
    
def draw_fdoc(fdoc_dict, fdoc_template, fdoc_target_folder):
    """
    Draws a single fdoc. All the fdoc components are in the root as a list 
    (parameters, components, name, template)
    """
    if 'parameters' in fdoc_dict:
        _size(fdoc_template, fdoc_dict['parameters'])
        _save(fdoc_template, fdoc_target_folder, fdoc_dict['name'])
          
def _draw_recursive_json(folder_dict, fdoc_folder, fdoc_target_folder):
    """
    Takes a component AIDE-compliant dictionary and draws
    all child component components. Passed in is the fdoc_folder that the 
    current layer in the dictionary is referring to. 
    and then re-adds them to parents and saves all
    in an organized folder hierarchy. The first folder is assumed to be the one
    you are in.
    """
    drawn_fdocs = []
    
    # Create all the child folders and make recursive calls on folders:
    if 'folders' in folder_dict and len(folder_dict['folders']) > 0:
        for name in folder_dict['folders']:
            child_fdoc_dict = folder_dict['folders'][name]
            child_fdoc_target_folder = fdoc_target_folder.dataFolders.add(name)
            child_fdoc_folder = fdoc_folder.dataFolders.itemByName(name)
            if not child_fdoc_folder:
                raise ValueError("The file specified in json doesn't exist.") 
             # Recursive call with the new fdoc folder
            drawn_fdocs = drawn_fdocs.extend(_draw_recursive_json(child_fdoc_dict, child_fdoc_folder,
                                 child_fdoc_target_folder))  
                             
    # Loop through all the files in the current folder. This takes a while,
    # so make sure to do it only once.
    for i in range(fdoc_folder.dataFiles.count):
        datafile_potential_template = fdoc_folder.dataFiles.item(i)
        # Get all defined fdoc_dicts for fdocs using this template
        fdoc_template_dict = {k: v for k, v in folder_dict['fdocs'].items() if v['template'] == datafile_potential_template.name}
        if len(fdoc_template_dict) > 0:
            # We know to use this template
            datafile_template = datafile_potential_template
            # Loop through all iterations of this fdoc defined in the dict. 
            for fdoc_dict in fdoc_template_dict:
                # Make sure sizing parameters are found
                if 'parameters' in fdoc_dict:
                    # Open the fdoc_template for sizing
                    fdoc_template = adsk.core.Application.get().documents.open(datafile_template)
                    _size(fdoc_template, fdoc_dict['parameters'])
                    _save(fdoc_template, fdoc_target_folder, fdoc_dict['name'])
                    drawn_fdocs = drawn_fdocs.append(fdoc_dict['name'])
                else:
                    warnings.warn("Template specified, but no parameters set"
                        "in the fdocs' json. Defaulting to copying the fdoc"
                        "directly.")
    
    # This is the base case, when all that are left are fdocs.
    if 'fdocs' in folder_dict and len(folder_dict['fdocs']) > 0:
        for fdoc in folder_dict['fdocs']:
            # need to create the component
            if 'create' in fdoc:
                _create(fdoc['create'])
                drawn_fdocs = drawn_fdocs.append(fdoc['name'])
    
    return drawn_fdocs

def _create(fdoc):
    """
    This should generate and open an fdoc with the specified creator python file
    """
    return 0

def _size(fdoc, params_desired):
    """
    Takes the param dictionary and a doc to be sized and adjusts all
    the parameters in the document.
    """
    params = adsk.fusion.FusionDocument.cast(fdoc).design.allParameters
    # Loop through the parameters  dictionary in a single component
    for key in params_desired:
        param_desired = params_desired[key]
        param_actual = params.itemByName(key)
        try:
            param_actual.expression = str(param_desired)
        except:
            raise ValueError(" Trying to change the param: {} but that" 
            " parameter doesn't exist. Make sure the parameter"
            " defined in the JSON is also defined in the Fusion template.".format(key))
            

        
######################## File/Folder Utilities ################################
def _load_json(file_path):
    """
    This should safely load jsons, ensuring jsons conform to AIDE standards and throw an error otherwise.
    simplest implementation possible right now:
    """
    return json.load(open(file_path))


def open_fdoc(file_path: str, root_folder = None):
    """
    Takes a file path string and opens the Fusion API dataFile given that file path using
    the defined root_folder. If no root_folder is specified AND it is a relative
    path, defaults to the currently active product's parent folder as the root 
    folder. If the root_folder is specified AND it is an absolute path, the 
    root folder is set to the active project's root folder. 
    If the root folder IS set, the file path is treated as a relative path to the
    set root folder. The root_folder param is a dataFolder
    
    
    Note that this will work much faster the closer the desired file is to the
    root_folder. Therefore you should try as much as possible to give a short
    folder path and a specific root folder. The document object is then returned
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
        raise ValueError("Version numbering is ambiguous, {} is not a proper "
        "version name".format(''.join(d_desired[1:])))

    # dig into the final folder before hitting the document
    if len(fp_list) > 1:
       for f_name in fp_list[0:len(fp_list)-1]:
           root_folder = find_dataFolder(root_folder, f_name)

    # search through the datafiles to find the right one.
    d = None
    d = find_dataFile(root_folder, d_name)
    
    # if no colens, open the datafile directly to the latest version. 
    # Otherwise, open to the version specified
    if d_version:
        d = find_version(d,d_version)
    
    adsk.core.Application.get().documents.open(d)   
    
def find_version(dataFile, version_number):
    """
    Opens the specified version_number of the passed in dataFile
    """
    for i in range(dataFile.versions.count):
        d_potential = dataFile.versions.item(i)
        if d_potential:
            if d_potential.versionNumber == version_number:
                return d_potential

def find_dataFile(dataFolder, dataFile_name):
    """
    Finds the dataFile in the dataFolder. Will not search within subfolders.
    """
    for i in range(dataFolder.dataFiles.count):
        df = dataFolder.dataFiles.item(i)
        if df.name == dataFile_name:
            return df
        else:
            raise ValueError("The dataFile {} was not found in the folder {}".format(dataFile_name, dataFolder.name))
     
def find_dataFolder(parent_dataFolder, dataFolder_name):
    """
    Finds a dataFolder within a dataFolder. Will not search within subfolders.
    """
    df = parent_dataFolder.dataFolders.itemByName(dataFolder_name)
    if df:
        return df
    else:
        raise ValueError("The dataFolder {} was not found in the folder {}".format(dataFolder_name, parent_dataFolder.name))