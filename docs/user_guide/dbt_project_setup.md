---
  weight: 2
---

# DBT Project Setup

## Fabric Workspace Setup

Next we will create a new dbt project and configure it to use the dbt-fabricsparknb adapter. But, before we do this we need to gather some information from the Power BI / Fabric Portal. To do this, follow the steps below:


1. Open the Power BI Portal and navigate to the workspace you want to use for development. If necessary, create a new workspace.
1. Ensure that the workspace is Fabric enabled. If not, enable it.
1. Make sure that there is at least one Datalake in the workspace.
1. Get the connection details for the workspace.
  
    1. You will need to get the ==workspace name==, ==workspace id==, ==lakehouse id==, and ==lakehouse name==. 
    1. The ==lakehouse name== and ==workspace name== are easily viewed from the fabric / power bi portal. 
    1. The easiest way to get the id information is to:
          1. Navigate to a file or folder in your target lakehouse.
          2. Click on the three dots to the right of the file or folder name, and select "Properties". Details will be displayed in the properties window.
          3. From these properties select copy url and paste it into a text editor. The ==workspace id== is the first GUID in the URL, the ==lakehouse id== is the second GUID in the URL.
          4. In the example below, the workspace id is `4f0cb887-047a-48a1-98c3-ebdb38c784c2` and the lakehouse id is `aa2e5f92-53cc-4ab3-9a54-a6e5b1aeb9a9`.

```plaintext title="Example URL"
https://onelake.dfs.fabric.microsoft.com/4f0cb887-047a-48a1-98c3-ebdb38c784c2/aa2e5f92-53cc-4ab3-9a54-a6e5b1aeb9a9/Files/notebooks
```

## Create Dbt Project
Once you have taken note of the ==workspace id==, ==lakehouse id==, ==workspace name== and ==lakehouse name== you can create a new dbt project and configure it to use the dbt-fabricsparknb adapter. To do this, run the code shown below:

```powershell
# Create your dbt project directories and profiles.yml file
dbt init my_project # Note that the name of the project is arbitrary... call it whatever you like
```
!!! Important "When asked the questions below, provide the answers in bold below:"
    1. `Which data base would you like to use?` <br/>**select `dbt-fabricksparknb`**
    2. `Desired authentication method option (enter a number):` <br/>**select `livy`**
    3. `workspaceid (GUID of the workspace. Open the workspace from fabric.microsoft.com and copy the workspace url):` <br/>**Enter the workspace id**
    4. `lakehouse (Name of the Lakehouse in the workspace that you want to connect to):` <br/>**Enter the lakehouse name**
    5. `lakehouseid (GUID of the lakehouse, which can be extracted from url when you open lakehouse artifact from fabric.microsoft.com):` <br/>**Enter the lakehouse id**
    6. `endpoint [https://api.fabric.microsoft.com/v1]:` <br/>**Press enter to accept the default**
    7. `auth (Use CLI (az login) for interactive execution or SPN for automation) [CLI]:` <br/>**select `cli`**
    8. `client_id (Use when SPN auth is used.):` <br/>**Enter a single space and press enter**
    9. `client_scrent (Use when SPN auth is used.):` <br/>**Enter a single space and press enter**
    10. `tenant_id (Use when SPN auth is used.):` <br/>**Enter a single space or Enter your PowerBI tenant id**
    11. `connect_retries [0]:` <br/>**Enter 0**
    12. `connect_timeout [10]:` <br/>**Enter 10**
    13. `schema (default schema that dbt will build objects in):` <br/>**Enter `dbo`**
    14. threads (1 or more) [1]: <br/>**Enter 1**
    
The command above will create a new directory called `my_project`. Within this directory you will find a `dbt_project.yml` file. Open this file in your favourite text editor and note that it should look like the example below except that in your case my_project will be replaced with the name of the project you created above.:

``` yaml title="dbt_project.yml"

# Name your project! Project names should contain only lowercase characters
# and underscores. A good package name should reflect your organization's
# name or the intended use of these models
name: 'my_project'
version: '1.0.0'

# This setting configures which "profile" dbt uses for this project.
profile: 'my_project'

# These configurations specify where dbt should look for different types of files.
# The `model-paths` config, for example, states that models in this project can be
# found in the "models/" directory. You probably won't need to change these!
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:         # directories to be removed by `dbt clean`
  - "target"
  - "dbt_packages"


# Configuring models
# Full documentation: https://docs.getdbt.com/docs/configuring-models

models:
  test4:
    # Config indicated by + and applies to all files under models/example/
    example:
      +materialized: view

```

The dbt init command will also update your `profiles.yml` file with a profile matching your dbt project name. Open this file in your favourite text editor using the command below:

=== "Windows"

    ```powershell

    code  $home/.dbt/profiles.yml

    ```

=== "MacOS"

    ```powershell
    code  ~/.dbt/profiles.yml
    ```

=== "Linux"

    ```powershell
    code  ~/.dbt/profiles.yml
    ```

When run this will display a file similar to the one below. Check that your details are correct.

!!! note 
    The `profiles.yml` file should look like the example below except that in your case the highlighted lines may contain different values.

```{.yaml hl_lines="1 2 4 10 11 13 14" linenums="1" title="profiles.yml"}
my_project:
  target: my_project_target
  outputs:
    my_project_target:
      authentication: CLI
      method: livy
      connect_retries: 0
      connect_timeout: 10
      endpoint: https://api.fabric.microsoft.com/v1
      workspaceid: 4f0cb887-047a-48a1-98c3-ebdb38c784c2
      workspacename: test
      lakehousedatapath: /lakehouse
      lakehouseid: 031feff6-071d-42df-818a-984771c083c4
      lakehouse: datalake
      schema: dbo
      threads: 1
      type: fabricsparknb
      retry_all: true
```

Now we are ready to run our dbt project for the first time. But first we need to create a build script.

### Create a python build script that will wrap our dbt process 

This repository contains a dbt build script created in python. Make a copy of this script by copying the code found at [https://github.com/Insight-Services-APAC/APAC-Capability-DAI-DbtFabricSparkNb/blob/main/test_post_install.py](https://github.com/Insight-Services-APAC/APAC-Capability-DAI-DbtFabricSparkNb/blob/main/test_post_install.py). Alternatively, you can copy the code in the code block titled [Python Build script template](#python-build-script-template) below. Paste the code into a new file in the root of your source code directory. You can create this file using the vscode command line shown in the code block titled [New file creation in vscode](#New-file-creation-in-vscode) below.

!!! Important
    Be sure to change the line `os.environ['DBT_PROJECT_DIR'] = "testproj"` by replacing "testproj" with the folder name of your dbt project.

``` powershell title="New file creation in vscode"
code post_install.py
```

```python title="Python Build script template"
from dbt.adapters.fabricsparknb import utils as utils
import os
import sys
 
utils.RunDbtProjectArg(PreInstall=False,argv = sys.argv)
```

!!! info
    You are now ready to move to the next step in which you will build your dbt project. Follow the [Dbt Build Process](./dbt_build_process.md) guide.

