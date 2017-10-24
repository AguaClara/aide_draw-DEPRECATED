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
json_path = "/Users/ethankeller/git_repos/AguaClara/AIDE/aide_draw/tests/data/test_pyramid2.json"

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
            fdoc_target_folder = project.rootFolder.dataFolders.add("Results")
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
        
def open_dataFile(dataFile):
    """
    Opens the dataFile
    """
    adsk.core.Application.get().documents.open(dataFile)
    
def find_dataFile(dataFolder, dataFile_name):
    """
    Finds the dataFile in the dataFolder. Will not search within subfolders.
    """
    for i in range(dataFolder.dataFiles.count):
        df = dataFolder.dataFiles.item(i)
        if df.name == dataFile_name:
            return df
        else:
            raise ValueError("The dataFile %s was not found in the folder %s", dataFile_name, dataFolder.name)
          
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
    if 'components' in params_desired:
        for component in params_desired['components']:
            comp_params_desired = params_desired['components'][component]
            params = fdoc.design.allComponents.itemByName(component).modelParameters
            # Loop through the parameters  dictionary in a single component
            for key in comp_params_desired:
                param_desired = comp_params_desired[key]
                param_actual = params.itemByName(key)
                try:
                    param_actual.expression = str(param_desired['magnitude']) + ' ' + \
                        param_desired['units']
                except:
                    raise ValueError(" Trying to change the param: %s but that" 
                    "parameter that doesn't exist. Make sure the parameter"
                    "defined in the JSON is also defined in the Fusion template.", key, component)
            
    
    

def _load_json(file_path):
    """
    This should safely load jsons, ensuring jsons conform to AIDE standards and throw an error otherwise.
    simplest implementation possible right now:
    """
    return json.load(open(file_path))


def _find_api_dataFile(file_path: str, root_folder = False):
    """
    Takes a file path string and returns the Fusion API dataFile given that file path using
    the defined root_folder. If the root_folder is not assigned, this can handle relative paths and absolute paths, 
    where the relative root location defaults to the current active document's parent folder, and the absolute defaults 
    to the active project's root folder. User override is also possible.
    Relative file_path that returns a dataFile looks like: "folder1/folder2/datafile_name" 
    Absolute file_path that returns a dataFile looks like: "/folder1/folder2/datafile_name"
    """

    fp_list = file_path.split["/"]

    # absolute path. Set root as project folder
    if fp_list[0] == '':
        root_folder = adsk.core.Application.get().activeProject.dataFolders
    d_desired = fp_list[len(fp_list-1)]

    # dig into the final folder before hitting the document
    if len(fp_list[0]) > 1:
       for f in fp_list[0:len(fp_list)-2]:
        if root_folder:
            root_folder = root_folder.dataFolders.itemByName(f)
        else:
            raise ValueError("%s is not a correct folder name", f)

    # search through the datafiles to find the right one.
    d = None
    i = 0
    while i < root_folder.dataFiles.count and not d:
        d_potential = root_folder.dataFiles[i]
        if d_potential:
            if d_potential.name == d_desired:
                d = d_potential
        else:
            raise ValueError("No such dataFile %s exists", d)
        i += 1

    return d_desired



    # if no colens, return the datafile directly. Otherwise, look along the object path (op)
    op = d_desired.split(":")
    if len(op) == 1 :
        return d_desired
    else:
        # Somehow use exec to find the correct object.
        return 0 

def _find_api_object(object_path: str, root_object = False):
    """
    Takes a object path string and returns the Fusion API dataFile given that file path using
    the defined root_object. If the root_object is not assigned, this can handle relative paths and absolute paths, 
    where the relative root location defaults to the current active edit object, and the absolute defaults 
    to the active project's root folder. User override is also possible.
    object_path that returns a sketch object looks like: "sketchCurves:sketchCircles:floc_out" 
    Please see the fusion object map and API to see the different type of objects.
    """