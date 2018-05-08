from .. import yaml


def compare_yamls(path1, path2):
    """
    Compare two yamls. Return true if they are the same excluding hp attributes

    Args:
        path1: path to a yaml file
        path2: path to a 2nd yaml file

    Returns:
        Boolean representing whether the two yamls were deemed equal

    Raises:

    Examples:
        ?
    """
    f1 = open(path1, 'r')
    f2 = open(path2, 'r')
    
    y1 = yaml.load(f1)
    y2 = yaml.load(f2)
    
    f1.close()
    f2.close()
    	
    return compare_yamls_helper(y1, y2)



def compare_yamls_helper(y1, y2):
        #starts as True, set to False if any incongruency found
	equal = True

        #regular equality if strings
	if isinstance(y1, str):
		return y1 == y2

	for key, value in y1.items():
		if key in y2:
                  #equal if compare_yamls_helper is always true for all keys
			equal = equal and compare_yamls_helper(y1[key], y2[key])
		elif key == "hp" or key == "cp":
			continue
		else:
                  #key missing from 2nd yaml, return false
			return False

	return equal