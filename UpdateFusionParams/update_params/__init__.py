from . import update_params

def change_param_value(root_component, param_name, param_value):
    return update_params.change_param_value(root_component, param_name, param_value)

def update_user_params(root_component, yaml_dict, update_args):
    return update_params.update_user_params(root_component, yaml_dict, update_args)

def update_fusion(update_args):
    return update_params.update_fusion(update_args)
