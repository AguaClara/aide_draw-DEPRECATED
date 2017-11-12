import adsk


def start(fdoc, params_desired):
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
