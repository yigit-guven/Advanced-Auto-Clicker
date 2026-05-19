import os
import sys
import shutil
import subprocess
import time
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QCheckBox, QFileDialog, 
                             QProgressBar, QStackedWidget, QWidget, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from styles import MAIN_STYLE

class InstallationWorker(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal(bool, str)

    def __init__(self, install_dir, create_desktop, create_start_menu):
        super().__init__()
        self.install_dir = install_dir
        self.create_desktop = create_desktop
        self.create_start_menu = create_start_menu

    def run(self):
        try:
            self.progress.emit(10)
            time.sleep(0.3)
            
            # Create destination folder
            os.makedirs(self.install_dir, exist_ok=True)
            self.progress.emit(30)
            time.sleep(0.3)
            
            # Copy executable
            current_exe = os.path.abspath(sys.executable)
            target_exe = os.path.join(self.install_dir, "AdvancedAutoClicker.exe")
            
            # If target exe already exists, try to delete it
            if os.path.exists(target_exe):
                try:
                    os.remove(target_exe)
                except OSError:
                    time.sleep(0.5)
                    os.remove(target_exe)
                    
            shutil.copy2(current_exe, target_exe)
            self.progress.emit(60)
            time.sleep(0.3)
            
            # Create shortcuts
            if self.create_desktop:
                desktop_dir = os.path.expanduser("~\\Desktop")
                shortcut_path = os.path.join(desktop_dir, "Advanced Auto Clicker.lnk")
                self.create_shortcut(target_exe, shortcut_path)
                
            self.progress.emit(80)
            time.sleep(0.2)
            
            if self.create_start_menu:
                appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
                start_menu_dir = os.path.join(appdata, "Microsoft\\Windows\\Start Menu\\Programs")
                shortcut_path = os.path.join(start_menu_dir, "Advanced Auto Clicker.lnk")
                self.create_shortcut(target_exe, shortcut_path)
                
            self.progress.emit(100)
            self.completed.emit(True, target_exe)
        except Exception as e:
            self.completed.emit(False, str(e))

    def create_shortcut(self, target_path, shortcut_path):
        try:
            ps_command = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{target_path}'
            $Shortcut.WorkingDirectory = '{os.path.dirname(target_path)}'
            $Shortcut.IconLocation = '{target_path},0'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return False

class InstallerWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Auto Clicker Setup")
        self.setFixedSize(500, 360)
        self.setStyleSheet(MAIN_STYLE)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Set Window Icon
        def get_resource_path(relative_path):
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
        self.setWindowIcon(QIcon(get_resource_path("icon.png")))
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 25, 25, 25)
        
        self.stacked = QStackedWidget()
        self.layout.addWidget(self.stacked)
        
        # Setup pages
        self._init_welcome_page()
        self._init_config_page()
        self._init_progress_page()
        self._init_finished_page()
        
        self.result_status = False # False = portable run, True = installed run
        self.installed_path = ""

    def _init_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        title = QLabel("Advanced Auto Clicker Setup")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #22d3ee;")
        layout.addWidget(title)
        
        desc = QLabel(
            "Welcome to the Advanced Auto Clicker installation wizard.\n\n"
            "This installer will copy the program to your local directory and create shortcuts for easier access.\n\n"
            "If you do not want to install, you can run the application directly in Portable mode."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 18px;")
        layout.addWidget(desc)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        portable_btn = QPushButton("Run Portable")
        portable_btn.setFixedSize(140, 40)
        portable_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        portable_btn.clicked.connect(self.reject) # Reject closes the dialog, continuing normal app startup
        
        install_btn = QPushButton("Install Now")
        install_btn.setObjectName("Primary")
        install_btn.setFixedSize(140, 40)
        install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        install_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        
        btn_layout.addWidget(portable_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(install_btn)
        layout.addLayout(btn_layout)
        
        self.stacked.addWidget(page)

    def _init_config_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        title = QLabel("Choose Installation Location")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #22d3ee;")
        layout.addWidget(title)
        
        # Path selection
        path_label = QLabel("Destination Folder:")
        path_label.setStyleSheet("color: #e2e8f0; font-weight: bold;")
        layout.addWidget(path_label)
        
        path_layout = QHBoxLayout()
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        self.default_dir = os.path.join(local_appdata, "Programs", "AdvancedAutoClicker")
        
        self.path_input = QLineEdit(self.default_dir)
        self.path_input.setStyleSheet("padding: 8px;")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedSize(90, 34)
        browse_btn.clicked.connect(self._browse_folder)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Shortcuts checkboxes
        self.desktop_check = QCheckBox("Create Desktop shortcut")
        self.desktop_check.setChecked(True)
        layout.addWidget(self.desktop_check)
        
        self.start_menu_check = QCheckBox("Create Start Menu shortcut")
        self.start_menu_check.setChecked(True)
        layout.addWidget(self.start_menu_check)
        
        layout.addStretch()
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(100, 36)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
        
        install_btn = QPushButton("Install")
        install_btn.setObjectName("Primary")
        install_btn.setFixedSize(100, 36)
        install_btn.clicked.connect(self._start_installation)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(install_btn)
        layout.addLayout(nav_layout)
        
        self.stacked.addWidget(page)

    def _init_progress_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        title = QLabel("Installing Files")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #22d3ee;")
        layout.addWidget(title)
        
        self.progress_label = QLabel("Preparing installation...")
        self.progress_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #334155;
                background-color: #0f172a;
                border-radius: 6px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #22d3ee;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        layout.addStretch()
        
        self.stacked.addWidget(page)

    def _init_finished_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        title = QLabel("Installation Completed")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #22d3ee;")
        layout.addWidget(title)
        
        desc = QLabel(
            "Advanced Auto Clicker has been successfully installed on your computer.\n\n"
            "You can close this installer to start using the app. The installer file will be cleaned up automatically."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 18px;")
        layout.addWidget(desc)
        
        self.launch_check = QCheckBox("Launch Advanced Auto Clicker now")
        self.launch_check.setChecked(True)
        layout.addWidget(self.launch_check)
        layout.addStretch()
        
        finish_btn = QPushButton("Finish")
        finish_btn.setObjectName("Primary")
        finish_btn.setFixedSize(120, 38)
        finish_btn.clicked.connect(self._on_finish)
        
        layout.addWidget(finish_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.stacked.addWidget(page)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Install Directory", self.path_input.text())
        if folder:
            self.path_input.setText(os.path.normpath(folder))

    def _start_installation(self):
        self.stacked.setCurrentIndex(2)
        self.progress_label.setText("Copying files...")
        
        self.worker = InstallationWorker(
            self.path_input.text(),
            self.desktop_check.isChecked(),
            self.start_menu_check.isChecked()
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.completed.connect(self._on_completed)
        self.worker.start()

    def _on_progress(self, val):
        self.progress_bar.setValue(val)
        if val == 30:
            self.progress_label.setText("Creating shortcuts...")
        elif val == 60:
            self.progress_label.setText("Configuring application path...")
        elif val == 100:
            self.progress_label.setText("Done!")

    def _on_completed(self, success, details):
        if success:
            self.installed_path = details
            self.stacked.setCurrentIndex(3)
        else:
            self.progress_label.setText(f"Installation failed: {details}")
            self.progress_label.setStyleSheet("color: #f43f5e;")

    def _on_finish(self):
        self.result_status = True
        if self.launch_check.isChecked():
            # Start the newly installed executable with cleanups
            current_exe = os.path.abspath(sys.executable)
            subprocess.Popen([self.installed_path, "--cleanup", current_exe], close_fds=True)
        self.accept()
