from . import names_to_versions
from . import locking

def build_names_to_versions(root_component):
    return names_to_versions.build_names_to_versions(root_component)

def lock_assem(rootComp):
    return locking.lock_assem(rootComp)
    
def unlock_assem(rootComp):
    return locking.unlock_assem(rootComp)
