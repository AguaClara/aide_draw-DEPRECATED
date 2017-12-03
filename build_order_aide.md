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


Assumptions made when the json is passed to fgen_manager.traverse_fdoc_dict:
1. Each entry within an fdoc corresponds to an fgen. 
2. All parameters that are :aide_expression types are converted to :fusion_expression types (there are no aide_expressions) or any jgen types. 
3. Within a single fdoc_set, each fdoc has a unique name. 
4. The following types are supported: :fgen :fgen_parameters :fdoc :fdoc_set :fusion_expression

Observations:

* RULE: If the key has a dictionary as that value, THEN the key is a declaring the TYPE for all in the dictionary
IF it doesn't have a dictionary, then it is assumed to be the type of the outer dictionary. 

* An outer scoping implies that certain types are expected. Within the scoping, the types expected have to 
be followed. If not, this raises an error. If ambiguity is expected, it's common to use types (:type) to 
avoid such ambiguity. 

* Extensions should be well-documented abstract classes. Additionally, the fgen manager should be an abstract class

* The json should go through some pre-processors before it passes off to the aide_draw functionality. Ask:
what is the simplest json aide_draw can get that still specifies everything and hasn't touched adsk?

* Key idea: adsk is NOT available to aide_design. Good reason for this. 

* jgens are functions in aide_design that can "pre-process" the json. These, like fgens, can completely
build a well-documented json through recursive generation. They also provide a key way to see the progression
of a plant design through multiple stages. 

* How do we make budgets? Are these also fgens? Almost seems like they could be.. You "update" them the same way...
A budget fgen could fetch parameters, know the name of the thing you're creating... 

* Types would let us go backwards...

