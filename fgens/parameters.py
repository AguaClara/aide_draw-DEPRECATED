import adsk

def generate_fdoc(fdoc, fdoc_dict):
    raise UserWarning("The parameters fgen can only update fdocs, not generate them")


def update_fdoc(fdoc, params_desired):
    """Adjusts the fusion document's parameters to the desired expressions

    Parameters
    ----------
    fdoc : FusionDocument
        A FusionDocument in memory.
    params_desired : flat dictionary
        A dictionary without any nesting that has parameter_name:expression key
        -value pairs.

    Returns
    -------
    params_changed : list of strings
        A list of all the parameters that were changed in the given
        FusionDocument.

    Raises
    ------
    UserWarning
        Raised when the parameter specified in 'params_desired' is not available
        in the userParameters of the FusionDocument
    """
    params = adsk.fusion.FusionDocument.cast(fdoc).design.allParameters
    params_changed = []
    # Loop through the parameters  dictionary in a single component
    for param_name in params_desired:
        param_desired = params_desired[param_name]
        param_actual = params.itemByName(param_name)
        if param_actual:
            param_actual.expression = str(param_desired)
            params_changed.append(param_name)
        else:
            raise UserWarning(param_name + " is in the json, but not in the"
                " model. All other values were changed.")
    return params_changed
