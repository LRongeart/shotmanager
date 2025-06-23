import nuke
import getpass
import os
import shotmanager

from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import isValid



#Global reference to prevent garbage collection
submit_ui_instance = None
help_ui_instance = None
username = getpass.getuser()
shotmanagerVersion = "v1.0"
shotmanagerWindowTitle = 'ShotManager {}'.format(shotmanagerVersion)
shotmanagerHelpWindowTitle = 'ShotManager Help {}'.format(shotmanagerVersion)
contactLR = "loucas.rongeart@gmail.com"


class ShotManagerUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ShotManagerUI, self).__init__(parent)
        self.setWindowTitle("ShotManager - Browser")
        self.setMinimumWidth(1400)
        self.setMinimumHeight(600)
        
        # Main folder path - supports UNC paths (\\server\share\path)
        self.main_folder_path = "E:/SHOWS"  # Change this to your desired path
        self.secondary_folder_path = "E:/01_PROJECTS" # Change this to your desired path
        
        # Load projects from JSON first
        self.active_projects = []
        self.loadActiveProjects()
        
        self.setupUI()
        self.populateMainFolders()


    def setupUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Header row with icon and title side-by-side
        header_layout = QtWidgets.QHBoxLayout()
        # Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon/shotManager.png")
        if os.path.exists(icon_path):
            icon_label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(icon_path)
            pixmap = pixmap.scaledToHeight(48, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(QtCore.Qt.AlignVCenter)
            header_layout.addWidget(icon_label)
        else:
            print("[ShotManager UI] Icon file not found:", icon_path)

        # Title
        header_label = QtWidgets.QLabel(shotmanagerWindowTitle)
        header_font = header_label.font()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(QtCore.Qt.AlignVCenter)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Username label
        user_label = QtWidgets.QLabel(f"Logged in as: {getpass.getuser()}")
        user_label.setAlignment(QtCore.Qt.AlignRight)
        main_layout.addWidget(user_label)

        # Path display with change button
        path_layout = QtWidgets.QHBoxLayout()
        self.path_label = QtWidgets.QLabel(f"Main Folder: {self.main_folder_path}")
        path_layout.addWidget(self.path_label)

        # Change Main Folder button
        self.change_folder_button = QtWidgets.QPushButton("Change Main Folder")
        self.change_folder_button.clicked.connect(self.changeMainFolder)
        path_layout.addWidget(self.change_folder_button)

        # Switch Button
        self.switch_folder_button = QtWidgets.QPushButton("Switch Between Primary/Secondary Folder")
        self.switch_folder_button.clicked.connect(self.switchMainFolder)
        path_layout.addWidget(self.switch_folder_button)

        path_layout.addStretch()
        main_layout.addLayout(path_layout)

        # Four-column layout
        columns_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(columns_layout)

        # First Column
        first_column_layout = QtWidgets.QVBoxLayout()
        self.first_column_label = QtWidgets.QLabel("Shows")
        self.first_column_label.setAlignment(QtCore.Qt.AlignCenter)
        first_column_layout.addWidget(self.first_column_label)

        self.main_folders_list = QtWidgets.QListWidget()
        self.main_folders_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.main_folders_list.itemSelectionChanged.connect(self.onMainFolderSelected)
        first_column_layout.addWidget(self.main_folders_list)
        columns_layout.addLayout(first_column_layout)

        # Second Column
        second_column_layout = QtWidgets.QVBoxLayout()
        self.second_column_label = QtWidgets.QLabel("Folder Category")
        self.second_column_label.setAlignment(QtCore.Qt.AlignCenter)
        second_column_layout.addWidget(self.second_column_label)

        self.type_list = QtWidgets.QListWidget()
        self.type_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.type_list.itemSelectionChanged.connect(self.onTypeSelected)
        second_column_layout.addWidget(self.type_list)
        columns_layout.addLayout(second_column_layout)

        # Third Column
        third_column_layout = QtWidgets.QVBoxLayout()
        self.third_column_label = QtWidgets.QLabel("Asset/Shot Name")
        self.third_column_label.setAlignment(QtCore.Qt.AlignCenter)
        third_column_layout.addWidget(self.third_column_label)

        self.subfolders_list = QtWidgets.QListWidget()
        self.subfolders_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.subfolders_list.itemSelectionChanged.connect(self.onSubfolderSelected)
        third_column_layout.addWidget(self.subfolders_list)
        columns_layout.addLayout(third_column_layout)

        # Fourth Column
        fourth_column_layout = QtWidgets.QVBoxLayout()
        self.fourth_column_label = QtWidgets.QLabel("Asset/Shot Files")
        self.fourth_column_label.setAlignment(QtCore.Qt.AlignCenter)
        fourth_column_layout.addWidget(self.fourth_column_label)

        self.files_list = QtWidgets.QListWidget()
        self.files_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.files_list.itemSelectionChanged.connect(self.onFileSelected)
        fourth_column_layout.addWidget(self.files_list)
        columns_layout.addLayout(fourth_column_layout)

        # Bottom Section
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.selected_path_label = QtWidgets.QLabel("No file selected")
        self.selected_path_label.setWordWrap(True)
        button_layout.addWidget(self.selected_path_label)

        button_layout.addStretch()

        self.open_script_button = QtWidgets.QPushButton("Open Selected Script")
        self.open_script_button.clicked.connect(self.openScript)
        self.open_script_button.setEnabled(False)
        button_layout.addWidget(self.open_script_button)

        main_layout.addLayout(button_layout)


    def switchMainFolder(self):
        """Swap between the main and secondary folder"""
        self.main_folder_path, self.secondary_folder_path = self.secondary_folder_path, self.main_folder_path
        self.path_label.setText(f"Main Folder: {self.main_folder_path}")
        self.loadActiveProjects()  # Optional: reload project highlights
        self.populateMainFolders()


    def setMainFolderPath(self, path):
        """Set the main folder path and refresh the UI - supports UNC paths"""
        if os.path.exists(path) and os.path.isdir(path):
            self.main_folder_path = path
            self.path_label.setText(f"Main Folder: {self.main_folder_path}")
            self.populateMainFolders()
            return True
        return False

    def populateMainFolders(self):
        """Populate the first column with folders from the main directory (Shows)"""
        self.main_folders_list.clear()
        self.type_list.clear()
        self.subfolders_list.clear()
        self.files_list.clear()
        self.open_script_button.setEnabled(False)
        self.selected_path_label.setText("No file selected")
        
        if not os.path.exists(self.main_folder_path):
            print(f"[ShotManager] Main folder path does not exist: {self.main_folder_path}")
            return
        
        try:
            for item in os.listdir(self.main_folder_path):
                item_path = os.path.join(self.main_folder_path, item)
                if os.path.isdir(item_path):
                    list_item = QtWidgets.QListWidgetItem(item)
                    list_item.setData(QtCore.Qt.UserRole, item_path)
                    
                    # Check if this show is in the active projects list
                    if item in self.active_projects:
                        # Style active projects with black background and bold white text
                        list_item.setBackground(QtCore.Qt.black)
                        list_item.setForeground(QtCore.Qt.white)
                        font = list_item.font()
                        font.setBold(True)
                        list_item.setFont(font)
                        print(f"[ShotManager] Highlighting active project: {item}")
                    else:
                        print(f"[ShotManager] Project '{item}' not in active list - using normal styling")
                    
                    self.main_folders_list.addItem(list_item)
        except Exception as e:
            print(f"[ShotManager] Error reading main folder: {e}")

    def onMainFolderSelected(self):
        """Handle selection of a main folder (Show)"""
        self.type_list.clear()
        self.subfolders_list.clear()
        self.files_list.clear()
        self.open_script_button.setEnabled(False)
        self.selected_path_label.setText("No file selected")
        
        selected_items = self.main_folders_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        folder_path = selected_item.data(QtCore.Qt.UserRole)
        
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    print(f"[ShotManager] Found category: {item_path}")
                    list_item = QtWidgets.QListWidgetItem(item)
                    list_item.setData(QtCore.Qt.UserRole, item_path)
                    self.type_list.addItem(list_item)
        except Exception as e:
            print(f"[ShotManager] Error reading show folders: {e}")

    def onTypeSelected(self):
        """Handle selection of type (ASSETS/SHOTS)"""
        self.subfolders_list.clear()
        self.files_list.clear()
        self.open_script_button.setEnabled(False)
        self.selected_path_label.setText("No file selected")
        
        selected_items = self.type_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        type_path = selected_item.data(QtCore.Qt.UserRole)
        
        # Update the third column label based on selection
        type_name = selected_item.text().upper()
        if "SHOT" in type_name:
            self.third_column_label.setText("Shots")
        elif "ASSET" in type_name:
            self.third_column_label.setText("Assets")
        else:
            self.third_column_label.setText("Miscellaneous")
        
        try:
            for item in os.listdir(type_path):
                item_path = os.path.join(type_path, item)
                if os.path.isdir(item_path):
                    list_item = QtWidgets.QListWidgetItem(item)
                    list_item.setData(QtCore.Qt.UserRole, item_path)
                    self.subfolders_list.addItem(list_item)
        except Exception as e:
            print(f"[ShotManager] Error reading type folders: {e}")

    def onSubfolderSelected(self):
        """Handle selection of a subfolder (Sequence/Asset) and look for nuke folder"""
        self.files_list.clear()
        self.open_script_button.setEnabled(False)
        self.selected_path_label.setText("No file selected")
        
        selected_items = self.subfolders_list.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        subfolder_path = selected_item.data(QtCore.Qt.UserRole)
        
        # Look for the 'nuke' folder inside the selected subfolder
        nuke_folder_path = os.path.join(subfolder_path, 'nuke')
        
        if not os.path.exists(nuke_folder_path) or not os.path.isdir(nuke_folder_path):
            # If 'nuke' folder doesn't exist, show message in the files list
            no_nuke_item = QtWidgets.QListWidgetItem("No 'nuke' folder found")
            no_nuke_item.setData(QtCore.Qt.UserRole, None)
            self.files_list.addItem(no_nuke_item)
            print(f"[ShotManager] No 'nuke' folder found in: {subfolder_path}")
            return
        
        try:
            # List all files in the nuke folder (not just .nk files)
            files_found = False
            for item in os.listdir(nuke_folder_path):
                item_path = os.path.join(nuke_folder_path, item)
                if os.path.isfile(item_path):
                    list_item = QtWidgets.QListWidgetItem(item)
                    list_item.setData(QtCore.Qt.UserRole, item_path)
                    
                    # Highlight .nk files differently (without emoji to avoid display issues)
                    if item.lower().endswith('.nk'):
                        list_item.setBackground(QtCore.Qt.black)
                        # Bold text for NUKE scripts instead of emoji
                        font = list_item.font()
                        font.setBold(True)
                        list_item.setFont(font)
                    
                    self.files_list.addItem(list_item)
                    files_found = True
            
            if not files_found:
                no_files_item = QtWidgets.QListWidgetItem("No files found in 'nuke' folder")
                no_files_item.setData(QtCore.Qt.UserRole, None)
                self.files_list.addItem(no_files_item)
                
        except Exception as e:
            print(f"[ShotManager] Error reading nuke folder: {e}")
            error_item = QtWidgets.QListWidgetItem(f"Error reading folder: {str(e)}")
            error_item.setData(QtCore.Qt.UserRole, None)
            self.files_list.addItem(error_item)

    def onFileSelected(self):
        """Handle file selection and update UI accordingly"""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            self.open_script_button.setEnabled(False)
            self.selected_path_label.setText("No file selected")
            return
        
        selected_item = selected_items[0]
        file_path = selected_item.data(QtCore.Qt.UserRole)
        
        if file_path is None:
            # This is a placeholder item (no nuke folder, no files, etc.)
            self.open_script_button.setEnabled(False)
            self.selected_path_label.setText("No valid file selected")
            return
        
        # Update the selected path label
        self.selected_path_label.setText(f"Selected: {file_path}")
        
        # Enable open button only for .nk files
        if file_path.lower().endswith('.nk'):
            self.open_script_button.setEnabled(True)
            self.open_script_button.setText("Open NUKE Script")
        else:
            self.open_script_button.setEnabled(False)
            self.open_script_button.setText("Select a .nk file to open")

    def changeMainFolder(self):
        """Open a dialog to change the main folder path"""
        new_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            "Select Main Folder", 
            self.main_folder_path
        )
        
        if new_path:
            if self.setMainFolderPath(new_path):
                # Reload projects when path changes
                self.loadActiveProjects()
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"Main folder changed to:\n{new_path}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Error", 
                    "Failed to set the selected folder as main folder."
                )

    def openScript(self):
        """Open the selected NUKE script"""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, 
                "No Selection", 
                "Please select a NUKE script to open."
            )
            return
        
        selected_item = selected_items[0]
        script_path = selected_item.data(QtCore.Qt.UserRole)
        
        if script_path is None or not script_path.lower().endswith('.nk'):
            QtWidgets.QMessageBox.warning(
                self, 
                "Invalid Selection", 
                "Please select a valid .nk file to open."
            )
            return
        
        # Check if there's already a script open
        current_script = nuke.root().name()
        if current_script != "Root":
            reply = QtWidgets.QMessageBox.question(
                self,
                "Script Already Open",
                f"A script is currently open: {os.path.basename(current_script)}\n\n"
                "Do you want to close it and open the new script?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply != QtWidgets.QMessageBox.Yes:
                return
        
        try:
            # Clear the current script
            nuke.scriptClear()
            
            # Open the new script
            nuke.scriptOpen(script_path)
            
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Successfully opened:\n{os.path.basename(script_path)}\n\nFrom: {script_path}"
            )
            
            # Optionally close the dialog after successful load
            # self.close()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to open script:\n{str(e)}"
            )

    def loadActiveProjects(self):
        """Load active projects from JSON file"""
        self.active_projects = []
        
        # Option 1: Look in ~/.nuke/tractor/
        project_file = os.path.join(os.path.expanduser("~/.nuke/shotmanager"), "live_projects.json")
        print(f"[ShotManager] -Opt1- Looking for project file at: {project_file}")

        # Option 2 fallback: Look relative to the script
        if not os.path.exists(project_file):
            project_file = os.path.join(os.path.dirname(__file__), "live_projects.json")
            print(f"[ShotManager] -Opt2- Looking for project file at: {project_file}")
        
        if os.path.exists(project_file):
            try:
                import json
                with open(project_file, 'r') as f:
                    projects = json.load(f)
                
                # Handle different JSON structures
                if isinstance(projects, list):
                    # If it's a simple list of project names
                    self.active_projects = projects
                elif isinstance(projects, dict):
                    # If it's a dictionary, try to extract project names
                    # Common keys: 'projects', 'shows', 'active', etc.
                    for key in ['projects', 'shows', 'active', 'list']:
                        if key in projects:
                            if isinstance(projects[key], list):
                                self.active_projects = projects[key]
                                break
                    
                    # If no common key found, check if it's a status-based dictionary
                    if not self.active_projects:
                        # Look for projects with "active" status
                        for project_name, project_data in projects.items():
                            if isinstance(project_data, dict) and 'status' in project_data:
                                if project_data['status'].lower() == 'active':
                                    self.active_projects.append(project_name)
                                    print(f"[ShotManager] Project '{project_name}' is active")
                                else:
                                    print(f"[ShotManager] Project '{project_name}' has status '{project_data['status']}' - not highlighted")
                        
                        # If still no active projects found, use all keys as fallback
                        if not self.active_projects:
                            self.active_projects = list(projects.keys())
                            print(f"[ShotManager] No status-based projects found, using all project keys as active")
                
                print(f"[ShotManager] Successfully loaded {len(self.active_projects)} active projects: {self.active_projects}")
                
            except Exception as e:
                print(f"[ShotManager] Failed to load project list: {e}")
                self.active_projects = []
        else:
            print(f"[ShotManager] No project file found at expected locations, no projects will be highlighted")

    def populateProjects(self):
        """Legacy method - now calls loadActiveProjects for compatibility"""
        self.loadActiveProjects()



class ShowManagerUIHelp(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ShowManagerUIHelp, self).__init__(parent)
        self.setWindowTitle("ShotManager - Help")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Make dialog resizable and set modal behavior
        self.setModal(False)  # Allow interaction with main window
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # Clean up when closed
        
        self.setupUI()
        self.loadHelpContent()
    
    def closeEvent(self, event):
        print("[Help UI] Closed")
        super().closeEvent(event)

    def __del__(self):
        print("[Help UI] Python __del__ called")

    def setupUI(self):
        """Setup the help window UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Title/Header
        header_label = QtWidgets.QLabel(shotmanagerHelpWindowTitle)
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        header_font = header_label.font()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)
        
        # Help content area - using QTextEdit for rich text and scrolling
        self.help_text_edit = QtWidgets.QTextEdit()
        self.help_text_edit.setReadOnly(True)
        self.help_text_edit.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        
        # Style the text area
        self.help_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                border: 1px solid #cccccc;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 11pt;
            }
        """)
        
        main_layout.addWidget(self.help_text_edit)
        
        # Button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        # Close button
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setMinimumWidth(100)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)

    def loadHelpContent(self):
        """Load and display the help content - customize this method with your text"""
        help_content = self.getHelpText()
        self.help_text_edit.setHtml(help_content)

    def getHelpText(self):
        """Return the help content as HTML"""
        return f"""
        <h2>ShotManager User Guide</h2>
        <hr>

        <h3>Overview</h3>
        <p>ShotManager is a NUKE tool designed to help you navigate and open project files efficiently. 
        It provides a four-column browser interface to quickly locate and open NUKE scripts across your shows directory.</p>
        
        <h3>Interface Layout</h3>
        <ul>
            <li><strong>Column 1 - Shows:</strong> Lists all available shows/projects from your main folder</li>
            <li><strong>Column 2 - Folder Category:</strong> Shows ASSETS, SHOTS, or other category folders</li>
            <li><strong>Column 3 - Asset/Shot Name:</strong> Lists individual assets or shots within the selected category</li>
            <li><strong>Column 4 - Files:</strong> Shows all files in the 'nuke' subfolder (NUKE scripts are highlighted)</li>
        </ul>
        
        <h3>How to Use</h3>
        <ol>
            <li><strong>Select a Show:</strong> Click on a show name in the first column</li>
            <li><strong>Choose Category:</strong> Select ASSETS or SHOTS from the second column</li>
            <li><strong>Pick Asset/Shot:</strong> Choose the specific asset or shot from the third column</li>
            <li><strong>Select File:</strong> Choose a NUKE script (.nk file) from the fourth column</li>
            <li><strong>Open Script:</strong> Click "Open NUKE Script" to load the selected file</li>
        </ol>
        
        <h3>Features</h3>
        <ul>
            <li><strong>Active Projects Highlighting:</strong> Projects marked as active in your configuration will be highlighted in black.
            All projects, whether active or not, need to be listed in a 'live_projects.json' file in your '~/.nuke/shotmanager/' directory</li>
            <li><strong>NUKE Script Detection:</strong> .nk files are automatically highlighted and made bold for easy identification</li>
            <li><strong>Path Flexibility:</strong> Supports both local drives and UNC network paths</li>
            <li><strong>Safe Script Opening:</strong> Prompts before closing current script when opening a new one</li>
        </ul>
        
        <h3>Configuration</h3>
        <p><strong>Main Folder:</strong> Use the "Change Main Folder" button to point to your shows directory. In 'shotmanager_ui.py' you'll find 
        the 'main_folder_path' variable in which you can specify it's default path. It can be customized based upon where you have your
        show directory.</p>
        <p><strong>Active Projects:</strong> Create a 'live_projects.json' file in your ~/.nuke/shotmanager/ directory 
        to specify which projects should be highlighted.</p>
        
        <h3>File Structure Expected</h3>
        <pre>
        Main Folder/
        ├── ShowName1/
        │   ├── ASSETS/
        │   │   └── AssetName/
        │   │       └── nuke/
        │   │           ├── script1.nk
        │   │           └── script2.nk
        │   └── SHOTS/
        │       └── ShotName/
        │           └── nuke/
        │               └── shot_script.nk
        └── ShowName2/
            └── ...
        </pre>
        
        <h3>Tips</h3>
        <ul>
            <li>The tool automatically looks for a 'nuke' subfolder within each asset/shot directory</li>
            <li>All files are shown, but only .nk files can be opened directly</li>
            <li>The selected file path is displayed at the bottom for verification</li>
            <li>You can keep the ShotManager window open while working in NUKE</li>
        </ul>
        
        <h3>Troubleshooting</h3>
        <p><strong>"No 'nuke' folder found":</strong> Ensure your assets/shots have a 'nuke' subfolder containing the NUKE scripts.</p>
        <p><strong>Projects not highlighting:</strong> Check that your 'live_projects.json' file exists and contains the correct project names.</p>
        <p><strong>Cannot access network paths:</strong> Ensure you have proper network permissions and the UNC path is accessible.</p>
        
        <hr>
        <p><em>For additional support or feature requests, contact Loucas RONGEART -- <a href="mailto:{contactLR}">{contactLR}</a></em></p>
        <p><em>ShotManager {shotmanagerVersion}</p>
        """

    def setHelpContent(self, content):
        """Set custom help content (can be plain text or HTML)"""
        if isinstance(content, str):
            if content.strip().startswith('<'):
                # Assume HTML content
                self.help_text_edit.setHtml(content)
            else:
                # Plain text content
                self.help_text_edit.setPlainText(content)
        else:
            self.help_text_edit.setPlainText(str(content))

    def appendHelpContent(self, content):
        """Append additional content to existing help text"""
        current_content = self.help_text_edit.toHtml()
        if isinstance(content, str):
            if content.strip().startswith('<'):
                # HTML content
                new_content = current_content + content
                self.help_text_edit.setHtml(new_content)
            else:
                # Plain text - convert to HTML and append
                self.help_text_edit.moveCursor(QtWidgets.QTextCursor.End)
                self.help_text_edit.insertPlainText(content)




def launch_shotmanager_ui():
    """Launch the browser window - can be called independently"""
    global submit_ui_instance

    if submit_ui_instance and submit_ui_instance.isVisible():
        submit_ui_instance.close()
        submit_ui_instance = None

    submit_ui_instance = ShotManagerUI()
    submit_ui_instance.show()

def launch_help_window():
    global help_ui_instance

    try:
        if help_ui_instance and isValid(help_ui_instance) and help_ui_instance.isVisible():
            help_ui_instance.close()
            help_ui_instance = None
    except Exception as e:
        print(f"[ShotManager] Safe cleanup error: {e}")
        help_ui_instance = None

    help_ui_instance = ShowManagerUIHelp()
    help_ui_instance.show()
