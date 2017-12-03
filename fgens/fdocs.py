import adsk.core, adsk.fusion, adsk.cam
import json_keys as keys
import aide_draw

def generate_fdoc(fdoc, fdoc_dict):
    """Calls update_fdoc. Refer to there for documentation.

    """
    if fdoc:
        update_fdoc(fdoc, fdoc_dict)
    else:
        raise UserWarning("The fdoc fgen should go at the end of the fgen list.")

def update_fdoc(fdoc, fdoc_dict):
    """Recursively call the fgen_manager on the various fgens within the fdocs key.

    This will use a dictionary of parameters to specify new designs.

    Parameters
    ----------
    fdoc : Fusion Document
        A Fusion Document, can contain linked documents.
    fdoc_dict : dictionary
        A dictionary that, at the top level, specifies the names of various fdocs that are linked to this fdoc.

    Returns
    -------
    The `(fdoc, fdoc_dict)` tuple of the changed fdoc and fdoc_dict.

    Notes
    -----
    This method is gauranteed to run through all of the fdocs specified within the `fdoc_dict`. Therefore it deals with
    the following four cases like so:

    fdoc cases         | fdoc_dict exists                        | fdoc_dict doesn't exist
    -------------------|-----------------------------------------|------------------------
    fdoc exists        | aide_draw.fgen_manager(fdoc, fdoc_dict) | remove the fdoc from the regerences.
    fdoc doesn't exist | aide_draw.fgen_manager(None, fdoc_dict) | don't change anything



    """
    # Open all documents linked to this document if there are any
    try:
        doc_refs = fdoc.documentReferences
    except:
        doc_refs = None

    # Let's loop through all the specified fdocs as efficiently as possible, hopefully without calling documents, as
    # that makes a server call.

    # This is to keep track of all the fdoc_dicts that are left to be called. Only made if there are children
    child_fdoc_dicts_left_keys = list(fdoc_dict.keys())
    child_fdoc = None

    # If the document references children documents, let's look through those
    if doc_refs:
        # Go through all the referenced children
        for i in range(doc_refs.count):
            doc_ref = doc_refs.item(i)
            child_fdoc_name = doc_ref.dataFile.name
            # A Rogue document is linked! What should we do with it? Other option is just delete it with a confirmation.
            if child_fdoc_name not in fdoc_dict:
                raise UserWarning("The Fusion Document: {} is linked to by {} but is not in the fdoc_dict."
                                  .format(child_fdoc_name, fdoc.name))

            # Need to open the linked document, first try with the dict.
            if keys.FDOC_REF_KEY in fdoc_dict[child_fdoc_name] and fdoc_dict[child_fdoc_name][keys.FDOC_REF_KEY].isValid:
                child_fdoc = fdoc_dict[child_fdoc_name][keys.FDOC_REF_KEY]
                # Activate this doc in the UI, and abort if not able to activate.
                if not child_fdoc.activate():
                    child_fdoc = None
            # If the dict ref doesn't work, open the file from the doc_ref. This is our last choice because it uses a
            # server call
            if not child_fdoc:
                app = adsk.core.Application.get()
                child_fdoc = app.documents.open(doc_ref.dataFile)

            if child_fdoc:
                aide_draw.draw_fdoc(child_fdoc, fdoc_dict[child_fdoc_name])
            else:
                raise RuntimeError("Couldn't open the fdoc: {}".format(child_fdoc_name))

            # child_fdoc has been processed.
            child_fdoc_dicts_left_keys.remove(child_fdoc_name)

    # Run through any additional fdocs that are specified in the dict but not yet created
    for k in child_fdoc_dicts_left_keys:
        aide_draw.draw_fdoc(child_fdoc, fdoc_dict[k])