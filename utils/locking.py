import adsk.core, adsk.fusion, adsk.cam

def lock_assem(rootComp):
    """
    Locks entire assembly (based on the rootComp) in a Rigid Group
    
    :param context: the root component of the assembly
    :return: None
    """
    
    #put all occurences into a collection
    occs = adsk.core.ObjectCollection.create()
    
    for i in range(0, len(rootComp.occurrences.asList)):
        occs.add(rootComp.occurrences.item(i))
        
    #create a rigid group
    isIncludeChildren = True
    rigidGroups = rootComp.rigidGroups
    
    if len(occs) > 1: #don't create rigis croup on single occurance, will fail
        lock = rigidGroups.add(occs, isIncludeChildren)
        lock.name = "aide_draw_lock"
    
def unlock_assem(rootComp):
    """
    Removes Rigid Group from assembly
    
    :param context: the root component of the assembly
    :return: None
    """
    rigidGroups = rootComp.rigidGroups
    if rigidGroups.itemByName("aide_draw_lock"):
        rigidGroups.itemByName("aide_draw_lock").deleteMe()