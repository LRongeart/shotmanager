import nuke
import getpass
import os
import shotmanager
import json

from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import isValid



mainFolderPath = "E:/SHOWS"
secondaryFolderPath = "E:/01_PROJECTS"

#Global reference to prevent garbage collection
submit_ui_instance = None
help_ui_instance = None
username = getpass.getuser()
shotmanagerVersion = "v1.1"
shotmanagerWindowTitle = 'ShotManager {}'.format(shotmanagerVersion)
shotmanagerHelpWindowTitle = 'ShotManager Help {}'.format(shotmanagerVersion)



class ScriptItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        item_data = index.data(QtCore.Qt.UserRole)
        is_selected = option.state & QtWidgets.QStyle.State_Selected
        is_favorite = index.data(QtCore.Qt.UserRole + 1)  # We'll store this below

        # Colors
        background = option.palette.base().color()
        text_color = option.palette.text().color()

        if isinstance(item_data, str) and item_data.lower().endswith('.nk'):
            if is_selected:
                background = QtGui.QColor("#4ddf8a")
                text_color = QtGui.QColor("black")
            else:
                background = QtGui.QColor("#215e3b")
                text_color = QtGui.QColor("white")
        elif is_selected:
            background = QtGui.QColor("#555555")
            text_color = QtGui.QColor("white")

        # Paint background
        painter.save()
        painter.fillRect(option.rect, background)

        # Text & icon
        icon = index.data(QtCore.Qt.DecorationRole)
        text = index.data(QtCore.Qt.DisplayRole)
        rect = option.rect.adjusted(5, 0, -5, 0)

        x_offset = 0
        if icon:
            icon_size = option.decorationSize
            icon.paint(painter, rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            x_offset = icon_size.width() + 6

        # Text
        painter.setPen(text_color)
        text_rect = rect.adjusted(x_offset, 0, 0, 0)
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, text)

        # Favorite icon on the right
        if is_favorite:
            star_path = os.path.join(os.path.dirname(__file__), "icon", "script", "star.png")
            if os.path.exists(star_path):
                star_icon = QtGui.QIcon(star_path)
                star_pixmap = star_icon.pixmap(16, 16)
                star_x = option.rect.right() - 20
                star_y = option.rect.center().y() - 8
                painter.drawPixmap(star_x, star_y, star_pixmap)

        painter.restore()

    def sizeHint(self, option, index):
        return super().sizeHint(option, index)


#__________________________________________________________
###########################################################    
class CustomListWidget(QtWidgets.QListWidget):
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            item = self.itemAt(event.pos())
            # Do NOT call super(), avoids selecting or changing focus
            if item:
                self.setCurrentItem(item)  # optional: show it selected
        else:
            super().mousePressEvent(event)


#__________________________________________________________
###########################################################
class ShotManagerUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ShotManagerUI, self).__init__(parent)
        self.setWindowTitle("ShotManager - Browser")
        self.setMinimumWidth(1400)
        self.setMinimumHeight(600)

        self.main_folder_path = mainFolderPath
        self.secondary_folder_path = secondaryFolderPath

        self.active_projects = []
        self.columns = []  # Store QLabel + QListWidget pairs

        self.default_button_style = """
            QPushButton {
                background-color: #2a2a2a;
                color: #888888;
                border: 1px solid #444;
                padding: 6px 12px;
            }
        """

        self.loadActiveProjects()
        self.loadFavorites()
        self.setupUI()
        self.populateRootColumn()

    def setupUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_layout = QtWidgets.QHBoxLayout()
        icon_path = os.path.join(os.path.dirname(__file__), "icon/shotManager.png")
        if os.path.exists(icon_path):
            icon_label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(icon_path)
            pixmap = pixmap.scaledToHeight(48, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            header_layout.addWidget(icon_label)
        header_label = QtWidgets.QLabel(shotmanagerWindowTitle)
        header_font = header_label.font()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        user_label = QtWidgets.QLabel(f"Logged in as: {getpass.getuser()}")
        user_label.setAlignment(QtCore.Qt.AlignRight)
        main_layout.addWidget(user_label)

        # Path and buttons
        path_layout = QtWidgets.QHBoxLayout()
        self.path_label = QtWidgets.QLabel(f"Main Folder: {self.main_folder_path}")
        path_layout.addWidget(self.path_label)

        self.change_folder_button = QtWidgets.QPushButton("Change Main Folder")
        self.change_folder_button.clicked.connect(self.changeMainFolder)
        path_layout.addWidget(self.change_folder_button)

        self.switch_folder_button = QtWidgets.QPushButton("Switch Between Primary/Secondary Folder")
        self.switch_folder_button.clicked.connect(self.switchMainFolder)
        path_layout.addWidget(self.switch_folder_button)
        path_layout.addStretch()
        main_layout.addLayout(path_layout)
        # Create a splitter to hold columns and favorites
        self.browser_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        # ---- Columns Layout ----
        self.columns_widget = QtWidgets.QWidget()
        self.columns_layout = QtWidgets.QHBoxLayout()
        self.columns_widget.setLayout(self.columns_layout)
        self.browser_splitter.addWidget(self.columns_widget)
        # ---- Favorites Layout ----
        self.fav_group = QtWidgets.QGroupBox("⭐ Favorites")
        self.fav_layout = QtWidgets.QHBoxLayout()
        self.fav_group.setLayout(self.fav_layout)
        self.browser_splitter.addWidget(self.fav_group)
        # Set initial sizes
        self.browser_splitter.setStretchFactor(0, 4)  # Browser gets more space
        self.browser_splitter.setStretchFactor(1, 1)
        # Add splitter to main layout
        main_layout.addWidget(self.browser_splitter)
        # Refresh favorites
        self.refreshFavoritesView()

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()

        self.selected_path_label = QtWidgets.QLabel("No file selected")
        self.selected_path_label.setWordWrap(True)
        bottom_layout.addWidget(self.selected_path_label)

        bottom_layout.addStretch()

        self.open_script_button = QtWidgets.QPushButton("Select a .nk Script")
        self.open_script_button.clicked.connect(self.openScript)
        self.open_script_button.setEnabled(False)
        self.open_script_button.setStyleSheet(self.default_button_style)
        bottom_layout.addWidget(self.open_script_button)

        main_layout.addLayout(bottom_layout)





#__________________________________________
    def refreshFavoritesView(self):
        # Clear old widgets
        while self.fav_layout.count():
            item = self.fav_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

        if not self.favorites:
            empty_label = QtWidgets.QLabel("No favorites yet. Right-click a folder to add.")
            self.fav_layout.addWidget(empty_label)
            return

        for show, paths in sorted(self.favorites.items()):
            col_widget = QtWidgets.QWidget()
            col_layout = QtWidgets.QVBoxLayout(col_widget)
            col_layout.setSpacing(2)
            col_layout.setContentsMargins(5, 5, 5, 5)
            label = QtWidgets.QLabel(f"<b>{show}</b>")
            col_layout.addWidget(label)

            for path in sorted(paths):
                base_name = os.path.basename(path)
                parent_name = os.path.basename(os.path.dirname(path))
                display_name = f"{parent_name}/{base_name} "
                row_widget = QtWidgets.QWidget()
                row_layout = QtWidgets.QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(5)

                # Main Favorite Button
                fav_btn = QtWidgets.QPushButton(display_name)
                fav_btn.setFixedHeight(24)
                fav_btn.setToolTip(path)
                fav_btn.setStyleSheet("QPushButton { text-align: left; }")
                fav_btn.clicked.connect(lambda checked=False, p=path: self.openFavoritePath(p))

                # Remove Button
                remove_btn = QtWidgets.QPushButton("✕")
                remove_btn.setFixedSize(24, 24)
                remove_btn.setToolTip("Remove from Favorites")
                remove_btn.setStyleSheet("""
                    QPushButton {
                        color: red;
                        background: none;
                        border: none;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #330000;
                    }
                """)
                remove_btn.clicked.connect(lambda checked=False, p=path: self.removeFavorite(p))

                row_layout.addWidget(fav_btn)
                row_layout.addWidget(remove_btn)
                col_layout.addWidget(row_widget)

            self.fav_layout.addWidget(col_widget)
            self.fav_layout.setAlignment(col_widget, QtCore.Qt.AlignTop)





#__________________________________________
    def removeFavorite(self, path):
        path = os.path.normpath(path)
        updated = False

        for show, paths in list(self.favorites.items()):
            if path in paths:
                self.favorites[show].remove(path)
                if not self.favorites[show]:
                    del self.favorites[show]
                updated = True
                break

        if updated:
            self.saveFavorites()
            self.refreshFavoritesView()
            self.refreshColumnsContainingPath(path)  # Force UI star update




#____________________________________________________
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clearLayout(child.layout())


    def pulseItem(self, list_widget, item):
        rect = list_widget.visualItemRect(item)
        effect = QtWidgets.QGraphicsColorizeEffect()
        effect.setColor(QtGui.QColor("#00ff88"))
        effect.setStrength(0.0)

        anim = QtCore.QPropertyAnimation(effect, b"strength", list_widget)
        anim.setStartValue(0.0)
        anim.setKeyValueAt(0.5, 1.0)
        anim.setEndValue(0.0)
        anim.setDuration(700)
        anim.start()

        # Attach effect and animation to keep them alive
        item_widget = list_widget.itemWidget(item)
        if not item_widget:
            proxy = QtWidgets.QWidget()
            list_widget.setItemWidget(item, proxy)
            item_widget = proxy

        item_widget.setGraphicsEffect(effect)
        anim.finished.connect(lambda: item_widget.setGraphicsEffect(None))



#__________________________________________
    def openFavoritePath(self, path):
        if not os.path.isdir(path):
            return

        path = os.path.normpath(path)
        rel_path = os.path.relpath(path, self.main_folder_path)
        parts = rel_path.split(os.sep)

        self.clearColumnsFrom(0)

        # Add root column
        try:
            entries = [
                (f, os.path.join(self.main_folder_path, f))
                for f in sorted(os.listdir(self.main_folder_path))
                if os.path.isdir(os.path.join(self.main_folder_path, f))
            ]
            self.addColumn(os.path.basename(self.main_folder_path), entries)
        except Exception as e:
            print(f"[ShotManager] Failed to add root column: {e}")
            return

        current_path = self.main_folder_path

        for i, part in enumerate(parts):
            current_path = os.path.join(current_path, part)
            if not os.path.exists(current_path):
                break

            if i < len(parts) - 1:
                # Add column for intermediate folders
                try:
                    entries = [
                        (f, os.path.join(current_path, f))
                        for f in sorted(os.listdir(current_path))
                    ]
                    self.addColumn(os.path.basename(current_path), entries)
                except Exception as e:
                    print(f"[ShotManager] Failed to add column for {current_path}: {e}")
                    break
            else:
                # Final part — just select the item in previous column
                if self.columns:
                    prev_list = self.columns[-1][1]
                    for j in range(prev_list.count()):
                        item = prev_list.item(j)
                        if os.path.normpath(item.data(QtCore.Qt.UserRole)) == current_path:
                            prev_list.setCurrentItem(item)
                            self.pulseItem(prev_list, item)
                            break

        # Refresh star icons on all list items
        self.refreshFavoritesView()
        for _, list_widget in self.columns:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                data = item.data(QtCore.Qt.UserRole)
                item.setData(QtCore.Qt.UserRole + 1, self.isFavorite(data))
            list_widget.viewport().update()

        



#_________________________________________________________
    def populateRootColumn(self):
        self.clearColumnsFrom(0)
        try:
            items = []
            for item in os.listdir(self.main_folder_path):
                path = os.path.join(self.main_folder_path, item)
                if os.path.isdir(path):
                    items.append((item, path))
            self.addColumn(os.path.basename(self.main_folder_path), items)
        except Exception as e:
            print(f"[ShotManager] Error reading main folder: {e}")



#_________________________________________________________
    def addColumn(self, folder_label, entries):
        print(f"[ShotManager] Adding column for: {folder_label} with {len(entries)} entries.")

        # --- Column UI Setup ---
        col_layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(folder_label)
        label.setAlignment(QtCore.Qt.AlignCenter)

        list_widget = CustomListWidget()
        list_widget.setItemDelegate(ScriptItemDelegate())
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #dddddd;
            }
        """)
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        list_widget.itemSelectionChanged.connect(self.onItemSelected)
        list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.showContextMenu)

        col_layout.addWidget(label)
        col_layout.addWidget(list_widget)
        self.columns_layout.addLayout(col_layout)
        self.columns.append((label, list_widget))

        # --- Icon Paths ---
        icon_dir = os.path.join(os.path.dirname(__file__), "icon", "script")

        for text, data in sorted(entries):
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, data)
            item.setData(QtCore.Qt.UserRole + 1, self.isFavorite(data))  # ⭐ Important for star icon rendering

            icon_path = None

            if data is None:
                item.setFlags(QtCore.Qt.NoItemFlags)
                item.setForeground(QtGui.QColor("white"))
                font = item.font()
                font.setItalic(True)
                item.setFont(font)

            elif isinstance(data, str):
                if os.path.isdir(data):
                    is_active = len(self.columns) == 1 and text in self.active_projects

                    # Icon handling for folders
                    icon_path = os.path.join(icon_dir, "folder_active.png") if is_active else os.path.join(icon_dir, "folder.png")
                    if os.path.exists(icon_path):
                        item.setIcon(QtGui.QIcon(icon_path))

                    if is_active:
                        item.setBackground(QtCore.Qt.black)
                        item.setForeground(QtCore.Qt.white)
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

                elif os.path.isfile(data):
                    if data.lower().endswith(".nk"):
                        icon_path = os.path.join(icon_dir, "nuke.png")
                        item.setBackground(QtGui.QColor("#215e3b"))  # dark green
                        item.setForeground(QtGui.QColor("white"))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    else:
                        icon_path = os.path.join(icon_dir, "file.png")

                # Apply icon if it exists
                if icon_path and os.path.exists(icon_path):
                    item.setIcon(QtGui.QIcon(icon_path))

            list_widget.addItem(item)
            list_widget.itemClicked.connect(self.onItemClickedForFavorite)

        # Only one viewport update after all items are added
        list_widget.viewport().update()



#_________________________________________________________
    def showContextMenu(self, position):
        list_widget = self.sender()
        item = list_widget.itemAt(position)

        if not item:
            print("[ContextMenu] No item under cursor.")
            return

        path = item.data(QtCore.Qt.UserRole)
        if not path or not os.path.isdir(path):
            print(f"[ContextMenu] Invalid or non-folder path: {path}")
            return

        # Normalize path once
        path = os.path.normpath(path)

        # Create context menu
        menu = QtWidgets.QMenu()

        is_fav = self.isFavorite(path)
        if is_fav:
            fav_action = menu.addAction("❌ Remove from Favorites")
        else:
            fav_action = menu.addAction("⭐ Add to Favorites")

        # Show the menu and get the clicked action
        action = menu.exec_(list_widget.viewport().mapToGlobal(position))

        if action == fav_action:
            print(f"[ContextMenu] Toggling favorite for: {path}")
            self.toggleFavorite(path)
            self.refreshFavoritesView()
            self.refreshColumnsContainingPath(path)




#_________________________________________________________
    def refreshColumnsContainingPath(self, path):
        norm_path = os.path.normpath(path)
        for label, list_widget in self.columns:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item_path = os.path.normpath(item.data(QtCore.Qt.UserRole))
                if item_path == norm_path:
                    item.setData(QtCore.Qt.UserRole + 1, self.isFavorite(item_path))
            list_widget.viewport().update()




#_________________________________________________________
    def rebuildCurrentColumns(self):
        """Rebuild the columns while preserving current selection path"""
        if not self.columns:
            return

        # Rebuild from currently selected folder
        for i in reversed(range(len(self.columns))):
            label, list_widget = self.columns[i]
            selected_items = list_widget.selectedItems()
            if selected_items:
                selected_item = selected_items[0]
                path = selected_item.data(QtCore.Qt.UserRole)
                if os.path.isdir(path):
                    entries = [(f, os.path.join(path, f)) for f in sorted(os.listdir(path))]
                    self.clearColumnsFrom(i + 1)
                    self.addColumn(os.path.basename(path), entries)
                    self.columns[-1][1].viewport().update()
                    list_widget.viewport().update()
                break



#_________________________________________________________
    def onItemClickedForFavorite(self, item):
        if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            path = item.data(QtCore.Qt.UserRole)
            if path and os.path.isdir(path):
                self.toggleFavorite(path)
                self.refreshFavoritesView()



#_________________________________________________________
    def loadFavorites(self):
        import json  # Make sure it's imported
        fav_file = os.path.join(os.path.dirname(__file__), f"favorites_{username}.json")
        self.favorites = {}  # Default

        if os.path.exists(fav_file):
            try:
                with open(fav_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.favorites = json.loads(content)
                    else:
                        print("[ShotManager] Empty favorites file, starting fresh.")
            except Exception as e:
                print(f"[ShotManager] Error reading favorites.json: {e}")
                self.favorites = {}
        else:
            print("[ShotManager] No favorites file found, starting fresh.")





#_________________________________________________________
    def saveFavorites(self):
        import json
        fav_file = os.path.join(os.path.dirname(__file__), f"favorites_{username}.json")
        os.makedirs(os.path.dirname(fav_file), exist_ok=True)
        try:
            with open(fav_file, 'w') as f:
                json.dump(self.favorites, f, indent=2)
        except Exception as e:
            print(f"[ShotManager] Failed to save favorites: {e}")




#_________________________________________________________
    def toggleFavorite(self, path):
        path = os.path.normpath(path)
        parts = path.split(os.sep)

        # Try to find a parent show name
        show_name = None

        # Match against folders like "SHOTS" or "ASSETS" and take the one before as the show name
        for i in range(1, len(parts)):
            if parts[i] in ("SHOTS", "ASSETS"):
                show_name = parts[i - 1]
                break

        # Fallback: use top-level show name from inside main_folder_path
        if not show_name and self.main_folder_path in path:
            rel_path = os.path.relpath(path, self.main_folder_path)
            show_name = rel_path.split(os.sep)[0] if os.sep in rel_path else rel_path

        # Final fallback
        if not show_name:
            show_name = "Misc"

        # Create group if needed
        self.favorites.setdefault(show_name, [])

        if path in self.favorites[show_name]:
            self.favorites[show_name].remove(path)
            if not self.favorites[show_name]:
                del self.favorites[show_name]
        else:
            self.favorites[show_name].append(path)

        self.saveFavorites()
        self.refreshFavoritesView()
        self.rebuildCurrentColumns()




#________________________________________________________
    def isFavorite(self, path):
        if not path or not isinstance(path, str):
            return False
        norm_path = os.path.normpath(path)
        return any(norm_path == os.path.normpath(fav) for favs in self.favorites.values() for fav in favs)





#__________________________________________
    def clearColumnsFrom(self, index):
        """Remove all columns starting at a given index"""
        while len(self.columns) > index:
            label, widget = self.columns.pop()
            widget.deleteLater()
            label.deleteLater()




#______________________________________________________
    def onItemSelected(self):
        """Determine which list triggered this and generate the next column or handle file selection"""
        sender_index = None
        for i, (_, list_widget) in enumerate(self.columns):
            if list_widget.hasFocus():
                sender_index = i
                break

        if sender_index is None:
            return

        selected_items = self.columns[sender_index][1].selectedItems()
        self.clearColumnsFrom(sender_index + 1)
        self.open_script_button.setEnabled(False)
        self.open_script_button.setText("Select a .nk Script")
        self.open_script_button.setStyleSheet(self.default_button_style)
        self.selected_path_label.setText("No file selected")

        if not selected_items:
            return

        selected_item = selected_items[0]
        path = selected_item.data(QtCore.Qt.UserRole)

        if path is None:
            return

        if os.path.isfile(path):
            self.selected_path_label.setText(f"Selected: {path}")
            if path.lower().endswith('.nk'):
                self.open_script_button.setText("Open .nk Script")
                self.open_script_button.setEnabled(True)
                self.open_script_button.setStyleSheet("""
                    QPushButton {
                        background-color: darkGrey;
                        color: black;
                        border: 1px solid #444;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #aa2222;
                    }
                """)
            else:
                self.open_script_button.setText("Select a .nk file to open")
                self.open_script_button.setEnabled(False)
            return

        if not os.path.isdir(path):
            self.open_script_button.setText("Select a .nk file to open")
            self.open_script_button.setEnabled(False)
            return

        # Load sub-items
        entries = []
        for item in sorted(os.listdir(path)):
            subpath = os.path.join(path, item)
            if os.path.isdir(subpath) or os.path.isfile(subpath):
                entries.append((item, subpath))

        if entries:
            self.addColumn(os.path.basename(path), entries)
        else:
            self.addColumn(os.path.basename(path), [("[This Folder is empty... ]", None)])





#____________________________________________________________
    def switchMainFolder(self):
        self.main_folder_path, self.secondary_folder_path = self.secondary_folder_path, self.main_folder_path
        self.path_label.setText(f"Main Folder: {self.main_folder_path}")
        self.loadActiveProjects()
        self.populateRootColumn()

    def changeMainFolder(self):
        new_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Main Folder", self.main_folder_path)
        if new_path and self.setMainFolderPath(new_path):
            self.loadActiveProjects()
            QtWidgets.QMessageBox.information(self, "Success", f"Main folder changed to:\n{new_path}")

    def setMainFolderPath(self, path):
        if os.path.isdir(path):
            self.main_folder_path = path
            self.path_label.setText(f"Main Folder: {self.main_folder_path}")
            self.populateRootColumn()
            return True
        return False

    def populateRootColumn(self):
        self.clearColumnsFrom(0)
        try:
            items = []
            for item in os.listdir(self.main_folder_path):
                path = os.path.join(self.main_folder_path, item)
                if os.path.isdir(path):
                    items.append((item, path))
            print(f"[ShotManager] Found {len(items)} top-level folders.")
            self.addColumn(os.path.basename(self.main_folder_path), items)
        except Exception as e:
            print(f"[ShotManager] Error reading main folder: {e}")




#_________________________________________________________
    def openScript(self):
        """Open the selected NUKE script"""
        if not self.columns:
            return

        last_list = self.columns[-1][1]
        selected_items = last_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a NUKE script to open.")
            return

        selected_item = selected_items[0]
        script_path = selected_item.data(QtCore.Qt.UserRole)

        if not script_path or not script_path.lower().endswith('.nk'):
            QtWidgets.QMessageBox.warning(self, "Invalid Selection", "Please select a valid .nk file to open.")
            return

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
            nuke.scriptClear()
            nuke.scriptOpen(script_path)
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Successfully opened:\n{os.path.basename(script_path)}\n\nFrom: {script_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open script:\n{str(e)}")




#_________________________________________________________
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


contactLR = "loucas.rongeart@gmail.com"
#__________________________________________________________
###########################################################
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
        It provides a column-based browser interface to quickly locate and open NUKE scripts across your project folders.</p>

        <h3>Interface Layout</h3>
        <ul>
            <li><strong>Top Panel:</strong> Set or switch between your main and secondary folder roots.</li>
            <li><strong>Column Browser:</strong> Dynamically updates as you navigate folders. Up to 4 columns may appear:
                <ul>
                    <li><strong>Column 1:</strong> Shows all projects in the root folder</li>
                    <li><strong>Column 2:</strong> Category level like SHOTS or ASSETS</li>
                    <li><strong>Column 3:</strong> Individual asset or shot folder</li>
                    <li><strong>Column 4:</strong> Files inside the selected folder</li>
                </ul>
            </li>
            <li><strong>Favorites Bar:</strong> Displays saved favorite paths with buttons to jump back to them</li>
            <li><strong>Status Panel:</strong> Shows the selected path and allows opening NUKE scripts</li>
        </ul>

        <h3>How to Use</h3>
        <ol>
            <li><strong>Browse:</strong> Click folders in sequence to explore your projects</li>
            <li><strong>Set Favorite:</strong> <kbd>Right-click</kbd> or <kbd>Ctrl+click</kbd> a folder and choose "⭐ Add to Favorites"</li>
            <li><strong>Remove Favorite:</strong> Use the ❌ icon in the favorites bar or right-click again</li>
            <li><strong>Open Scripts:</strong> Click a .nk file and then "Open NUKE Script"</li>
        </ol>

        <h3>Features</h3>
        <ul>
            <li><strong>Favorites Panel:</strong> Quickly jump to frequently used folders with one click</li>
            <li><strong>Star Icons:</strong> A small star appears on the right of folders marked as favorites</li>
            <li><strong>Favorites Grouping:</strong> Automatically grouped by show name (e.g., SHOW_A, Misc)</li>
            <li><strong>Pulse Feedback:</strong> When clicking a favorite, a glow effect confirms the jump</li>
            <li><strong>Folder State:</strong> Empty folders show a greyed "[ This Folder is empty... ]" entry</li>
            <li><strong>Active Project Highlight:</strong> Projects listed in 'live_projects.json' appear in bold black</li>
            <li><strong>Script Detection:</strong> NUKE scripts (.nk) are highlighted in green and bold</li>
            <li><strong>Customizable Paths:</strong> You can set your default paths in the script or dynamically in the UI</li>
        </ul>

        <h3>Configuration</h3>
        <ul>
            <li><strong>Main Folder:</strong> Defaults to <code>E:/SHOWS</code>, but can be changed via the UI</li>
            <li><strong>Secondary Folder:</strong> Toggle with the "Switch Folder" button (e.g., E:/01_PROJECTS)</li>
            <li><strong>Active Projects:</strong> Controlled via a <code>live_projects.json</code> file</li>
            <li><strong>Favorites Storage:</strong> Saved in <code>favorites_[username].json</code> in the ShotManager folder</li>
        </ul>

        <h3>Expected Folder Structure</h3>
        <pre>
        Main Folder
        ├── SHOW_A/
        │   ├── SHOTS/
        │   │   └── SEQ01_SH010/
        │   │       └── nuke/
        │   │           └── SHOT_template_script_v01.nk
        │   └── ASSETS/
        │       └── chrHero/
        │           └── nuke/
        │               └── ASSET_template_script_v01.nk
        │       
>       │  
        ├── SHOW_B/
        │   ├── ... (similar structure as SHOW_A)
        </pre>

        <h3>Tips & Shortcuts</h3>
        <ul>
            <li>Use <kbd>Ctrl+Click</kbd> on any folder to instantly add/remove it from favorites</li>
            <li>You can reorder or remove favorite paths via the favorites bar</li>
            <li>If a folder is empty, a placeholder item will be displayed</li>
            <li>Favorite folders always show a small star on the right</li>
            <li>Clicking a favorite rebuilds all columns to reveal it</li>
            <li>The "Open NUKE Script" button becomes active and styled when a .nk file is selected</li>
        </ul>

        <h3>Troubleshooting</h3>
        <ul>
            <li><strong>Favorites not saving:</strong> Check write permissions in your script folder</li>
            <li><strong>Missing live_projects.json:</strong> Create it in <code>~/.nuke/shotmanager</code> or script directory</li>
            <li><strong>Script won't open:</strong> Check if your current NUKE session already has a script open (you'll be prompted)</li>
        </ul>

        <hr>
        <p><em>For questions or feature requests, contact Loucas RONGEART – <a href="mailto:{contactLR}">{contactLR}</a></em></p>
        <p><em>ShotManager {shotmanagerVersion}</em></p>
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
