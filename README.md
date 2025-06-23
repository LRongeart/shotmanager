# shotmanager
>ShotManager is a NUKE tool designed to help you navigate and open project files efficiently. It provides a four-column browser interface to quickly locate and open NUKE scripts across your shows directory.


## Interface Layout:
> [!NOTE]
> ![ShotManager_screenshot width="350"](https://github.com/user-attachments/assets/ae7ab203-5d8f-41ef-bd35-7beaebfd17bc)
> - **_Column 1_** - Shows: Lists all available shows/projects from your main folder
> - **_Column 2_** - Folder Category: Shows ASSETS, SHOTS, or other category folders 
> - **_Column 3_** - Asset/Shot Name: Lists individual assets or shots within the selected category 
> - **_Column 4_** - Files: Shows all files in the `nuke` subfolder (NUKE scripts are highlighted)

## How to Use ShotManager
- **_Select a Show:_** Click on a show name in the first column 
- **_Choose Category:_** Select ASSETS or SHOTS from the second column 
- _**Pick Asset/Shot:**_ Choose the specific asset or shot from the third column 
- **_Select File:_** Choose a NUKE script (.nk file) from the fourth column 
- **_Open Script:_** Click "Open NUKE Script" to load the selected file 

## A - Features [^1]
- **_Active Projects Highlighting:_** Projects marked as active in your configuration will be highlighted in black. All projects, whether active or not, need to be listed in a `live_projects.json` file in your `~/.nuke/shotmanager/` directory 
- **_NUKE Script Detection:_** `.nk` files are automatically highlighted and made bold for easy identification 
- **_Path Flexibility:_** Supports both local drives and UNC network paths 
- **_Safe Script Opening:_** Prompts before closing current script when opening a new one 


## B - Configuration
> [!IMPORTANT]
> - **Initialization:**
>> - Copy the `shotmanager` folder in your local `~/.nuke/` directory,
>> - Copy the `shotmanager/icon` content in your local `~/.nuke/icons` directory,
>> - In your `~/.nuke/menu.py` script, add the content of `~/.nuke/menu.py`,
> - **In shotmanager_ui.py:**
>> - Open `shotmanager_ui.py` file in your `~/.nuke/shotmanager/` directory
>> - At l.29, change the value of `self.main_folder_path` to your primary directory;
>> - At l.30, change the value of `self.secondary_folder_path` to your secondary directory;
> - **In live_projects.json:** 
>> - Open `live_projects.json` file in your `~/.nuke/shotmanager/` directory
>> - 
 

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
>            └── ...

         
## D - Tips
> [!NOTE]
> - The tool automatically looks for a 'nuke' subfolder within each asset/shot directory 
> - All files are shown, but only .nk files can be opened directly 
> - The selected file path is displayed at the bottom for verification 
> - You can keep the ShotManager window open while working in NUKE 

## E - Troubleshooting 
- "No 'nuke' folder found": Ensure your assets/shots have a 'nuke' subfolder containing the NUKE scripts. 
- Projects not highlighting: Check that your 'live_projects.json' file exists and contains the correct project names. 
- Cannot access network paths: Ensure you have proper network permissions and the UNC path is accessible. 

[^1]: Sources
-- For additional support or feature requests, contact Loucas RONGEART -- loucas.rongeart@gmail.com 
ShotManager v1.0 
