"""This module can take an LFOM doc, and specify the number of holes per row

"""

import adsk
import adsk_utilities

def start(hole_list, max_holes, feature_name, seed_name, fdoc):
    """Makes a number of rings of holes on a vertical cylinder

        Parameters
        ----------
        hole_list : int list
            The number of holes desired in each row. This will cluster the holes to be on either side of the original
            line of holes.
        max_holes : int
            The maximum number of holes that could be patterned in a single row. We use this to calculate the total
            angle value for each row of holes.
        feature_name : str
            The name of the feature that will be copied. This can be set in the Fusion browser.
        fdoc : FusionDocument
            A FusionDocument.

        Returns
        -------
        ids_suppressed : list of ints
            A list of all the pattern ids that were suppressed.

        Raises
        ------
        UserWarning
            Raised when a number of holes for a certain line is too many to fit with the proper spacing.
    """
    # ensure the fdoc passed is a Fusion Document:
    fdoc = adsk.fusion.FusionDocument.cast(fdoc)
    root_component = fdoc.design.rootComponent
    features = root_component.features
    y_axis = root_component.yConstructionAxis

    # Get the faces of the extrusion:
    faces = features.itemByName(feature_name)

    # Get the the features that we will pattern
    seed_feature = features.itemByName(seed_name)
    pattern_elements = seed_feature.patternElements

    # get the feature input we need to copy
    circle_features = features.circularPatternFeatures
    rectangular_features = features.rectangularPatternFeatures

    # Make all the circular pattern features
    i = 0
    for n_holes in hole_list:
        input_entities = adsk.core.ObjectCollection.create()
        # Don't add a pattern if not needed
        if n_holes == 1:
            i += 1
            continue
        # The first row uses the original hole as the inputEntity
        if i == 0:
            input_entities.add(faces)
        else:
            pattern_element = pattern_elements.item(i-1)

            input_entities.add(adsk.fusion.BRepFace.cast(seed_feature.faces[i-1]))
        i += 1
        angle = ((n_holes-1)/max_holes)*360
        new_feature_input = circle_features.createInput(input_entities, y_axis)
        new_feature_input.quantity = adsk.core.ValueInput.createByReal(n_holes)
        new_feature_input.totalAngle = adsk.core.ValueInput.createByString(str(angle) + ' deg')
        new_feature_input.isSymmetric = True
        new_feature = circle_features.add(new_feature_input)
        new_feature.name = "cylindrical_pattern_feature_" + str(i+1)
