# shotmanager
>ShotManager is a NUKE tool designed to help you navigate and open project files efficiently. It provides a four-column browser interface to quickly locate and open NUKE scripts across your shows directory.

Interface Layout
>[!NOTE]
>Column 1 - Shows: Lists all available shows/projects from your main folder
>Column 2 - Folder Category: Shows ASSETS, SHOTS, or other category folders 
>Column 3 - Asset/Shot Name: Lists individual assets or shots within the selected category 
>Column 4 - Files: Shows all files in the `nuke` subfolder (NUKE scripts are highlighted)

How to Use
>Select a Show: Click on a show name in the first column 
>Choose Category: Select ASSETS or SHOTS from the second column 
>Pick Asset/Shot: Choose the specific asset or shot from the third column 
>Select File: Choose a NUKE script (.nk file) from the fourth column 
>Open Script: Click "Open NUKE Script" to load the selected file 

## A - Features [^1]
>Active Projects Highlighting: Projects marked as active in your configuration will be highlighted in black. All projects, whether active or not, need to be listed in a `live_projects.json` file in your `~/.nuke/shotmanager/` directory 
>NUKE Script Detection: `.nk` files are automatically highlighted and made bold for easy identification 
>Path Flexibility: Supports both local drives and UNC network paths 
>Safe Script Opening: Prompts before closing current script when opening a new one 

## B - Configuration
>[!IMPORTANT]
>Main Folder: Use the "Change Main Folder" button to point to your shows directory. In `shotmanager_ui.py` you'll find the `main_folder_path` variable in which you can specify >it's default path. It can be customized based upon where you have your show directory. 
>Active Projects: Create a `live_projects.json` file in your `~/.nuke/shotmanager/` directory to specify which projects should be highlighted. 

## C - File Structure Expected:
>        Main Folder/
>        ├── ShowName1/
>        │   ├── ASSETS/
>        │   │   └── AssetName/
>        │   │       └── nuke/
>        │   │           ├── script1.nk
>        │   │           └── script2.nk
>        │   └── SHOTS/
>        │       └── ShotName/
>        │           └── nuke/
>        │               └── shot_script.nk
>        └── ShowName2/
>            └── ...|

         
## D -Tips
>[!NOTE]
The tool automatically looks for a 'nuke' subfolder within each asset/shot directory 
All files are shown, but only .nk files can be opened directly 
The selected file path is displayed at the bottom for verification 
You can keep the ShotManager window open while working in NUKE 
Troubleshooting 
"No 'nuke' folder found": Ensure your assets/shots have a 'nuke' subfolder containing the NUKE scripts. 
Projects not highlighting: Check that your 'live_projects.json' file exists and contains the correct project names. 
Cannot access network paths: Ensure you have proper network permissions and the UNC path is accessible. 

[^1]: Sources
-- For additional support or feature requests, contact Loucas RONGEART -- loucas.rongeart@gmail.com 
ShotManager v1.0 
