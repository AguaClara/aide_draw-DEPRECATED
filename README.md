# Installation Instructions

1. Clone this repo to your local computer
2. Follow [these instructions](https://knowledge.autodesk.com/support/fusion-360/troubleshooting/caas/sfdcarticles/sfdcarticles/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html) or skip to step 3 for the
short of it!
3. In short, click on the scripts/add-ins button in fusion,
switch to the add-ins tab and click on the little green plus to open a folder
dialog box. Select the folder of this git repo you cloned. Now you should be
able to hit 'run' to start the script.
4. The script should open a dialog box. To ensure everything is working OK,
follow the testing instructions in [Tests.](#tests)

# Tests

## Run a Test

1. Open the template(s) you'd like to parametrize in Fusion from the
tests/templates folder within the AIDE add-in folder. To do this, you'll need
to select 'New Design From File' above the model workspace in the new File
drop down, and select the f3d associated with the test you want to perform.
be sure to name it to whatever the template name is in the associated JSON.
For the test_cube test, you should name the document "test_cube" and save it.
Alternatively, you can input the official "AIDE Tests" Fusion project [here]
2. If the add-in is properly installed, you should be able to open the AIDE
dialog by clicking the aide button next to the add-in button in Fusion 360.
3. In the dialog box, select the test JSON you'd like to run from the tests/json
folder.
4. Now select "OK" to indicate you would like to run the AIDE.
5. You should now see the finalized design and it should be saved in the root
folder of your current project with the name specified within the JSON. If a
folder of designs was generated, the folder will be in the current project's
root.
6. The JSON should be simple enough to compare with the test output.

## Notes About Testing

The Fusion 360 API makes it difficult to run proper tests, and so we are
unfortunately left to a manual testing protocol. We hope this will change.

# Development Guidelines

The Fusion 360 environment is limited. It runs within an old version of Python
(3.5) and thus the goal is to get out of the environment as quickly as possible.
This is why we attempt to reduce the number of calculations F360 needs to do by
using a JSON to communicate all the required parameters. Therefore, it's
important to use the Fusion API for only the most general tasks. The goal is to
keep this as a simple add-in that can take a JSON and corresponding Fusion 360
template folder and generate the dimensioned results folder.

# AIDE-JSON Design

The AIDE JSON design allows designers to elegantly specify the parameters of
complex design using a standard AIDE JSON language. Below are increasingly
complex examples that explain the steps AIDE JSON takes to make these designs
and the corresponding JSON file. All of these examples can be found in the
tests/ folder of this add-in.

## Sizing a Single Fusion Document

The JSON is what AIDE uses to properly size the templates. AIDE expects the JSON
to be formatted properly to the AIDE language, as stipulated below.
The following illustrates a simple JSON cube design:

``` JSON
{
  "name":"test_cube_result",
  "template":"test_cube",
  "parameters":{
    "width":"1 in",
    "height":"2 in",
    "length":"3 in"
  }
}
```

When this JSON is selected along with the test_cube.f3d template, AIDE will
accomplish the following:
1. Ensure the template's name is "test_cube.f3d" and it is currently open and active
2. Update the expressions of the width, height and length parameters (model OR
  user) to the corresponding values
3. Save the resulting sized model as "test_cube_result.f3d" in whatever folder
was selected by the user.

## Sizing a Folder of Fusion Documents

Say you want to create a whole bunch of components that are all nested in various
folders. The AIDE JSON can do this with only some slight tweaks.
The JSON is formatted roughly the same way as the target folder structure, such
that the root JSON object corresponds to the root folder of the target folder.
Working off the cube example above, the following can take one template, and
generate a base, middle and top, naming them and putting them into the appropriate
folders:

``` JSON
{
  "name":"pyramid_components",
  "fdocs":[
    {
    "name":"base",
    "template":"test_cube",
    "parameters":{
      "width":"3 in",
      "height":"3 in",
      "length":"3 in"
      }
    },
    {
    "name":"middle",
    "template":"test_cube",
    "parameters":{
      "width":"2 in",
      "height":"2 in",
      "length":"2 in"
      }
    },
    {
    "name":"top",
    "template":"test_cube",
    "parameters":{
      "width":"1 in",
      "height":"1 in",
      "length":"1 in"
      }
    }
  ]
}
```

# TODO:

There are many features that the AIDE team is currently working on. Please see
the "issues" section of this repo to see all the great work the team is up to!
And don't hesitate to make comments/suggestions.

Let's make the best parametric design engine possible!
