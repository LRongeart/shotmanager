import nuke
import sys
import os

# Add .nuke/shotmanager to sys.path so we can import shotmanager
shotmanager_path = os.path.join(os.path.dirname(__file__), "shotmanager")
if shotmanager_path not in sys.path:
    sys.path.append(shotmanager_path)

# Add shortcut to access shotmanager:
shotmanager_key = "F10"

try:
    # Try importing from .nuke/shotmanager/shotmanager_ui.py
    import shotmanager
    from shotmanager import shotmanager_ui
except ImportError as e:
    nuke.tprint(f"[ShotManager] Failed to import shotmanager_ui: {e}")
    shotmanager = None

menu = nuke.menu("Nuke")
shotmanager_menu = menu.findItem("ShotManager") or menu.addMenu("ShotManager")
shotmanager_menu.addCommand("Launch ShotManager", "shotmanager_ui.launch_shotmanager_ui()", shotmanager_key, icon="ShotManager.png")
shotmanager_menu.addSeparator()
shotmanager_menu.addCommand("Help for ShotManager", "shotmanager_ui.launch_help_window()", icon="info_icon.png")