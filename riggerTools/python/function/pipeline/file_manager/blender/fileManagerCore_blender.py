# Qt Abstraction to support PySide2 or PySide6
try:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMenu, QInputDialog, QMessageBox, QAction
    from PySide2.QtCore import Qt, QSize, QDir, QSortFilterProxyModel
    from PySide2.QtGui import QIcon, QPixmap
except ImportError:
    try:
        from PySide6 import QtWidgets, QtGui, QtCore
        from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMenu, QInputDialog, QMessageBox
        from PySide6.QtGui import QAction, QIcon, QPixmap
        from PySide6.QtCore import Qt, QSize, QDir, QSortFilterProxyModel
        # Handle Some PySide6 differences if needed
    except ImportError:
        # Fallback if neither is installed
        pass

import json
import os
import subprocess
import sys
import re
import fnmatch
import logging

import bpy

# UI Shim to make fileManagerMainUI (PySide2) compatible with PySide6
if 'PySide6' in sys.modules:
    import PySide6.QtWidgets as QtWidgets
    import PySide6.QtGui as QtGui
    import PySide6.QtCore as QtCore
    # Add PySide2 module to sys.modules pointing to PySide6 to fool the generated UI
    sys.modules['PySide2'] = sys.modules['PySide6']
    sys.modules['PySide2.QtWidgets'] = sys.modules['PySide6.QtWidgets']
    sys.modules['PySide2.QtGui'] = sys.modules['PySide6.QtGui']
    sys.modules['PySide2.QtCore'] = sys.modules['PySide6.QtCore']

# UI Import
try:
    from function.pipeline.file_manager.file_manager_ui import fileManagerMainUI
except ImportError:
    # If standard import fails, try to find it relative to current script
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    from function.pipeline.file_manager.file_manager_ui import fileManagerMainUI

# Logger setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FileManagerBlender")

# --- Config and Constants ---
user_home = os.path.expanduser("~")
config_directory = os.path.join(user_home, 'Documents', 'maya', 'scripts') # Reusing existing config location
config_file = 'fileManager_config.py'
file_path = os.path.join(config_directory, config_file)

CORE_VERSION = '0.9.7-blender'
THUMBNAIL_NAME = 'thumb.png'
PADDING = 4

if os.path.exists(file_path):
    sys.path.insert(0, config_directory)
    try:
        import fileManager_config as config
        import importlib
        importlib.reload(config)
        DRIVES = config.DRIVES
        PROJECT_NAME = config.PROJECT_NAME
        DICTIONARY_TEMPLATE = config.DICTIONARY_TEMPLATE
        BASE_FOLDER = config.BASE_FOLDER
        ASSET_TOP_FOLDER = config.ASSET_TOP_FOLDER
        SCENE_TOP_FOLDER = config.SCENE_TOP_FOLDER
        DEPT_NAME = config.DEPT_NAME
        DEPT_EMPTY = config.DEPT_EMPTY
        JOB_TEMPLATE = config.JOB_TEMPLATE
        EXCLUDE_VIEW_ITEM = config.EXCLUDE_VIEW_ITEM
        STATIC_FOLDER = config.STATIC_FOLDER
        DEFAULT_PROJECT = config.DEFAULT_PROJECT
        USE_VARIATION = config.USE_VARIATION
        SVN_BIN_PATH = config.SVN_BIN_PATH
        HIDE_FORMAT = config.HIDE_FORMAT
        FIXED_PROJECT_PATHS = getattr(config, 'FIXED_PROJECT_PATHS', {})
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        # Default Fallbacks
        DRIVES = ["D:\\", "E:\\"]
        PROJECT_NAME = ['P_sample','Project_A']
        BASE_FOLDER = "projects"
        ASSET_TOP_FOLDER = "Content"
        SCENE_TOP_FOLDER = "Sequence"
        DEFAULT_PROJECT = 'Project_A'
        SVN_BIN_PATH = r"C:\Program Files\TortoiseSVN\bin"
        FIXED_PROJECT_PATHS = {}
else:
    # Default Fallbacks
    DRIVES = ["D:\\", "E:\\"]
    PROJECT_NAME = ['P_sample','Project_A']
    DICTIONARY_TEMPLATE = {"base_path":"","entitie_type":"","entitie_name":"","full_entity_name":"","comment":"","department_name":"","add_path_SVN":""}
    BASE_FOLDER = "projects"
    ASSET_TOP_FOLDER = "Content"
    SCENE_TOP_FOLDER = "Sequence"
    DEPT_NAME = ['Model', 'Rig', 'Anim']
    DEPT_EMPTY = ['Commit','Texture', 'ConceptArt','FBX']
    JOB_TEMPLATE = ['Version', 'Data', 'Output', 'Commit', 'FBX']
    EXCLUDE_VIEW_ITEM = ['data.json', THUMBNAIL_NAME, 'Commit', '_Backup', '_Bakup', '_backup', '_bakup']
    STATIC_FOLDER = [ASSET_TOP_FOLDER, 'Version', 'Commit']
    DEFAULT_PROJECT = 'Project_A'
    USE_VARIATION = ('Project_A')
    SVN_BIN_PATH = r"C:\Program Files\TortoiseSVN\bin"
    HIDE_FORMAT = ['*.pyc', '*.o']
    FIXED_PROJECT_PATHS = {}

BLENDER_EXT = 'blend'

class SvnBlender:
    def __init__(self):
        pass
    def execute_cmd(self, cmd_type, file_path, close_on_end, add_fixed_folder=False, logmsg=''):
        file_path = os.path.normpath(file_path)
        if add_fixed_folder == False:
            command_line = r'cd "{0}" && TortoiseProc.exe /command:{1} /path:"{2}" /logmsg:"{4}" /closeonend:{3}'.format(SVN_BIN_PATH, cmd_type, file_path, close_on_end, logmsg)
        else:
            command_line = r'cd "{0}" && TortoiseProc.exe /command:{1} /path:"{2}" /closeonend:{3} /logmsg:"{4}" --depth=files /nodlg'.format(SVN_BIN_PATH, cmd_type, file_path, close_on_end, logmsg)
        subprocess.run(command_line, shell=True)

class FileManagerBlender(fileManagerMainUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(FileManagerBlender, self).__init__()
        self.setupUi(self)
        self.path = None
        
        # Asset Model setup
        self.asset_fs_model = QtWidgets.QFileSystemModel(self)
        self.asset_proxy = QtCore.QSortFilterProxyModel(self)
        self.asset_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.asset_proxy.setFilterKeyColumn(0)
        if hasattr(self.asset_proxy, "setRecursiveFilteringEnabled"):
            self.asset_proxy.setRecursiveFilteringEnabled(True)

        self.setObjectName("FileManager")
        self.setWindowTitle(f"Blender File Manager {CORE_VERSION}")
        self.svn_tool = SvnBlender()

        self.populate_drives()
        self.populate_project()
        
        logger.debug('Set default project...')
        self.drive_comboBox.setCurrentText(DRIVES[0])
        self.project_comboBox.setCurrentText(DEFAULT_PROJECT)

        self.setupMenuBar()
        self.entite_TAB.setCurrentIndex(0)  
        self.drive_comboBox.currentIndexChanged.connect(self.update_project_comboBox)
        self.populate_ASSET_treeView()
        self.project_comboBox.currentIndexChanged.connect(self.populate_ASSET_treeView)	

        self.asset_dir_TREEVIEW.clicked.connect(self.on_treeview_clicked)
        self.asset_department_listWidget.itemClicked.connect(self.on_department_clicked)
        self.asset_version_view_listWidget.itemClicked.connect(self.on_version_clicked)
        self.populate_SCENE_treeView()
        self.dir_scene_TREEVIEW.clicked.connect(self.on_treeview_SCENE_clicked)
        self.asset_global_listWidget.itemClicked.connect(self.on_glogal_commit_clicked)

        # Context Menus
        self.asset_department_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.asset_department_listWidget.customContextMenuRequested.connect(self.show_job_context_menu)
        self.asset_version_view_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.asset_version_view_listWidget.customContextMenuRequested.connect(self.show_step_context)
        self.asset_global_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.asset_global_listWidget.customContextMenuRequested.connect(self.handle_right_click_global_widget)
        self.asset_local_view_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.asset_local_view_listWidget.customContextMenuRequested.connect(self.handle_right_click_local_widget)
        self.asset_dir_TREEVIEW.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.asset_dir_TREEVIEW.customContextMenuRequested.connect(self.show_context_menu)

        # Double Clicks
        self.asset_version_view_listWidget.itemDoubleClicked.connect(self.handle_double_click)
        self.asset_local_view_listWidget.itemDoubleClicked.connect(self.handle_double_click_local_widget)
        self.asset_global_listWidget.itemDoubleClicked.connect(self.handle_double_click_global_widget)

        # Buttons
        self.asset_localCommit_BTN.clicked.connect(self.push_btn_local_publish)
        self.asset_commit_BTN.clicked.connect(self.push_btn_global_publish)

        # Sync UI to active Blender file
        self.check_exists_blender()

        # Apply premium dark theme
        self.apply_dark_theme()

    def apply_dark_theme(self):
        dark_stylesheet = """
        QMainWindow {
            background-color: #353535;
            color: #e0e0e0;
            font-family: 'Segoe UI', 'Outfit', Helvetica, sans-serif;
            font-size: 10pt;
        }
        
        QWidget {
            color: #e0e0e0;
            background-color: #353535;
        }
        
        QMenuBar {
            background-color: #2b2b2b;
            border-bottom: 1px solid #222222;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 10px;
            color: #b0b0b0;
        }
        
        QMenuBar::item:selected {
            background-color: #444444;
            color: #ffffff;
            border-radius: 4px;
        }
        
        QMenu {
            background-color: #2b2b2b;
            border: 1px solid #222222;
            border-radius: 4px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 6px 20px;
            border-radius: 2px;
            color: #e0e0e0;
        }
        
        QMenu::item:selected {
            background-color: #d29a2e;
            color: #000000;
        }
        
        QTabWidget::pane {
            border: 1px solid #222222;
            border-radius: 4px;
            background-color: #353535;
            top: -1px;
        }
        
        QTabBar::tab {
            background-color: #2b2b2b;
            border: 1px solid #222222;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            color: #a0a0a0;
        }
        
        QTabBar::tab:selected {
            background-color: #353535;
            color: #ffffff;
            border-bottom: 2px solid #d29a2e;
        }
        
        QTabBar::tab:hover {
            color: #ffffff;
            background-color: #303030;
        }
        
        QTreeView, QListWidget, QListView {
            background-color: #212121;
            border: 1px solid #2c2c2c;
            border-radius: 4px;
            padding: 2px;
            color: #e0e0e0;
            outline: none;
        }
        
        QHeaderView::section {
            background-color: #5d5d5d;
            color: #ffffff;
            padding: 4px 6px;
            border: 1px solid #2b2b2b;
            font-weight: normal;
        }
        
        QHeaderView {
            background-color: #2b2b2b;
            border: none;
        }
        
        QTreeView::item, QListWidget::item {
            padding: 4px;
            border-radius: 2px;
        }
        
        QTreeView::item:hover, QListWidget::item:hover {
            background-color: #2e2e2e;
            color: #ffffff;
        }
        
        QTreeView::item:selected, QListWidget::item:selected {
            background-color: #4e4e4e;
            color: #ffffff;
            border-left: 3px solid #d29a2e;
        }
        
        QComboBox {
            background-color: #2b2b2b;
            border: 1px solid #222222;
            border-radius: 4px;
            padding: 4px 8px;
            color: #e0e0e0;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #222222;
        }
        
        QComboBox QAbstractItemView {
            background-color: #212121;
            border: 1px solid #222222;
            selection-background-color: #d29a2e;
            selection-color: #000000;
            color: #e0e0e0;
            outline: none;
        }
        
        QLineEdit {
            background-color: #212121;
            border: 1px solid #2c2c2c;
            border-radius: 4px;
            padding: 4px 8px;
            color: #e0e0e0;
        }
        
        QLineEdit:focus {
            border: 1px solid #d29a2e;
        }
        
        QPushButton {
            background-color: #4e4e4e;
            border: 1px solid #2c2c2c;
            border-radius: 4px;
            padding: 6px 12px;
            color: #e0e0e0;
        }
        
        QPushButton:hover {
            background-color: #5c5c5c;
            border: 1px solid #d29a2e;
            color: #ffffff;
        }
        
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #212121;
            width: 8px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #4e4e4e;
            min-height: 20px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #d29a2e;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QGroupBox {
            border: 1px solid #2c2c2c;
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 8px;
            color: #a0a0a0;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0px 3px;
        }
        
        QLabel {
            color: #a0a0a0;
        }
        
        QDialog {
            background-color: #353535;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def is_scene_open(self):
        return bool(bpy.data.filepath)

    def setupMenuBar(self):
        file_menu = self.menuFile
        
        create_thumbnail_action = QAction("Create Thumbnail", self)
        create_thumbnail_action.triggered.connect(self.create_thumbnail)
        file_menu.addAction(create_thumbnail_action)

        link_ref_action = QAction("Link Selected Collection", self)
        link_ref_action.triggered.connect(self.handle_link_global_widget)
        file_menu.addAction(link_ref_action)

    def link_blender_file(self, filepath):
        if not os.path.exists(filepath): return
        try:
            with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
                data_to.collections = data_from.collections
            for coll in data_to.collections:
                if coll:
                    bpy.context.scene.collection.children.link(coll)
            logger.info(f"Linked collections from {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Link Failed", str(e))

    def handle_link_version_widget(self):
        file_path = self.get_deep_path()
        self.link_blender_file(file_path)

    def handle_link_global_widget(self):
        file_path = self.get_deep_path_global_commit()
        self.link_blender_file(file_path)

    def handle_link_local_widget(self):
        file_path = self.get_deep_path_local_commit()
        self.link_blender_file(file_path)

    def handle_double_click(self, item):
        file_path = self.get_deep_path()
        self.blender_open(file_path)

    def handle_double_click_global_widget(self, item):
        full_path = self._get_full_path()
        global_commit = self.asset_global_listWidget.currentItem()
        if not global_commit: return
        file_path = os.path.normpath(os.path.join(full_path, STATIC_FOLDER[2], global_commit.text()))
        self.blender_open(file_path)

    def handle_double_click_local_widget(self, item):
        file_path = self.get_deep_path_local_commit()
        if not file_path: return
        self.blender_open(file_path)

    def blender_open(self, file_path):
        if bpy.data.is_dirty:
            current_scene_name = os.path.basename(bpy.data.filepath) if bpy.data.filepath else "Untitled"
            reply = QMessageBox.question(
                self,
                'Save Changes',
                'Current file has unsaved changes. Do you want to save? {0}'.format(current_scene_name),
                QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No
            )
            if reply == QMessageBox.Save:
                if bpy.data.filepath:
                    bpy.ops.wm.save_mainfile()
                else:
                    bpy.ops.wm.save_as_mainfile(filepath=file_path)
            elif reply == QMessageBox.Cancel:
                return

        bpy.ops.wm.open_mainfile(filepath=file_path)
        self.check_exists_blender()

    def create_thumbnail(self):
        filepath = bpy.data.filepath
        if not filepath:
            QMessageBox.warning(self, "Warning", "Save file first!")
            return
        
        save_dir = os.path.dirname(filepath)
        save_path = os.path.join(save_dir, THUMBNAIL_NAME)
        
        # Blender Render Thumbnail
        bpy.context.scene.render.filepath = save_path
        
        # Find a 3D Viewport area and window region to override context (since we are called from PySide UI)
        view3d_area = None
        view3d_win = None
        for win in bpy.context.window_manager.windows:
            if win.screen:
                for area in win.screen.areas:
                    if area.type == 'VIEW_3D':
                        view3d_area = area
                        view3d_win = win
                        break
                if view3d_area:
                    break
        
        if view3d_area:
            view3d_region = None
            for region in view3d_area.regions:
                if region.type == 'WINDOW':
                    view3d_region = region
                    break
            
            if hasattr(bpy.context, "temp_override"):
                with bpy.context.temp_override(window=view3d_win, area=view3d_area, region=view3d_region):
                    bpy.ops.render.opengl(write_still=True)
            else:
                # Fallback for Blender < 3.2
                override = bpy.context.copy()
                override['window'] = view3d_win
                override['area'] = view3d_area
                if view3d_region:
                    override['region'] = view3d_region
                bpy.ops.render.opengl(override, write_still=True)
        else:
            bpy.ops.render.opengl(write_still=True)
            
        logger.info(f"Thumbnail created at {save_path}")

        save_full_path = os.path.normpath(save_path)
        reply = QMessageBox(self)
        reply.setWindowTitle('Commit Changes')
        reply.setText('Do you want to commit thumbnail to SVN ?\n\t')

        commit_button = reply.addButton('Commit', QMessageBox.AcceptRole)
        save_button = reply.addButton('Just Save', QMessageBox.AcceptRole)
        reply.addButton(QMessageBox.Cancel)	

        result = reply.exec_()	
        if reply.clickedButton() == commit_button:
            self.svn_tool.execute_cmd('add', file_path=save_full_path, close_on_end=0, logmsg='')
            self.svn_tool.execute_cmd('commit', file_path=save_full_path, close_on_end=0, logmsg='')
        elif reply.clickedButton() == save_button:
            pass

    def blender_save(self, save_path, save_name, mode):
        logmsg = ''
        
        # Look for logmsg in Blender text block or scene custom property
        if "logmsg" in bpy.context.scene:
            logmsg = bpy.context.scene["logmsg"]
            bpy.context.scene["logmsg"] = "" 
        elif "logmsg" in bpy.data.texts:
            logmsg = bpy.data.texts["logmsg"].as_string()
            bpy.data.texts.remove(bpy.data.texts["logmsg"])

        logger.debug('save_path: {}\nsave_name: {}'.format(save_path, save_name))
        save_full_path = os.path.join(save_path, save_name)
        bpy.ops.wm.save_as_mainfile(filepath=save_full_path)
        logger.debug('FILE SAVE AT: {0}'.format(save_full_path))
        return save_full_path, logmsg

    def blender_save_version(self, save_path, save_name):
        logger.debug('save_path: {}\nsave_name: {}'.format(save_path, save_name))
        save_full_path = os.path.join(save_path, save_name)
        bpy.ops.wm.save_as_mainfile(filepath=save_full_path)
        logger.debug('FILE SAVE AT: {0}'.format(save_full_path))
        return True

    def do_global_commit(self):
        logger.debug("do_global_commit START: Running Blender cleanups (if any)...")
        # Placeholder for Blender-specific scene prep (e.g. purging unused data blocks)
        pass

    def do_local_commit(self):
        logger.debug("do_local_commit START: Running Blender cleanups (if any)...")
        pass

    def push_btn_global_publish(self):
        try:
            original_scene_path = bpy.data.filepath
            asset_path = self._get_full_path()
            dept_item = self.asset_department_listWidget.currentItem()
            if not dept_item: return
            department_text = dept_item.text()

            global_path = os.path.normpath(os.path.join(asset_path, STATIC_FOLDER[2]))
            global_path_list = global_path.split(os.path.sep)
            selected_project = self.project_comboBox.currentText()

            if selected_project in USE_VARIATION:
                global_commit_name = f"{global_path_list[-3]}_{global_path_list[-2]}_{department_text}"
            else:
                global_commit_name = f"{global_path_list[-2]}_{department_text}"

            # Adjust casing to match any existing file in the target directory (case-insensitive match)
            if os.path.exists(global_path):
                existing_files = os.listdir(global_path)
                target_file_with_ext = f"{global_commit_name}.{BLENDER_EXT}"
                for f in existing_files:
                    if f.lower() == target_file_with_ext.lower():
                        global_commit_name = os.path.splitext(f)[0]
                        logger.warning(f"Casing mismatch detected! Adjusted casing to match existing global file: '{global_commit_name}'. Please rename your files to match this casing.")
                        break

            save_full_path = os.path.join(global_path, global_commit_name)

            reply = QMessageBox(self)
            reply.setWindowTitle('Commit Changes')
            reply.setText(f'Do you want to commit file to SVN ?\n\t{global_commit_name}')

            commit_button = reply.addButton('Commit', QMessageBox.AcceptRole)
            save_button = reply.addButton('Just Save', QMessageBox.AcceptRole)
            reply.addButton(QMessageBox.Cancel)

            result = reply.exec_()
            if reply.clickedButton() == commit_button:
                self.do_global_commit()
                save_file_path, logmsg = self.blender_save(global_path, f"{global_commit_name}.{BLENDER_EXT}", 'global')
                if original_scene_path:
                    bpy.ops.wm.open_mainfile(filepath=original_scene_path)
                self.svn_tool.execute_cmd('add', file_path=save_file_path, close_on_end=0, logmsg=logmsg)
                self.svn_tool.execute_cmd('commit', file_path=save_file_path, close_on_end=0, logmsg=logmsg)
                self.load_global_commit(global_path)
            elif reply.clickedButton() == save_button:
                self.do_global_commit()
                self.blender_save(global_path, f"{global_commit_name}.{BLENDER_EXT}", 'global')
                if original_scene_path:
                    bpy.ops.wm.open_mainfile(filepath=original_scene_path)
                self.load_global_commit(global_path)
        except Exception as e:
            logger.error(f"Error publishing global commit: {e}")

    def push_btn_local_publish(self):
        original_scene_path = bpy.data.filepath
        if not original_scene_path:
            logger.debug('The current file is not saved. Save it first.')
            return False

        asset_path = self._get_full_path()
        dept_item = self.asset_department_listWidget.currentItem()
        if not dept_item: return
        department_text = dept_item.text()
        full_path = os.path.normpath(os.path.join(asset_path, department_text, STATIC_FOLDER[2]))

        file_ext = os.path.basename(original_scene_path)
        file_name, ext = os.path.splitext(file_ext)
        check_digit = file_name.split('.')[-1]

        if check_digit.isdigit() and len(check_digit) == PADDING:
            local_commit_name = file_name.split('.')[0]
        else:
            logger.debug(f'This not valid name: using original ({file_name})')
            local_commit_name = file_name

        # Adjust casing to match any existing file in the target directory (case-insensitive match)
        if os.path.exists(full_path):
            existing_files = os.listdir(full_path)
            target_file_with_ext = f"{local_commit_name}.{BLENDER_EXT}"
            for f in existing_files:
                if f.lower() == target_file_with_ext.lower():
                    local_commit_name = os.path.splitext(f)[0]
                    logger.warning(f"Casing mismatch detected! Adjusted casing to match existing local file: '{local_commit_name}'. Please rename your files to match this casing.")
                    break

        save_full_path = os.path.join(full_path, local_commit_name)

        reply = QMessageBox(self)
        reply.setWindowTitle('Commit Changes')
        reply.setText(f'Do you want to commit file to SVN ?\n\t{local_commit_name}')

        commit_button = reply.addButton('Commit', QMessageBox.AcceptRole)
        save_button = reply.addButton('Just Save', QMessageBox.AcceptRole)
        reply.addButton(QMessageBox.Cancel)

        result = reply.exec_()
        if reply.clickedButton() == commit_button:
            self.do_local_commit()
            save_file_path, logmsg = self.blender_save(full_path, f"{local_commit_name}.{BLENDER_EXT}", 'local')
            if original_scene_path:
                bpy.ops.wm.open_mainfile(filepath=original_scene_path)
            self.svn_tool.execute_cmd('add', file_path=save_file_path, close_on_end=0, logmsg=logmsg)
            self.svn_tool.execute_cmd('commit', file_path=save_file_path, close_on_end=0, logmsg=logmsg)
            self.load_local_commit(full_path)
        elif reply.clickedButton() == save_button:
            self.do_local_commit()
            self.blender_save(full_path, f"{local_commit_name}.{BLENDER_EXT}", 'local')
            if original_scene_path:
                bpy.ops.wm.open_mainfile(filepath=original_scene_path)
            self.load_local_commit(full_path)

    def update_project_name(self):
        logger.debug(f'\tUI has change project name to >>> {self.project_comboBox.currentText()}')
        current_scene_path = bpy.data.filepath
        if current_scene_path:
            current_scene_path = os.path.normpath(current_scene_path)
            path_elements = current_scene_path.split(os.path.sep)
            project_name = path_elements[2]
            if project_name != self.project_comboBox.currentText():
                pass
            logger.debug('# # # update_project_name # # #')		

    def check_exists_blender(self):
        blender_file_path = bpy.data.filepath
        if not blender_file_path:
            logger.debug("No scene loaded (or never saved).")
            return False

        blender_file_path = os.path.normpath(blender_file_path)
        folder_path = os.path.dirname(blender_file_path)
        parent_folder = os.path.basename(folder_path)

        if parent_folder == STATIC_FOLDER[1]: # 'Version'
            logger.debug("The folder containing named 'Version'.")
            version_parent = os.path.dirname(folder_path)
            asset_path = os.path.dirname(version_parent)

            if os.path.exists(os.path.join(asset_path, 'data.json')):
                logger.debug('This file is valid. Go on.')
                self.update_to_browser(asset_path)
                self.populate_version_from_open_scene(asset_path)
                return True
            else:
                logger.warning(f"Invalid asset structure (missing data.json): {asset_path}")
                return False

        elif parent_folder == STATIC_FOLDER[2]: # 'Commit'
            logger.debug("There is a Commit file.")
            back_folder_path = os.path.normpath(os.path.dirname(folder_path))

            if os.path.exists(os.path.join(back_folder_path, 'data.json')):
                logger.debug(f"This file is Global Commit >>> {back_folder_path}")
                src_index = self.asset_fs_model.index(back_folder_path)
                if src_index.isValid():
                    proxy_index = self.asset_proxy.mapFromSource(src_index)
                    sel = self.asset_dir_TREEVIEW.selectionModel()
                    sel.setCurrentIndex(
                        proxy_index,
                        QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Current
                    )
                    self.asset_dir_TREEVIEW.scrollTo(proxy_index, QtWidgets.QAbstractItemView.PositionAtTop)
                    self.asset_dir_TREEVIEW.clicked.emit(proxy_index)
                else:
                    logger.warning(f"Invalid index for back_folder_path: {back_folder_path}")
                self.load_global_commit(folder_path)
                return True
            else:
                logger.debug("This file is Local Commit.")
                assetName_path = os.path.normpath(os.path.dirname(back_folder_path))

                if os.path.exists(os.path.join(assetName_path, 'data.json')):
                    src_index = self.asset_fs_model.index(assetName_path)
                    if src_index.isValid():
                        proxy_index = self.asset_proxy.mapFromSource(src_index)
                        sel = self.asset_dir_TREEVIEW.selectionModel()
                        sel.setCurrentIndex(
                            proxy_index,
                            QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Current
                        )
                        self.asset_dir_TREEVIEW.scrollTo(proxy_index, QtWidgets.QAbstractItemView.PositionAtTop)
                        self.asset_dir_TREEVIEW.clicked.emit(proxy_index)
                    else:
                        logger.warning(f"Invalid index for assetName_path: {assetName_path}")

                    department_name = os.path.basename(back_folder_path)
                    department_item = self.asset_department_listWidget.findItems(department_name, QtCore.Qt.MatchExactly)
                    if department_item:
                        self.asset_department_listWidget.setCurrentItem(department_item[0])

                    self.load_local_commit(folder_path)
                    return True
                else:
                    logger.warning(f"Invalid local commit structure (missing data.json): {assetName_path}")
                    return False
        else:
            logger.debug("The current file is not under managed Version/Commit paths.")
            return False

    def update_to_browser(self, file_path):
        logger.debug(f"The Scene is already open: {file_path}")
        src_index = self.asset_fs_model.index(file_path)
        if src_index.isValid():
            proxy_index = self.asset_proxy.mapFromSource(src_index)
            self.asset_dir_TREEVIEW.setCurrentIndex(proxy_index)
            self.asset_dir_TREEVIEW.selectionModel().setCurrentIndex(
                proxy_index, QtCore.QItemSelectionModel.ClearAndSelect
            )
            self.asset_dir_TREEVIEW.scrollTo(proxy_index, QtWidgets.QAbstractItemView.PositionAtTop)
        else:
            logger.warning(f"update_to_browser: invalid index for {file_path}")

    def populate_version_from_open_scene(self, file_path):
        logger.debug('Populate version from open scene...')
        current_scene_path = bpy.data.filepath
        if current_scene_path:
            current_scene_path = os.path.normpath(current_scene_path)
            path_elements = current_scene_path.split(os.path.sep)
            
            asset_name = path_elements[-4]
            department_name = path_elements[-3]

            asset_index = self.asset_fs_model.index(file_path)
            if asset_index.isValid():
                proxy_index = self.asset_proxy.mapFromSource(asset_index)
                self.asset_dir_TREEVIEW.setCurrentIndex(proxy_index)
                self.asset_dir_TREEVIEW.selectionModel().setCurrentIndex(
                    proxy_index, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Current
                )
                self.asset_dir_TREEVIEW.selectionModel().select(
                    proxy_index, QtCore.QItemSelectionModel.ClearAndSelect
                )
                self.asset_dir_TREEVIEW.scrollTo(proxy_index, QtWidgets.QAbstractItemView.PositionAtTop)

            # Load all departments for this asset
            self.load_asset_departments(file_path)

            department_item = self.asset_department_listWidget.findItems(department_name, QtCore.Qt.MatchExactly)
            if department_item:
                self.asset_department_listWidget.setCurrentItem(department_item[0])
            else:
                self.asset_department_listWidget.addItem(department_name)
                department_item = self.asset_department_listWidget.findItems(department_name, QtCore.Qt.MatchExactly)
                if department_item:
                    self.asset_department_listWidget.setCurrentItem(department_item[0])

            version_folder = os.path.normpath(os.path.join(file_path, department_name, STATIC_FOLDER[1]))
            self.show_version_entite(version_folder)

            asset_name_file = path_elements[-1]
            version_item = self.asset_version_view_listWidget.findItems(asset_name_file, QtCore.Qt.MatchExactly)
            if version_item:
                self.asset_version_view_listWidget.setCurrentItem(version_item[0])

            data_file = os.path.join(file_path, 'data.json')
            if os.path.exists(data_file):
                with open(data_file, "r") as file:
                    json_data = json.load(file)
                self.assetInfo_list_listWidget.addItem(json_data.get('comment', ''))

            thumbnail_path = os.path.join(file_path, THUMBNAIL_NAME)
            self.display_images(thumbnail_path)

            global_commit_folder = os.path.join(file_path, STATIC_FOLDER[2])
            if os.path.exists(global_commit_folder):
                self.load_global_commit(global_commit_folder)

            local_commit_folder = os.path.join(file_path, department_name, STATIC_FOLDER[2])
            if os.path.exists(local_commit_folder):
                self.load_local_commit(local_commit_folder)

    def find_step_and_version(self, my_list):
        logger.debug('my_list >>> : {0}'.format(my_list))
        if my_list is not None:
            result_job_element = {
                "step": [],
                "max_version": []
            }
            result = {}

            current_index = self.asset_dir_TREEVIEW.currentIndex()
            src_index = self._asset_proxy_to_source(current_index)
            full_path = self.asset_fs_model.filePath(src_index)
            full_path = os.path.normpath(full_path)
            full_path = full_path.split(os.path.sep)
            department_text = self.asset_department_listWidget.currentItem().text()

            if self.project_comboBox.currentText() in USE_VARIATION:
                use_name = full_path[-2] + '_' + full_path[-1] + '_' + department_text + '_'	
            else:
                use_name = full_path[-1] + '_' + department_text + '_'

            logger.debug('Got use_name: {0}'.format(use_name))
            filtered_list = [name for name in my_list if name.startswith(use_name)]

            for element in filtered_list:
                replace_name = element.replace(use_name, '')
                replace_name = replace_name.split('.')

                if len(replace_name) == 3:
                    name = replace_name[0]	
                    match = re.search(r'\.(\d+)\.blend$', element)
                    if match:
                        version = int(match.group(1))
                        if name not in result or version > int(result[name][1]):
                            result[name] = [element, version]
                else:
                    logger.error('{0} is wrong here.'.format(use_name))
                    continue

            if not result:
                logger.debug('result_job_element: There are no right naming to Query')
                return False

            for name in result:
                result_job_element["step"].append(name)
                result_job_element["max_version"].append(result[name][1])
            logger.debug('result_job_element: {0}'.format(result_job_element))
            return result_job_element
        else:
            return False

    def filter_proper_version_list(self):
        try:
            asset_path = self._get_full_path()
            if not asset_path or not os.path.exists(asset_path):
                return None
            
            current_dept = self.asset_department_listWidget.currentItem()
            if not current_dept:
                return None
            department_text = current_dept.text()
            
            department_path = os.path.normpath(os.path.join(asset_path, department_text))
            job_step_list = os.path.join(department_path, STATIC_FOLDER[1])
            if not os.path.exists(job_step_list):
                return None
            job_step_list = os.listdir(job_step_list)
            logger.debug('This job_step_list: {0}'.format(job_step_list))

            path_list = asset_path.split(os.path.sep)
            selected_project = self.project_comboBox.currentText()

            if selected_project in USE_VARIATION:
                path_check = path_list[-2] + '_' + path_list[-1]
                pattern_esc = r'{0}.*\.blend'.format(re.escape(path_check))
            else:
                path_check = path_list[-1]
                pattern_esc = r'{0}.*\.blend'.format(re.escape(path_check))

            step_filter_list = []
            for each in job_step_list:
                if re.match(pattern_esc, each):
                    step_filter_list.append(each)

            if step_filter_list:
                return step_filter_list
            else:
                logger.debug('There are no proper naming to return')
                return None
        except Exception as e:
            logger.error(f"Error in filter_proper_version_list: {e}")
            return None

    def query_step_list(self):
        step_filter_list = self.filter_proper_version_list()
        result_job_element = self.find_step_and_version(step_filter_list)
        if step_filter_list == None:		
            return False
        else:
            return result_job_element

    def create_job_step(self):
        step_name, okPressed = QInputDialog.getText(self, "Create Step", "Enter Step name:")
        if okPressed and step_name:
            self.create_name_saving(step_name)

    def create_name_saving(self, step_name):
        try:
            asset_path_text = self._get_full_path()
            current_dept = self.asset_department_listWidget.currentItem()
            if not current_dept:
                logger.warning("Cannot save: no department selected.")
                return False
            department_text = current_dept.text()
            new_folder_path = os.path.normpath(os.path.join(asset_path_text, department_text))

            step_filter_list = self.filter_proper_version_list()
            result_job_element = self.find_step_and_version(step_filter_list)

            selected_project = self.project_comboBox.currentText()
            split_path_list = new_folder_path.split(os.path.sep)

            if selected_project in USE_VARIATION:
                asset_name = split_path_list[-3]
                variation_name = split_path_list[-2]
                job_name = split_path_list[-1]
                final_file_name = f"{asset_name}_{variation_name}_{job_name}"
            else:
                asset_name = split_path_list[-2]
                job_name = split_path_list[-1]
                final_file_name = f"{asset_name}_{job_name}"

            if result_job_element != False and result_job_element is not None:
                step_list = result_job_element.get('step', [])
                if step_name in step_list:
                    index = step_list.index(step_name)
                    max_version = result_job_element['max_version'][index]
                    max_version += 1
                    max_version = str(max_version).zfill(PADDING)
                else:
                    max_version = str(1).zfill(PADDING)
            else:
                max_version = str(1).zfill(PADDING)

            new_file_name = f"{final_file_name}_{step_name}.{max_version}.{BLENDER_EXT}"
            save_full_path = os.path.normpath(os.path.join(asset_path_text, department_text, STATIC_FOLDER[1], new_file_name))
            save_path = os.path.normpath(os.path.join(asset_path_text, department_text, STATIC_FOLDER[1]))

            os.makedirs(save_path, exist_ok=True)
            self.blender_save_version(save_path, new_file_name)
            self.asset_version_view_listWidget.clear()
            self.show_version_entite(save_path)
            return True
        except Exception as e:
            logger.error(f"Error in create_name_saving: {e}")
            import traceback
            traceback.print_exc()
            return False

    def show_step_context(self, position):
        try:
            current_dept = self.asset_department_listWidget.currentItem()
            if not current_dept:
                logger.debug("Cannot show step context: no department selected.")
                return

            contextMenu = QtWidgets.QMenu(self)

            setp_showInExplorer_action = QAction("Show in Explorer", self)
            setp_showInExplorer_action.triggered.connect(self.show_local_version_explorer)
            contextMenu.addAction(setp_showInExplorer_action)

            current_version = self.asset_version_view_listWidget.currentItem()
            if current_version:
                link_action = QAction("Link selected this file...", self)
                link_action.triggered.connect(self.handle_link_version_widget)
                contextMenu.addAction(link_action)

            createStep_action = QAction("Create New Step...", self)
            createStep_action.triggered.connect(self.create_job_step)
            contextMenu.addAction(createStep_action)

            result_job_element = self.query_step_list()
            if result_job_element:
                step_list = result_job_element.get('step', [])
                for option in step_list:
                    action = QAction(option, self)
                    action.setData(option)
                    action.triggered.connect(self.handle_dynamic_context)
                    contextMenu.addAction(action)

            contextMenu.exec_(self.asset_version_view_listWidget.mapToGlobal(position))
        except Exception as e:
            logger.error(f"Error in show_step_context: {e}")
            import traceback
            traceback.print_exc()

    def handle_dynamic_context(self):
        try:
            action = self.sender()
            selected_context = action.data()

            confirmation_dialog = QMessageBox(self)
            confirmation_dialog.setIcon(QMessageBox.Question)
            confirmation_dialog.setText(f"Are you sure you want to save this step job\n\t{selected_context} ?")
            confirmation_dialog.setWindowTitle("Confirmation")
            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirmation_dialog.setDefaultButton(QMessageBox.No)

            choice = confirmation_dialog.exec_()
            if choice == QMessageBox.Yes:
                self.create_name_saving(selected_context)
        except Exception as e:
            logger.error(f"Error in handle_dynamic_context: {e}")
            import traceback
            traceback.print_exc()

    def show_job_context_menu(self, position):
        contextMenu = QtWidgets.QMenu(self)
        createJobs_action = QAction("Create Jobs", self)
        createJobs_action.triggered.connect(self.create_jobs)
        contextMenu.addAction(createJobs_action)

        showInExplorer_action = QAction("Show in Explorer", self)
        showInExplorer_action.triggered.connect(self.show_job_explorer)
        contextMenu.addAction(showInExplorer_action)

        contextMenu.exec_(self.asset_department_listWidget.mapToGlobal(position))

    def show_job_explorer(self):
        asset_path_text = self._get_full_path()
        new_department_text = self.asset_department_listWidget.currentItem().text()
        new_folder_path = os.path.join(asset_path_text, new_department_text)
        self._open_folder_path(new_folder_path)

    def _open_folder_path(self, input_path):
        if not os.path.exists(input_path):
            logger.debug('{0} is not exists'.format(input_path))
            return
        if sys.platform == "win32":
            os.startfile(input_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", input_path])
        else:
            subprocess.Popen(["xdg-open", input_path])	

    def create_jobs(self):
        jobs_name, okPressed = QInputDialog.getText(self, "Create Jobs", "Enter folder name:")
        if okPressed and jobs_name:
            asset_path = self._get_full_path()
            new_folder_path = os.path.normpath(os.path.join(asset_path, jobs_name))

            if not os.path.exists(new_folder_path):
                self.asset_department_listWidget.clear()

                for job_type in JOB_TEMPLATE:
                    job_each_path = os.path.join(new_folder_path, job_type)
                    os.makedirs(job_each_path, exist_ok=True)

                logger.debug('This is department_name {0}'.format(new_folder_path))
                items = os.listdir(asset_path)
                items_excluded = [dept for dept in items if dept not in EXCLUDE_VIEW_ITEM and os.path.isdir(os.path.join(asset_path, dept))]
                self.asset_department_listWidget.addItems(sorted(items_excluded))
            else:
                logger.warning('Cannot create a folder when that folder already exists.')

    def display_images(self, image_paths):
        if image_paths is not None:
            logger.debug(image_paths)
            self.asset_thumbnail_IMAGE_LABEL.setScaledContents(True)
            pixmap = QPixmap(image_paths)
            self.asset_thumbnail_IMAGE_LABEL.setPixmap(pixmap.scaled(self.asset_thumbnail_IMAGE_LABEL.size(), Qt.KeepAspectRatio))
            self.asset_thumbnail_IMAGE_LABEL.repaint()
            QApplication.processEvents()
        else:
            logger.debug('There are nothing to show.')
            self.asset_thumbnail_IMAGE_LABEL.clear()

    def populate_drives(self):
        self.drive_comboBox.clear()
        self.drive_comboBox.addItems(DRIVES)

    def populate_project(self):
        self.project_comboBox.clear()
        self.project_comboBox.addItems(PROJECT_NAME)

    def update_project_comboBox(self):
        selected_drive = self.drive_comboBox.currentText()
        selected_project = self.project_comboBox.currentText()
        try:
            if DEFAULT_PROJECT in ['NangRam', 'True']:
                self.path = os.path.join(selected_drive, BASE_FOLDER, DEFAULT_PROJECT)
            else:
                self.path = os.path.join(selected_drive, BASE_FOLDER, DEFAULT_PROJECT, ASSET_TOP_FOLDER)
        except Exception:
            if PROJECT_NAME[0] in ['NangRam', 'True']:
                self.path = os.path.join(selected_drive, BASE_FOLDER, PROJECT_NAME[0])
            else:
                self.path = os.path.join(selected_drive, BASE_FOLDER, PROJECT_NAME[0], ASSET_TOP_FOLDER)

    def populate_ASSET_treeView(self):
        current_project = self.project_comboBox.currentText()
        if current_project in FIXED_PROJECT_PATHS:
            self.path = FIXED_PROJECT_PATHS[current_project]
        else:
            if current_project in ['NangRam', 'True']:
                self.path = os.path.join(self.drive_comboBox.currentText(), BASE_FOLDER, current_project)
            else:
                self.path = os.path.join(self.drive_comboBox.currentText(), BASE_FOLDER, current_project, ASSET_TOP_FOLDER)

        if not os.path.exists(self.path): return
        self.asset_fs_model.setRootPath(self.path)
        self.asset_proxy.setSourceModel(self.asset_fs_model)
        self.asset_dir_TREEVIEW.setModel(self.asset_proxy)
        src_root = self.asset_fs_model.index(self.path)
        proxy_root = self.asset_proxy.mapFromSource(src_root)
        self.asset_dir_TREEVIEW.setRootIndex(proxy_root)

        self.asset_filter_lineEdit.setPlaceholderText('Search.')
        
        self.asset_fs_model.setNameFilters(HIDE_FORMAT)
        self.asset_fs_model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)

        header = self.asset_dir_TREEVIEW.header()
        self.asset_dir_TREEVIEW.setColumnHidden(1, True)
        self.asset_dir_TREEVIEW.setColumnHidden(2, True)
        self.asset_dir_TREEVIEW.setColumnHidden(3, True)
        if hasattr(header, "setSectionResizeMode"):
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

    def populate_SCENE_treeView(self):
        current_project = self.project_comboBox.currentText()
        if current_project in FIXED_PROJECT_PATHS:
            path = FIXED_PROJECT_PATHS[current_project]
        else:
            if current_project in ['NangRam', 'True']:
                path = os.path.join(self.drive_comboBox.currentText(), BASE_FOLDER, current_project)
            else:
                path = os.path.join(self.drive_comboBox.currentText(), BASE_FOLDER, current_project, SCENE_TOP_FOLDER)

        if not os.path.exists(path): return
        self.scene_fs_model = QtWidgets.QFileSystemModel(self)
        self.scene_fs_model.setRootPath(path)
        self.scene_fs_model.setNameFilters(HIDE_FORMAT)
        self.scene_fs_model.setNameFilterDisables(False)

        self.dir_scene_TREEVIEW.setModel(self.scene_fs_model)
        self.dir_scene_TREEVIEW.setRootIndex(self.scene_fs_model.index(path))

        self.dir_scene_TREEVIEW.setSortingEnabled(True)
        self.dir_scene_TREEVIEW.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.dir_scene_TREEVIEW.setColumnHidden(1, True)
        self.dir_scene_TREEVIEW.setColumnHidden(2, True)

    def on_treeview_clicked(self, index):
        self.asset_local_view_listWidget.clear()
        self.asset_global_listWidget.clear()
        self.asset_department_listWidget.clear()
        self.asset_version_view_listWidget.clear()
        self.assetInfo_list_listWidget.clear()

        src_index = self._asset_proxy_to_source(index)
        file_path = self.asset_fs_model.filePath(src_index)

        if os.path.isfile(file_path):
            return
        
        data_file = os.path.join(file_path, 'data.json')
        self.display_images(None)

        is_asset_by_meta = os.path.exists(data_file)
        
        is_asset_by_structure = False
        if not is_asset_by_meta:
            is_asset_by_structure = any(
                os.path.isdir(os.path.join(file_path, dept)) for dept in (JOB_TEMPLATE + DEPT_NAME)
            )

        if is_asset_by_meta or is_asset_by_structure:
            self.load_asset_departments(file_path)
            global_commit_folder = os.path.join(file_path, STATIC_FOLDER[2])
            if os.path.exists(global_commit_folder):
                self.load_global_commit(global_commit_folder)

            thumbnail_path = os.path.join(file_path, THUMBNAIL_NAME)
            if os.path.exists(thumbnail_path):
                self.display_images(thumbnail_path)
            else:
                self.display_images(None)


            if is_asset_by_meta:
                try:
                    with open(data_file, "r") as file:
                        json_data = json.load(file)
                    self.assetInfo_list_listWidget.addItem(json_data.get('comment', 'No Comment'))
                except Exception as e:
                    logger.error(f"Error reading {data_file}: {e}")
            else:
                self.assetInfo_list_listWidget.addItem("⚠️ Missing 'data.json'")

    def on_treeview_SCENE_clicked(self, index):
        file_path = self.scene_fs_model.filePath(index)
        logger.debug(f"This is scene file path: {file_path}")

    def on_department_clicked(self, item):
        self.asset_local_view_listWidget.clear()
        self.asset_global_listWidget.clear()

        selected_item = self.asset_department_listWidget.currentItem()
        department_text = selected_item.text()
        asset_path = self._get_full_path()

        version_folder = os.path.join(asset_path, department_text, 'Version')
        self.show_version_entite(version_folder)

        global_commit_folder = os.path.join(asset_path, STATIC_FOLDER[2])
        if os.path.exists(global_commit_folder):
            self.load_global_commit(global_commit_folder)

        local_commit_folder = os.path.join(asset_path, department_text, STATIC_FOLDER[2])
        if os.path.exists(local_commit_folder):
            self.load_local_commit(local_commit_folder)

    def show_version_entite(self, version_folder, department_text=None):
        self.asset_version_view_listWidget.clear()

        if department_text is None and hasattr(self, 'asset_department_listWidget'):
            curr = self.asset_department_listWidget.currentItem()
            if curr:
                department_text = curr.text()

        is_image_dept = department_text and department_text.lower() in ('texture', 'conceptart')

        if is_image_dept:
            if os.path.basename(version_folder).lower() == 'version':
                dept_folder = os.path.dirname(version_folder)
            else:
                dept_folder = version_folder

            dept_folder = os.path.normpath(dept_folder)
            files_to_show = []

            # 1. Scan direct department folder
            if os.path.exists(dept_folder) and not os.path.isfile(dept_folder):
                for f in os.listdir(dept_folder):
                    full_f = os.path.join(dept_folder, f)
                    if os.path.isfile(full_f):
                        if (f not in EXCLUDE_VIEW_ITEM 
                            and f.lower() not in ('_backup', '_bakup')
                            and not f.lower().startswith(('_backup', '_bakup'))
                            and not any(fnmatch.fnmatch(f, p) for p in ['*.pyc', '*.o', '.mayaSwatches'])):
                            files_to_show.append(f)

            # 2. Also check Version subfolder if it exists
            sub_version = os.path.join(dept_folder, 'Version')
            if os.path.exists(sub_version) and not os.path.isfile(sub_version):
                for f in os.listdir(sub_version):
                    full_f = os.path.join(sub_version, f)
                    if os.path.isfile(full_f):
                        if (f not in EXCLUDE_VIEW_ITEM 
                            and f.lower() not in ('_backup', '_bakup')
                            and not f.lower().startswith(('_backup', '_bakup'))
                            and not any(fnmatch.fnmatch(f, p) for p in ['*.pyc', '*.o', '.mayaSwatches'])):
                            if f not in files_to_show:
                                files_to_show.append(f)

            if files_to_show:
                self.asset_version_view_listWidget.addItems(sorted(files_to_show))
                logger.debug(f"Found image files in {department_text}: {files_to_show}")
            else:
                logger.info(f"No files found in {department_text} folder.")
            return

        if os.path.exists(version_folder):
            version_folder = os.path.normpath(version_folder)
            if not os.path.isfile(version_folder):
                version_file_list = os.listdir(version_folder)			
                filtered_file_list = [
                    f for f in version_file_list
                    if f not in EXCLUDE_VIEW_ITEM
                    and f.lower() not in ('_backup', '_bakup')
                    and not f.lower().startswith(('_backup', '_bakup'))
                    and os.path.isfile(os.path.join(version_folder, f))
                    and not any(fnmatch.fnmatch(f, pattern) for pattern in HIDE_FORMAT)
                ]
                self.asset_version_view_listWidget.addItems(filtered_file_list)

    def on_version_clicked(self):
        asset_path = self._get_full_path()
        selected_item = self.asset_department_listWidget.currentItem()

        if selected_item:
            department_text = selected_item.text()
            selected_task = self.asset_version_view_listWidget.currentItem()
            if not selected_task:
                return
            selected_task_text = selected_task.text()

            direct_path = os.path.normpath(os.path.join(asset_path, department_text, selected_task_text))
            version_path = os.path.normpath(os.path.join(asset_path, department_text, STATIC_FOLDER[1], selected_task_text))

            if os.path.exists(direct_path):
                current_version_clicked = direct_path
            else:
                current_version_clicked = version_path

            current_version_clicked = self.handle_selected_path(current_version_clicked)
            _, ext = os.path.splitext(current_version_clicked)
            if ext.lower() in ('.png', '.jpg', '.jpeg', '.tga', '.tif', '.tiff', '.bmp'):
                self.display_images(current_version_clicked)
        else:
            selected_task = self.asset_version_view_listWidget.currentItem()
            if not selected_task:
                return
            selected_task_text = selected_task.text()
            current_version_clicked = os.path.join(asset_path, 'Version', selected_task_text)
            current_version_clicked = self.handle_selected_path(current_version_clicked)
            _, ext = os.path.splitext(current_version_clicked)
            if ext.lower() in ('.png', '.jpg', '.jpeg', '.tga', '.tif', '.tiff', '.bmp'):
                self.display_images(current_version_clicked)

    def load_global_commit(self, folder):
        self.asset_global_listWidget.clear()
        if os.path.exists(folder):
            items = [
                f for f in os.listdir(folder)
                if f not in EXCLUDE_VIEW_ITEM
                and f.lower() not in ('_backup', '_bakup')
                and not f.lower().startswith(('_backup', '_bakup'))
                and os.path.isfile(os.path.join(folder, f))
            ]
            self.asset_global_listWidget.addItems(items)

    def load_local_commit(self, folder):
        self.asset_local_view_listWidget.clear()
        if os.path.exists(folder):
            items = [
                f for f in os.listdir(folder)
                if f not in EXCLUDE_VIEW_ITEM
                and f.lower() not in ('_backup', '_bakup')
                and not f.lower().startswith(('_backup', '_bakup'))
                and os.path.isfile(os.path.join(folder, f))
            ]
            self.asset_local_view_listWidget.addItems(items)

    def _get_full_path(self):
        current_index = self.asset_dir_TREEVIEW.currentIndex()
        src_index = self._asset_proxy_to_source(current_index)
        return os.path.normpath(self.asset_fs_model.filePath(src_index))

    def _asset_proxy_to_source(self, index):
        model = self.asset_dir_TREEVIEW.model()
        return model.mapToSource(index) if isinstance(model, QSortFilterProxyModel) else index

    def get_deep_path(self):
        asset_path = self._get_full_path()
        dept = self.asset_department_listWidget.currentItem().text()
        item = self.asset_version_view_listWidget.currentItem()
        if not item:
            return ""
        file_name = item.text()

        direct_path = os.path.normpath(os.path.join(asset_path, dept, file_name))
        version_path = os.path.normpath(os.path.join(asset_path, dept, STATIC_FOLDER[1], file_name))

        if os.path.exists(direct_path):
            return direct_path
        return version_path

    def get_deep_path_global_commit(self):
        asset_path = self._get_full_path()
        item = self.asset_global_listWidget.currentItem()
        if not item: return ""
        return os.path.normpath(os.path.join(asset_path, STATIC_FOLDER[2], item.text()))

    def get_deep_path_local_commit(self):
        full_department_path = self._get_department_path()
        local_commit = self.asset_local_view_listWidget.currentItem()
        if not local_commit: return ""
        return os.path.normpath(os.path.join(full_department_path, STATIC_FOLDER[2], local_commit.text()))

    def _get_department_path(self):
        full_path = self._get_full_path()
        department_text = self.asset_department_listWidget.currentItem().text()
        return os.path.join(full_path, department_text)

    def handle_selected_path(self, path):
        return os.path.normpath(path)

    def load_asset_departments(self, folder_path):
        self.asset_department_listWidget.clear()
        items = []
        for name in os.listdir(folder_path):
            if name in EXCLUDE_VIEW_ITEM: continue
            full = os.path.join(folder_path, name)
            if os.path.isdir(full):
                items.append(name)
        if items:
            self.asset_department_listWidget.addItems(sorted(items))

    def on_glogal_commit_clicked(self):
        pass

    def show_local_version_explorer(self):
        asset_path_text = self._get_full_path()
        new_department_text = self.asset_department_listWidget.currentItem().text()
        new_folder_path = os.path.join(asset_path_text, new_department_text, STATIC_FOLDER[1])
        self._open_folder_path(new_folder_path)

    def show_local_widget_explorer(self):
        asset_path_text = self._get_full_path()
        new_department_text = self.asset_department_listWidget.currentItem().text()
        new_folder_path = os.path.join(asset_path_text, new_department_text, STATIC_FOLDER[2])
        self._open_folder_path(new_folder_path)

    def show_global_widget_explorer(self):
        asset_path_text = self._get_full_path()		
        full_path = os.path.join(asset_path_text, STATIC_FOLDER[2])
        self._open_folder_path(full_path)

    def handle_right_click_global_widget(self, position):
        contextMenu = QtWidgets.QMenu(self)
        showInExplorer_action = QAction("Show in Explorer", self)
        showInExplorer_action.triggered.connect(self.show_global_widget_explorer)
        contextMenu.addAction(showInExplorer_action)

        link_action = QAction("Link selected this file...", self)
        link_action.triggered.connect(self.handle_link_global_widget)
        contextMenu.addAction(link_action)

        contextMenu.exec_(self.asset_global_listWidget.mapToGlobal(position))

    def handle_right_click_local_widget(self, position):
        contextMenu = QtWidgets.QMenu(self)
        local_commit_showInExplorer_action = QAction("Show in Explorer", self)
        local_commit_showInExplorer_action.triggered.connect(self.show_local_widget_explorer)
        contextMenu.addAction(local_commit_showInExplorer_action)

        link_action = QAction("Link selected this file...", self)
        link_action.triggered.connect(self.handle_link_local_widget)
        contextMenu.addAction(link_action)

        contextMenu.exec_(self.asset_local_view_listWidget.mapToGlobal(position))

    def show_context_menu(self, point):
        proxy_index = self.asset_dir_TREEVIEW.indexAt(point)
        menu = QtWidgets.QMenu(self)
        new_entitie_action = menu.addAction("Create Entite...")
        new_asset_action = menu.addAction("Create Asset...")
        show_in_explorer_action = menu.addAction("Show in Explorer")

        chosen_action = menu.exec_(self.asset_dir_TREEVIEW.mapToGlobal(point)) 

        if chosen_action == new_entitie_action:
            self.create_entite(proxy_index)
        elif chosen_action == new_asset_action:
            self.create_asset(proxy_index)
        elif chosen_action == show_in_explorer_action:
            # Use the proxy_index at right-click point directly instead of current selection
            filepath = self._path_from_treeview_index(proxy_index)
            if filepath and os.path.isdir(filepath):
                self._open_folder_path(filepath)

    def _path_from_treeview_index(self, proxy_index):
        if not proxy_index.isValid(): return None
        src_index = self._asset_proxy_to_source(proxy_index)
        return self.asset_fs_model.filePath(src_index)

    def create_entite(self, index):
        model = self.asset_dir_TREEVIEW.model()
        if not index or not index.isValid():
            root_proxy = self.asset_dir_TREEVIEW.rootIndex()
            if isinstance(model, QtCore.QSortFilterProxyModel):
                parent_dir = self.asset_fs_model.filePath(model.mapToSource(root_proxy))
            else:
                parent_dir = model.filePath(root_proxy)
        else:
            if isinstance(model, QtCore.QSortFilterProxyModel):
                src_index = model.mapToSource(index)
                parent_src = src_index.parent()
                parent_dir = self.asset_fs_model.filePath(parent_src) if parent_src.isValid() else self.asset_fs_model.rootPath()
            else:
                parent_dir = model.filePath(index.parent())

        parent_dir = parent_dir or self.asset_fs_model.rootPath() or self.path
        if not parent_dir:
            QMessageBox.warning(self, "No Root", "Please select a project/drive first.")
            return

        name, ok = QtWidgets.QInputDialog.getText(self, "New Entite", "Enter folder name:")
        if not (ok and name): return
        new_folder_path = os.path.normpath(os.path.join(parent_dir, name))
        os.makedirs(new_folder_path, exist_ok=True)

        src_new = self.asset_fs_model.index(new_folder_path)
        proxy_new = self.asset_proxy.mapFromSource(src_new)
        self.asset_dir_TREEVIEW.selectionModel().setCurrentIndex(
            proxy_new, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Current
        )
        self.asset_dir_TREEVIEW.scrollTo(proxy_new)

    def get_full_entity_name(self, base_path):
        base_path = os.path.normpath(base_path).replace('\\', '/')
        directories = base_path.split("/")
        if ASSET_TOP_FOLDER in directories: 
            content_index = directories.index(ASSET_TOP_FOLDER)
            directories = directories[content_index+1:]
        else:
            current_project = self.project_comboBox.currentText()
            if current_project in directories:
                proj_index = directories.index(current_project)
                directories = directories[proj_index+1:]
            else:
                directories = directories[1:] if len(directories) > 1 else directories
        if directories:
            directories.pop()
        return "/" + "/".join(directories) if directories else "/"

    def get_department_name(self, new_asset_path):
        folders_list = os.listdir(new_asset_path)
        if 'data.json' in folders_list:
            folders_list.remove('data.json')
        return folders_list

    def create_data_JSON(self, base_path, entitie_type, entitie_name, full_entity_name, department_name, comment, add_path_SVN):
        entitie_dict = DICTIONARY_TEMPLATE.copy()
        entitie_dict["base_path"] = base_path
        entitie_dict["entitie_type"] = entitie_type
        entitie_dict["entitie_name"] = entitie_name
        entitie_dict["full_entity_name"] = full_entity_name
        entitie_dict["department_name"] = department_name
        entitie_dict["comment"] = comment
        entitie_dict["add_path_SVN"] = add_path_SVN
        return entitie_dict

    def write_entite_folder(self, dictionary):
        with open("{0}/data.json".format(dictionary["base_path"]), "w") as f:
            json.dump(dictionary, f, indent=2)
        return True

    def create_asset(self, index):
        if not index or not index.isValid():
            index = self.asset_dir_TREEVIEW.currentIndex()
        parent_dir = self._path_from_treeview_index(index)
        if parent_dir and os.path.isfile(parent_dir):
            parent_dir = os.path.dirname(parent_dir)

        asset_name, ok = QtWidgets.QInputDialog.getText(self, "Create Asset", "Enter asset name:")
        if ok and asset_name:
            new_asset_path = os.path.join(parent_dir, asset_name)
            if not os.path.exists(new_asset_path):
                logger.debug("\tNo existing folder here. Continue.")
                new_asset_path = os.path.normpath(new_asset_path).replace('\\', '/')
                
                # Create department/job structure
                for job in DEPT_NAME:
                    job_path = os.path.join(new_asset_path, job)
                    os.makedirs(job_path, exist_ok=True)
                    for job_type in JOB_TEMPLATE:
                        os.makedirs(os.path.join(job_path, job_type), exist_ok=True)

                if DEPT_EMPTY:
                    for job in DEPT_EMPTY:
                        os.makedirs(os.path.join(new_asset_path, job), exist_ok=True)
                
                logger.debug("\tThis is asset path:\t{0}".format(new_asset_path))
                fullEntityName = self.get_full_entity_name(new_asset_path)
                department_name = self.get_department_name(new_asset_path)
                
                add_path_for_SVN = []
                add_path_for_SVN.append(os.path.normpath(new_asset_path))
                folder_global_path = os.path.normpath(os.path.join(new_asset_path, STATIC_FOLDER[2]))
                add_path_for_SVN.append(folder_global_path)

                for each in department_name:
                    if each in DEPT_EMPTY:
                        continue
                    else:
                        folder_version_path = os.path.normpath(os.path.join(new_asset_path, each, STATIC_FOLDER[1]))
                        folder_commit_path = os.path.normpath(os.path.join(new_asset_path, each, STATIC_FOLDER[2]))
                        add_path_for_SVN.append(folder_version_path)
                        add_path_for_SVN.append(folder_commit_path)

                entite_dict = self.create_data_JSON(new_asset_path, 'Asset', asset_name, fullEntityName, department_name, "", add_path_for_SVN)
                logger.debug(entite_dict)
                self.write_entite_folder(entite_dict)

                reply = QMessageBox(self)
                reply.setWindowTitle('Commit Changes')
                reply.setText('Do you want to commit thumbnail to SVN ?\n\t')
                commit_button = reply.addButton('Add', QMessageBox.AcceptRole)
                save_button = reply.addButton('Just Create', QMessageBox.AcceptRole)
                reply.addButton(QMessageBox.Cancel)

                result = reply.exec_()
                if reply.clickedButton() == commit_button:
                    logger.debug("\tThis is File path:\t{0}".format(add_path_for_SVN[0]))
                    self.svn_tool.execute_cmd('add', file_path=add_path_for_SVN[0], close_on_end=0, add_fixed_folder=True)
                elif reply.clickedButton() == save_button:
                    logger.debug("\tJust Create Do nothing.")
            else:
                logger.warning("\tThere are already folder skipped.")
            self.asset_dir_TREEVIEW.update()

def run():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    global win
    win = FileManagerBlender()
    win.show()
    return win

if __name__ == "__main__":
    run()
