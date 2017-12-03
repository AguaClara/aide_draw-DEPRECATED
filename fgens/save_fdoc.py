"""
This fgen will save the fgen in the correct folder to keep things organized.
"""

def generate_fdoc(fdoc, fdoc_dict):
    """This will generate a folder in which to save the current fdoc. fdoc is assumed to exist.

    """

    # Make sure that the fdoc exists.
    if not fdoc:
        raise UserWarning("The save_fdoc fgen cannot be called with an empty fdoc. It needs to be called after an fdoc"
                          " is created. Move it to later in the fgen list.")

    # Generate the folder to save within. The 