import adsk.core, adsk.fusion, traceback
import sys, os
import json

from .. import yaml

def build_orig_params_helper(root_component):
    ret = {}
    if hasattr(root_component, "occurrences"):
        for i in range(root_component.occurrences.count):
            occurrence = root_component.occurrences.item(i)
            full_name = occurrence.name
            name_parts = full_name.split(" ")
            name_only = name_parts[0]
            ret[name_only] = build_orig_params_helper(occurrence.component)

    params = {}
    for i in range(root_component.parentDesign.userParameters.count):
        param = root_component.parentDesign.userParameters.item(i)
        params[param.name] = param.expression

    if root_component.parentDesign.userParameters.count > 0:
        ret["dp"] = params

    return ret

def build_orig_params(root_component):
    result = build_orig_params_helper(root_component)
    name = root_component.name.split(" ")[0]
    return { name : result }

def create_yaml(ui, root_component): # TODO THIS WILL BREAK
    yamlSaveDialog = ui.createFileDialog()
    yamlSaveDialog.isMultiSelectEnabled = False
    yamlSaveDialog.title = "Specify yaml save file"
    yamlSaveDialog.filter = 'yaml files (*.yaml)'
    yamlSaveDialog.filterIndex = 0
    saveDialogResult = yamlSaveDialog.showSave()
    if saveDialogResult == adsk.core.DialogResults.DialogOK:
        yaml_out_file = yamlSaveDialog.filename
    else:
        return

    original_params = build_orig_params(root_component)

    with open(yaml_out_file, 'w+') as yamlOut:
        yaml.dump(original_params, yamlOut, default_flow_style=False)

def count_yaml(yaml, cur_count):
    for k,v in yaml.items():
        if k != "dp" and k != "hp" and isinstance(v, dict):
            cur_count = cur_count + 1
            cur_count = count_yaml(v, cur_count)

    return cur_count
