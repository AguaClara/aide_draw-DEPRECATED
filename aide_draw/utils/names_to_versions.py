import adsk.core, adsk.fusion

def build_names_to_versions_helper(occurrences, input_dict):    
    """
    Helper used to build dictionary mapping component names used in
    parameters file to component names used in Fusion 360, e.g.
    testAssem -> testAssem v14

    Args:
        occurrences: Occurrences object used to access child occurrences
        input_dict: Python dict to update with new key-value pairs

    Returns:
        Dictionary containing the completed mapping of param component names to Fusion component names

    Raises:

    Examples:
        ?
    """
    for i in range(0, occurrences.count):
        occ = occurrences.item(i)
        full_name = occ.name
        name_parts = full_name.split(" ")
        name_only = name_parts[0]
        input_dict[name_only] = full_name

        if occ.childOccurrences: #if there are more levels of assemblies to recurse through
            child_dict = build_names_to_versions_helper(occ.childOccurrences, input_dict)
            child_copy = child_dict.copy()
            input_dict.update(child_copy)

    return input_dict


def build_names_to_versions(root_component):    
    """
    Builds a mapping from parameter file component names to versioned Fusion 360
    component names, e.g. testAssem -> testAssem v14

    Args:
        root_component: Root component of Fusion 360 assembly

    Returns:
        Dictionary mapping parameter component names to Fusion 360 component names

    Raises:

    Examples:
        ?
    """
    input_dict = {}
    full_name = root_component.name
    name_parts = full_name.split(" ")
    name_only = name_parts[0]
    input_dict[name_only] = full_name

    occurrences = root_component.occurrences.asList
    return build_names_to_versions_helper(occurrences, input_dict)
