import adsk.core, adsk.fusion
import json

from .. import utils
from .. import yaml
from .. import build_params

def change_param_value(open_doc, param_name, param_value, update_args):
    """
    Updates a Fusion 360 component's user parameter corresponding to
    param_name with expression param_value. This is a helper function called
    by the update_user_params function.

    Args:
        param_name: Name of user parameter to update
        param_value: New expression for user parameter

    Returns:
        None

    Raises:
        ?

    Examples:
        ?
    """
    ui = update_args['ui'] #user interface
    component = update_args['curr_component']

    if component.features.itemByName(param_name): #if the parameter is a feature
        #AIDE design decision: if parma value is 0, suppress the feature
        if param_value == '0':
            component.features.itemByName(param_name).isSuppressed = True
        #make sure it's unsupressed if not 0
        else:
            if component.features.itemByName(param_name).isSuppressed:
                component.features.itemByName(param_name).isSuppressed = False

    else: #normal parameter case
        try:
            #parameter update happens here
            params = open_doc.design.allParameters
            params.itemByName(param_name).expression = param_value

            #print information, only seen if code run via Python, instead of from Fusion
            print("Updated component: {} {}={}".format(open_doc.name, param_name, param_value))

        except AttributeError: #parameter doesn't exist in the open document
            ui.messageBox("Failed to update params: Parameter {}={} for component {} does not exist".format(
            param_name, param_value, open_doc.name))
            # TODO should we fail the whole build if a param doesn't match or just continue? ask team

def update_user_params(root_component, yaml_dict, update_args):
    """
    Updates a Fusion 360 assembly, with root_component as the root
    component, by setting the user parameters using the structure in yaml_dict,
    with name mappings in component_names_to_versions. This is a recursive helper function
    for the update_fusion function.

    Args:
        root_component: Root component of Fusion 360 assembly
        yaml_dict: Python dict built from yaml parameter file specifying which parameters to change
        update_args: Dictionary with update materials

    Returns:
        None

    Raises:
        ?

    Examples:
        ?
    """
    app = update_args['app']
    #dictionary to map componenet name (how it's referenced in yaml) to component name + version (name in Fusion)
    component_names_to_versions = update_args['component_names_to_versions']

    #show progress bar
    if 'progressDialog' in update_args:
        cur_progress = update_args['cur_progress']
        progressDialog = update_args['progressDialog']
        progressDialog.show('Progress Dialog', 'Percentage: %p, Current Value: %v, Total steps: %m', 0, progressDialog.maximumValue, 1)
        progressDialog.progressValue = cur_progress

        #update progress, to show next time progressDialog.show() is called
        update_args['progressDialog'] = progressDialog
        update_args['cur_progress'] = cur_progress + 1

    assembly_doc = app.activeDocument #outer assembly
    parent_doc = root_component.parentDesign.parentDocument #document of the component whose parameter is being updated
    component_doc = adsk.fusion.FusionDocument.cast(parent_doc) #same as parent_doc, but a FusionDocument object instead of Document

    for prop in list(yaml_dict.keys()):
        if prop == "dp": #design parameters
            # modify this component's params
            open_doc = app.documents.open(component_doc.dataFile, False) #open file holding the design

            user_params = yaml_dict[prop]
            for param in list(user_params.keys()):
                expression = user_params[param]
                update_args['curr_component'] = root_component
                change_param_value(open_doc, param, expression, update_args)

            if open_doc.isModified: #save if modified
                print("Modified: " + component_doc.name)
                open_doc.save("Modified: " + open_doc.name + " from AIDE")

            if open_doc.name != assembly_doc.name: #close if not the outer assembly
                open_doc.close(True)

            assembly_doc.activate() #make sure outer level assembly is activated
        elif prop == "hp": #ignore hydraulic parameters
            break
        else:
            # it's a component, not user params, continue recursively calling update_user_params
            component_name = prop
            true_name = component_names_to_versions[component_name]
            working_occurrence = root_component.occurrences.asList.itemByName(true_name)

            if working_occurrence:
                # that means we are not operating at the highest level, i.e. it's a child occurrence
                update_user_params(working_occurrence.component, yaml_dict[prop], update_args)
            else:
                # it's the root component
                update_user_params(root_component, yaml_dict[prop], update_args)

def update_fusion(update_args, yaml_file_path=None):
    """
    Updates a Fusion 360 assembly, with root_component as the root
    component, by setting the user parameters using the structure in yaml_dict,
    with name mappings in component_names_to_versions

    Args:
        update_args: Dictionary with update materials

    Returns:
        None

    Raises:
        ?

    Examples:
        ?
    """
    root_component = update_args['root_component']
    ui = update_args['ui']

    component_names_to_versions = utils.build_names_to_versions(root_component)
    print(json.dumps(component_names_to_versions))

    # Takes in a yaml parameter file to change the parameters in assembly file into
#    if not yaml_ifile_path:
#        yamlFileDalog = ui.createFileDialog()
#        yamlFileDialog.isMultiSelectEnabled = False
#        yamlFileDialog.title = "Specify yaml parameter file"
#        yamlFileDialog.filter = 'yaml files (*.yaml)'
#        yamlFileDialog.filterIndex = 0
#        takeDialogResult = yamlFileDialog.showOpen()
#        if takeDialogResult == adsk.core.DialogResults.DialogOK:
#            yaml_file_path = yamlFileDialog.filename
#        else:
#            return

    yamlFileDialog = ui.createFileDialog()
    yamlFileDialog.isMultiSelectEnabled = False
    yamlFileDialog.title = "Specify yaml parameter file"
    yamlFileDialog.filter = 'yaml files (*.yaml)'
    yamlFileDialog.filterIndex = 0
    takeDialogResult = yamlFileDialog.showOpen()
    if takeDialogResult == adsk.core.DialogResults.DialogOK:
        yaml_file_path = yamlFileDialog.filename
    else:
        return

    assembly_params = build_params.build_orig_params(root_component) #save current parameters into yaml
    count = build_params.count_yaml(assembly_params, 0) #count number of files in assembly (for progress bar)

    progressDialog = ui.createProgressDialog()
    progressDialog.cancelButtonText = 'Cancel'
    progressDialog.isBackgroundTranslucent = False
    progressDialog.isCancelButtonShown = True
    progressDialog.maximumValue = count

    update_args['progressDialog'] = progressDialog

    utils.unlock_assem(root_component) #remove aide_draw_lock rigid group from assembly

    with open(yaml_file_path, "r") as f:
        doc = yaml.load(f)
        update_args['component_names_to_versions'] = component_names_to_versions
        update_user_params(root_component, doc, update_args)

    utils.lock_assem(root_component) #add aide_draw_lock rigid group to assembly

    #progressDialog.show('Progress Dialog', 'Percentage: %p, Current Value: %v, Total steps: %m', 0, count, 1)

    #utils.lock_assem(root_component)
