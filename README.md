# shotmanager
ShotManager is a NUKE tool designed to help you navigate and open project files efficiently.
It provides a column-based browser interface to quickly locate and open NUKE scripts across your project folders.
<p align="center">
  <img src="https://github.com/LRongeart/shotmanager/blob/main/icon/shotManager.png" width="150" title="ShotManagerIcon">
</p>

## Interface Layout:
> [!NOTE]
> ![image](https://github.com/user-attachments/assets/f44684bb-aaed-42de-897f-3b1acb57bb6a)
> - **_FIRST Column_** - Shows: Lists all available shows/projects from your main folder
> - **_INTER Columns_** - Folder Name: Lists all folders up to your `.nk` files
> - **_LAST Column_** - Files: Shows all files in the `nuke` subfolder (`.nk` scripts are highlighted)

## How to Use ShotManager
- **_Select a Show:_** Click on a show name in the first column 
- **_Browse Files:_** Navigate in your file directories up until your `nuke` subfolder or `nuke` files
- **_Select File:_** Choose a NUKE script (`.nk` file) from the last column 
- **_Open Script:_** Click "Open .nk Script" to load the selected file
- **_Use Favorites:_** LeftClick on Favorites to navigate directly to that folder. You can RightClick on Folders to add them to your Favourite Tab.

## A - Configuration
> [!IMPORTANT]
> **Initialization:**
>> - Copy the `shotmanager` folder in your local `~/.nuke/` directory;
>> - Copy the `shotmanager/icon` content in your local `~/.nuke/icons` directory;
>> - In your `~/.nuke/menu.py` script, add the content of `~/.nuke/menu.py`;
>>
> **In shotmanager_ui.py:**
>> - Open `shotmanager_ui.py` file in your `~/.nuke/shotmanager/` directory;
>> - At l.12, change the value of `mainFolderPath` to your primary directory;
>> - At l.13, change the value of `secondaryFolderPath` to your secondary directory;
>> 
> **In live_projects.json:** 
>> - Open `live_projects.json` file in your `~/.nuke/shotmanager/` directory;
>> - You can add to this list the folder names of Shows/Projects you want to see highlighted in ShotManager. By default, they're not active ( == `{"status": "offline"}`), but you need to specify `{"status": "active"}` to have them highlighted.
>> 
 
## B - Features [^1]
- **_Favorites Panel:_** Quickly jump to frequently used folders with one click
- **_Favorite Star Icons:_** A small star appears on the right of folders marked as favorites
- **_Favorites Grouping:_** Automatically grouped by show name (e.g., SHOW_A, SHOW_B)
- **_Script Detection:_** NUKE scripts (.nk) are highlighted in green and bold
- **_Active Projects Highlighting:_** Projects marked as active in your configuration will be highlighted in black. All projects, whether active or not, need to be listed in a `live_projects.json` file in your `~/.nuke/shotmanager/` directory 
- **_NUKE Script Detection:_** `.nk` files are automatically highlighted and made bold for easy identification 
- **_Path Flexibility:_** Supports both local drives and UNC network paths 
- **_Safe Script Opening:_** Prompts before closing current script when opening a new one 

## C - File Structure Expected:
>      Main Folder
>        ├── SHOW_A/
>        │   ├── SHOTS/
>        │   │   └── SEQ01_SH010/
>        │   │       └── nuke/
>        │   │           └── SHOT_template_script_v01.nk
>        │   └── ASSETS/
>        │       └── chrHero/
>        │           └── nuke/
>        │               └── ASSET_template_script_v01.nk
>        ├── SHOW_B/
>        │   ├── ... (similar structure as SHOW_A)

         
## D - Tips
> [!NOTE]
> - Use Ctrl+Click on any folder to instantly add/remove it from favorites
> - You can reorder or remove favorite paths via the favorites bar
> - Clicking a favorite rebuilds all columns to reveal it
> - If a folder is empty, a placeholder item will be displayed
> - The "Open NUKE Script" button becomes active and styled when a .nk file is selected
> - All files are shown, but only .nk files can be opened directly 
> - The selected file path is displayed at the bottom for verification 
> - You can keep the ShotManager window open while working in NUKE 

## E - Troubleshooting 
- Favorites not saving: Check write permissions in your script folder. 
- Missing live_projects.json:: Check that your `live_projects.json` file exists in `~/.nuke/shotmanager` and contains the correct project names. 
- Cannot access network paths: Ensure you have proper network permissions and the UNC path is accessible. 

[^1]: Sources
-- For additional support or feature requests, contact Loucas RONGEART -- loucas.rongeart@gmail.com 
ShotManager v1.1 
