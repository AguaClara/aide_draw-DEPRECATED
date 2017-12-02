Order of operations:

Inserting File References
-collect all path references and assemble template folder tree
-fill in the tree with all template dataFile references (breadth-first-search)
-copy and paste those references into the param section of the fgen (perhaps just replace "template" with the ref)

Resolving inter-referenced expressions
-Search the folder_dict_tree for dependent expressions
-If you find one, search for the dependencies recursively and

MVP:
scoping in parameters

Generate the Json:
Build the JSON from the folders.
Takes a defined sketch, creates a json from the sketch, with all the parameters
that currently exist.

Change the parameters, then run the tool to change the params.
