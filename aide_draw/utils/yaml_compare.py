from .. import yaml


#compares yaml files, ignoring hp attributes
def compare_yamls(path1, path2):
	f1 = open(path1, 'r')
	f2 = open(path2, 'r')

	y1 = yaml.load(f1)
	y2 = yaml.load(f2)

	f1.close()
	f2.close()
	
	return compare_yamls_helper(y1, y2)



def compare_yamls_helper(y1, y2):
	equal = True

	if isinstance(y1, str):
		return y1 == y2

	for key, value in y1.items():
		if key in y2:
			equal = equal and compare_yamls_helper(y1[key], y2[key])
		elif key == "hp" or key == "cp":
			continue
		else:
			return False

	return equal