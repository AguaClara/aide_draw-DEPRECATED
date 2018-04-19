import adsk.core, adsk.fusion, adsk.cam

def lock_assem(rootComp):
    
    occs = adsk.core.ObjectCollection.create()
    
    for i in range(0, len(rootComp.occurrences.asList)):
        occs.add(rootComp.occurrences.item(i))
        
    #create a rigid group
    isIncludeChildren = True
    rigidGroups = rootComp.rigidGroups
    
    if len(occs) > 1:
        lock = rigidGroups.add(occs, isIncludeChildren)
        lock.name = "aide_draw_lock"
    
def unlock_assem(rootComp):
    rigidGroups = rootComp.rigidGroups
    if rigidGroups.itemByName("aide_draw_lock"):
        rigidGroups.itemByName("aide_draw_lock").deleteMe()