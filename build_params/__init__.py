from . import build_params

def build_orig_params(root_component):
    return build_params.build_orig_params(root_component)

def create_yaml(ui, root_component):
    return build_params.create_yaml(ui, root_component)

def count_yaml(yaml, cur_count):
    return build_params.count_yaml(yaml, cur_count)
