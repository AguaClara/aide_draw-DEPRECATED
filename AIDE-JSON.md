# AIDE JSON Formal Definition

## Introduction
This is the formal language definition of the AIDE JSON. In defining the
language, we define the values as particular objects with types
that make up the JSON file. The following types correspond to special keywords
that indicate the corresponding object is of that type. The following list
outlines the type keyword, the structure of the object, and an example of the
JSON that would make this.

## Syntax
We try to follow the python syntax as closely as possible. 

<> indicates the object inside is necessary
() indicates the object within is unnecessary

* key: folders
  * structure:
  ```JSON
  {
    "<name>":"string",
    "(fdocs)":["fdoc_dict"]
  }
  ```
  * example:
  ```JSON
  {
    "name":"folder_of_components",
    "fdocs":[]
  }
  ```
* key: fdocs
  * structure:
  ```JSON
  [{
    "<name>":"string",
    "<generator_name>":"generator_dict"
  }]
  ```
  * example:
  ```JSON
  {
    "name":"folder_of_components",
    "adjust_template":{

    }
  }
  ```
