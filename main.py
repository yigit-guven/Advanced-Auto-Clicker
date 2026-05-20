
import sys
import os
import shutil
import time
import subprocess
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QFormLayout)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread, Qt
from PyQt6.QtGui import QPalette, QColor
from pynput import keyboard
import pyautogui

from dashboard import DashboardWindow
from overlay import OverlayWindow
from engine import engine
from version import VERSION

def handle_exe_deduplication():
    # Only run if packaged as a PyInstaller executable
    if not getattr(sys, 'frozen', False):
        return

    current_exe_path = os.path.abspath(sys.executable)
    current_exe_dir = os.path.dirname(current_exe_path)
    current_exe_name = os.path.basename(current_exe_path)
    if "installer" in current_exe_name.lower():
        return
    
    target_exe_name = "AdvancedAutoClicker.exe"
    target_exe_path = os.path.join(current_exe_dir, target_exe_name)

    # 1. Clean up the duplicate loader file that started us
    if "--cleanup" in sys.argv:
        try:
            idx = sys.argv.index("--cleanup")
            path_to_delete = sys.argv[idx + 1]
            if os.path.exists(path_to_delete):
                # Wait for the caller process to exit
                time.sleep(1.2)
                os.remove(path_to_delete)
        except Exception as e:
            print(f"Cleanup of duplicate failed: {e}")
            
    # 2. If running as a duplicate (e.g. AdvancedAutoClicker (1).exe), overwrite the main exe and launch it
    if current_exe_name.lower() != target_exe_name.lower():
        try:
            # Delete old main executable if not running
            if os.path.exists(target_exe_path):
                try:
                    os.remove(target_exe_path)
                except OSError:
                    # If it's locked/running, we can't overwrite it
                    return
            
            # Copy ourselves to the target filename
            shutil.copy2(current_exe_path, target_exe_path)
            
            # Spawn the clean target exe, telling it to delete this launcher file
            subprocess.Popen([target_exe_path, "--cleanup", current_exe_path], close_fds=True)
            sys.exit(0)
        except Exception as e:
            print(f"Self-replacement failed: {e}")

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version

    def run(self):
        try:
            import urllib.request
            import json
            req = urllib.request.Request(
                "https://api.github.com/repos/yigit-guven/Advanced-Auto-Clicker/releases/latest",
                headers={"User-Agent": "Advanced-Auto-Clicker-Update-Checker"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "")
                html_url = data.get("html_url", "https://github.com/yigit-guven/Advanced-Auto-Clicker/releases")
                if latest_tag:
                    if self.is_newer(latest_tag, self.current_version):
                        self.update_available.emit(latest_tag, html_url)
        except Exception as e:
            # Silent fallback
            print(f"Update check failed: {e}")

    def is_newer(self, latest, current):
        def parse(v):
            v = v.strip().lstrip('v')
            try:
                return list(map(int, v.split('.')))
            except ValueError:
                return [0, 0, 0]
        return parse(latest) > parse(current)

class EngineBridge(QObject):
    active_change = pyqtSignal(int)

class HotkeyListener(QObject):
    capture_signal = pyqtSignal()
    toggle_signal = pyqtSignal()
    clear_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.capture_key = "F7"
        self.toggle_key = "F6"
        self.clear_key = "F8"
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def update_keys(self, capture, toggle, clear):
        self.capture_key = capture
        self.toggle_key = toggle
        self.clear_key = clear

    def _key_matches(self, event_key, target_str):
        try:
            if target_str.upper().startswith("F"):
                f_num = int(target_str[1:])
                expected_key = getattr(keyboard.Key, f"f{f_num}", None)
                if expected_key == event_key:
                    return True
            else:
                if hasattr(event_key, 'char') and event_key.char == target_str.lower():
                    return True
        except Exception:
            pass
        return False

    def _on_press(self, key):
        try:
            if self._key_matches(key, self.capture_key):
                self.capture_signal.emit()
            elif self._key_matches(key, self.toggle_key):
                self.toggle_signal.emit()
            elif self._key_matches(key, self.clear_key):
                self.clear_signal.emit()
        except AttributeError:
            pass

def setup_dark_theme(app):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e293b"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#334155"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#22d3ee"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#22d3ee"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#22d3ee"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#0f172a"))
    app.setPalette(palette)

class SettingsDialog(QDialog):
    def __init__(self, parent, current_theme, hotkeys, settings_flags):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(380)
        
        # Apply the current theme stylesheet to the settings dialog so it inherits colors
        from styles import get_theme_stylesheet
        self.setStyleSheet(get_theme_stylesheet(current_theme))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title_label = QLabel("SETTINGS")
        title_label.setObjectName("Title")
        layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Appearance Section
        theme_title = QLabel("Appearance")
        theme_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 5px; color: #94a3b8;")
        form_layout.addRow(theme_title)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Blue", "Light", "Matrix Green", "Sunset Purple"])
        self.theme_combo.setCurrentText(current_theme)
        form_layout.addRow("Theme:", self.theme_combo)
        
        # Hotkeys Section
        hotkeys_title = QLabel("Hotkey Bindings")
        hotkeys_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #94a3b8;")
        form_layout.addRow(hotkeys_title)
        
        f_keys = [f"F{i}" for i in range(1, 13)]
        
        self.toggle_combo = QComboBox()
        self.toggle_combo.addItems(f_keys)
        self.toggle_combo.setCurrentText(hotkeys.get("toggle", "F6"))
        form_layout.addRow("Start / Stop:", self.toggle_combo)
        
        self.capture_combo = QComboBox()
        self.capture_combo.addItems(f_keys)
        self.capture_combo.setCurrentText(hotkeys.get("capture", "F7"))
        form_layout.addRow("Add Point:", self.capture_combo)
        
        self.clear_combo = QComboBox()
        self.clear_combo.addItems(f_keys)
        self.clear_combo.setCurrentText(hotkeys.get("clear", "F8"))
        self.clear_combo.addItems(f_keys)
        self.clear_combo.setCurrentText(hotkeys.get("clear", "F8"))
        form_layout.addRow("Clear Sequence:", self.clear_combo)
        
        # Application Settings Section
        app_title = QLabel("Application Settings")
        app_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; color: #94a3b8;")
        form_layout.addRow(app_title)
        
        self.startup_check = QCheckBox("Run on Windows Startup")
        self.startup_check.setChecked(settings_flags.get("startup", False))
        form_layout.addRow(self.startup_check)
        
        self.tray_check = QCheckBox("Minimize to System Tray on close")
        self.tray_check.setChecked(settings_flags.get("tray", True))
        form_layout.addRow(self.tray_check)
        
        self.log_check = QCheckBox("Enable Background Logging")
        self.log_check.setChecked(settings_flags.get("logging", False))
        form_layout.addRow(self.log_check)
        
        layout.addLayout(form_layout)
        layout.addSpacing(10)
        
        # Custom styled action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("Primary")
        save_btn.clicked.connect(self.accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

class AppController:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)
            setup_dark_theme(self.app)
            
        # Enforce single instance
        from PyQt6.QtCore import QSharedMemory
        self.shared_memory = QSharedMemory("AdvancedAutoClicker_Mutex")
        if not self.shared_memory.create(1):
            sys.exit(0)
            
        self.run_on_startup = False
        self.minimize_to_tray = True
        self.enable_logging = False
        
        self.profiles = {"Default": []}
        self.current_profile = "Default"
        self.points = []
        
        self.dashboard = DashboardWindow()
        self.overlay = OverlayWindow()
        self.hotkeys = HotkeyListener()
        self.bridge = EngineBridge()
        engine.on_active_change = self.bridge.active_change.emit
        
        # Connect Bridge Signals
        self.bridge.active_change.connect(self.overlay.highlight_point)
        
        # Check for updates asynchronously
        self.update_checker = UpdateChecker(VERSION)
        self.update_checker.update_available.connect(self.dashboard.show_update_notification)
        self.update_checker.start()
        
        # Connect Dashboard Signals
        self.dashboard.start_requested.connect(self.start_engine)
        self.dashboard.stop_requested.connect(self.stop_engine)
        self.dashboard.clear_requested.connect(self.clear_points)
        self.dashboard.point_updated.connect(self.update_point)
        self.dashboard.point_removed.connect(self.remove_point)
        self.dashboard.point_moved_up.connect(self.move_point_up)
        self.dashboard.point_moved_down.connect(self.move_point_down)
        self.dashboard.settings_requested.connect(self.show_settings_dialog)
        self.dashboard.profile_changed.connect(self.on_profile_changed)
        self.dashboard.save_profile_requested.connect(self.on_save_profile)
        self.dashboard.delete_profile_requested.connect(self.on_delete_profile)
        self.dashboard.rename_profile_requested.connect(self.on_rename_profile)
        self.dashboard.add_empty_profile_requested.connect(self.on_add_empty_profile)
        
        # Connect Overlay Signals
        self.overlay.point_moved.connect(self.move_point)
        self.overlay.point_removed.connect(self.remove_point)
        
        # Connect Hotkey Signals
        self.hotkeys.capture_signal.connect(self.capture_point)
        self.hotkeys.toggle_signal.connect(self.toggle_engine)
        self.hotkeys.clear_signal.connect(self.clear_points)
        
        self.load_config()
        self.refresh_ui()
        self.setup_tray()
        self.setup_logging()
        self.dashboard.set_minimize_to_tray(self.minimize_to_tray)
        if "--hidden" not in sys.argv:
            self.dashboard.show()

    def get_config_path(self):
        base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        return os.path.join(base_dir, "config.json")

    def apply_theme(self, theme_name):
        self.dashboard.apply_theme(theme_name)
        self.overlay.apply_theme(theme_name)

    def show_settings_dialog(self):
        current_hotkeys = {
            "capture": self.hotkeys.capture_key,
            "toggle": self.hotkeys.toggle_key,
            "clear": self.hotkeys.clear_key
        }
        settings_flags = {
            "startup": self.run_on_startup,
            "tray": self.minimize_to_tray,
            "logging": self.enable_logging
        }
        dialog = SettingsDialog(self.dashboard, self.dashboard.current_theme, current_hotkeys, settings_flags)
        if dialog.exec():
            new_theme = dialog.theme_combo.currentText()
            new_capture = dialog.capture_combo.currentText()
            new_toggle = dialog.toggle_combo.currentText()
            new_clear = dialog.clear_combo.currentText()
            
            self.run_on_startup = dialog.startup_check.isChecked()
            self.minimize_to_tray = dialog.tray_check.isChecked()
            self.enable_logging = dialog.log_check.isChecked()
            
            self.apply_theme(new_theme)
            self.hotkeys.update_keys(new_capture, new_toggle, new_clear)
            self.dashboard.update_hotkey_labels(new_capture, new_toggle, new_clear)
            
            self.apply_startup_setting()
            self.setup_logging()
            self.dashboard.set_minimize_to_tray(self.minimize_to_tray)
            self.save_config()

    def load_config(self):
        try:
            path = self.get_config_path()
            theme_name = "Dark Blue"
            capture_key = "F7"
            toggle_key = "F6"
            clear_key = "F8"
            self.profiles = {"Default": []}
            self.current_profile = "Default"
            
            if os.path.exists(path):
                import json
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    if "profiles" in data:
                        self.profiles = data["profiles"]
                        self.current_profile = data.get("current_profile", list(self.profiles.keys())[0])
                    else:
                        legacy_points = data.get("points", [])
                        self.profiles = {"Default": legacy_points}
                        self.current_profile = "Default"

                    theme_name = data.get("theme", "Dark Blue")
                    capture_key = data.get("capture_key", "F7")
                    toggle_key = data.get("toggle_key", "F6")
                    clear_key = data.get("clear_key", "F8")
                    
                    self.run_on_startup = data.get("run_on_startup", False)
                    self.enable_logging = data.get("enable_logging", False)
                    self.minimize_to_tray = data.get("minimize_to_tray", True)
                else:
                    self.profiles = {"Default": data}
                    self.current_profile = "Default"
            
            for prof_name, pts in self.profiles.items():
                for p in pts:
                    p.setdefault("x", 0)
                    p.setdefault("y", 0)
                    p.setdefault("action", "left_click")
                    p.setdefault("delay_before", 0.1)
                    p.setdefault("delay_after", 0.1)
                    p.setdefault("key", "a")
                    p.setdefault("duration", 1.0)
                    p.setdefault("text", "Hello World!")
                    p.setdefault("press_enter", False)
            
            self.points = self.profiles.get(self.current_profile, [])
            self.apply_theme(theme_name)
            self.hotkeys.update_keys(capture_key, toggle_key, clear_key)
            self.dashboard.update_hotkey_labels(capture_key, toggle_key, clear_key)
        except Exception as e:
            print(f"Failed to load config: {e}")

    def save_config(self):
        try:
            self.profiles[self.current_profile] = self.points
            path = self.get_config_path()
            import json
            data = {
                "theme": self.dashboard.current_theme,
                "capture_key": self.hotkeys.capture_key,
                "toggle_key": self.hotkeys.toggle_key,
                "clear_key": self.hotkeys.clear_key,
                "profiles": self.profiles,
                "current_profile": self.current_profile,
                "run_on_startup": self.run_on_startup,
                "enable_logging": self.enable_logging,
                "minimize_to_tray": self.minimize_to_tray
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def capture_point(self):
        import logging
        logging.info("Capturing point")
        x, y = pyautogui.position()
        new_point = {
            "x": x,
            "y": y,
            "action": "left_click",
            "delay_before": 0.1,
            "delay_after": 0.1,
            "key": "a",
            "duration": 1.0,
            "text": "Hello World!",
            "press_enter": False
        }
        self.points.append(new_point)
        self.refresh_ui()
        self.save_config()

    def setup_tray(self):
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
        from PyQt6.QtGui import QAction, QIcon
        
        # Use existing method to get resource
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "icon.png")
            
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self.app)
        self.tray_icon.setToolTip("Advanced Auto Clicker")
        
        tray_menu = QMenu()
        show_action = QAction("Show Dashboard", self.app)
        show_action.triggered.connect(lambda: (self.dashboard.showNormal(), self.dashboard.activateWindow()))
        
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.dashboard.showNormal()
            self.dashboard.activateWindow()

    def quit_app(self):
        import logging
        logging.info("Quitting application")
        self.dashboard.force_close = True
        self.app.quit()

    def apply_startup_setting(self):
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            app_name = "AdvancedAutoClicker"
            if self.run_on_startup:
                exe_path = os.path.abspath(sys.executable)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --hidden')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except Exception:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def setup_logging(self):
        import logging
        from logging.handlers import RotatingFileHandler
        logger = logging.getLogger()
        
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        if self.enable_logging:
            logger.setLevel(logging.INFO)
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
            log_dir = os.path.join(local_appdata, "Programs", "AdvancedAutoClicker", "Logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "app.log")
            
            handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=1)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logging.info("Logging started")
        else:
            logger.addHandler(logging.NullHandler())

    def update_point(self, index, data):
        if 0 <= index < len(self.points):
            self.points[index] = data
            self.overlay.update_points(self.points)
            self.save_config()

    def move_point(self, index, x, y):
        if 0 <= index < len(self.points):
            self.points[index]["x"] = x
            self.points[index]["y"] = y
            self.dashboard.update_point_coords(index, x, y)
            self.save_config()

    def move_point_up(self, index):
        if 0 < index < len(self.points):
            self.points[index], self.points[index - 1] = self.points[index - 1], self.points[index]
            self.refresh_ui()
            self.save_config()

    def move_point_down(self, index):
        if 0 <= index < len(self.points) - 1:
            self.points[index], self.points[index + 1] = self.points[index + 1], self.points[index]
            self.refresh_ui()
            self.save_config()

    def remove_point(self, index):
        if 0 <= index < len(self.points):
            self.points.pop(index)
            self.refresh_ui()
            self.save_config()

    def clear_points(self):
        self.points = []
        self.refresh_ui()
        self.stop_engine()
        self.save_config()

    def refresh_ui(self):
        self.dashboard.set_profiles(list(self.profiles.keys()), self.current_profile)
        self.dashboard.refresh_list(self.points)
        self.overlay.update_points(self.points)

    def on_profile_changed(self, name):
        if name in self.profiles and name != self.current_profile:
            self.stop_engine()
            self.profiles[self.current_profile] = self.points
            self.current_profile = name
            self.points = self.profiles[name]
            self.refresh_ui()
            self.save_config()

    def on_save_profile(self, new_name):
        self.profiles[self.current_profile] = self.points
        if new_name not in self.profiles:
            import copy
            self.profiles[new_name] = copy.deepcopy(self.points)
        
        self.current_profile = new_name
        self.points = self.profiles[new_name]
        self.refresh_ui()
        self.save_config()

    def on_delete_profile(self, name):
        if name in self.profiles and len(self.profiles) > 1:
            del self.profiles[name]
            self.current_profile = list(self.profiles.keys())[0]
            self.points = self.profiles[self.current_profile]
            self.refresh_ui()
            self.save_config()

    def on_rename_profile(self, old_name, new_name):
        if old_name in self.profiles and new_name not in self.profiles:
            self.profiles[new_name] = self.profiles.pop(old_name)
            if self.current_profile == old_name:
                self.current_profile = new_name
            self.save_config()
            self.dashboard.set_profiles(list(self.profiles.keys()), self.current_profile)
            
    def on_add_empty_profile(self, new_name):
        if new_name and new_name not in self.profiles:
            self.profiles[new_name] = []
            self.current_profile = new_name
            self.points = self.profiles[self.current_profile]
            engine.set_points(self.points)
            self.save_config()
            self.dashboard.set_profiles(list(self.profiles.keys()), self.current_profile)
            self.refresh_ui()

    def start_engine(self):
        if not self.points: return
        self.overlay.set_running(True)
        engine.set_points(self.points)
        engine.start()
        self.dashboard.set_running_state(True)

    def stop_engine(self):
        engine.stop()
        self.overlay.set_running(False)
        self.dashboard.set_running_state(False)

    def toggle_engine(self):
        if engine.is_running:
            self.stop_engine()
        else:
            self.start_engine()

    def run(self):
        sys.exit(self.app.exec())

def handle_uninstallation():
    from PyQt6.QtWidgets import QApplication, QMessageBox
    import winreg
    
    app = QApplication(sys.argv)
    reply = QMessageBox.question(None, "Uninstall Advanced Auto Clicker", 
                                 "Are you sure you want to completely remove Advanced Auto Clicker and all of its components?", 
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if reply == QMessageBox.StandardButton.Yes:
        desktop_dir = os.path.expanduser("~\\Desktop")
        appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        start_menu_dir = os.path.join(appdata, "Microsoft\\Windows\\Start Menu\\Programs")
        
        shortcut_desktop = os.path.join(desktop_dir, "Advanced Auto Clicker.lnk")
        shortcut_start = os.path.join(start_menu_dir, "Advanced Auto Clicker.lnk")
        
        for p in [shortcut_desktop, shortcut_start]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\AdvancedAutoClicker")
        except Exception:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\AdvancedAutoClicker")
        except Exception:
            pass
            
        import tempfile
        install_dir = os.path.dirname(os.path.abspath(sys.executable))
        temp_bat = os.path.join(tempfile.gettempdir(), "uninstall_aac.bat")
        
        bat_content = f"""@echo off
timeout /t 2 /nobreak > NUL
rmdir /s /q "{install_dir}"
del "%~f0"
"""
        with open(temp_bat, "w") as f:
            f.write(bat_content)
            
        subprocess.Popen([temp_bat], creationflags=subprocess.CREATE_NO_WINDOW)
        
        QMessageBox.information(None, "Uninstalled", "Advanced Auto Clicker has been successfully removed from your computer.")
        sys.exit(0)
    else:
        sys.exit(0)

if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        handle_uninstallation()

    handle_exe_deduplication()
    
    if getattr(sys, 'frozen', False) and "--cleanup" not in sys.argv:
        from installer import get_previous_install_dir
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        reg_dir = get_previous_install_dir()
        installed_dir = reg_dir if reg_dir else os.path.join(local_appdata, "Programs", "AdvancedAutoClicker")
        installed_exe = os.path.join(installed_dir, "AdvancedAutoClicker.exe")
        
        current_exe = os.path.abspath(sys.executable)
        
        if current_exe.lower() != installed_exe.lower():
            app = QApplication(sys.argv)
            setup_dark_theme(app)
            
            from installer import InstallerWindow
            wizard = InstallerWindow()
            wizard.exec()
            
            if wizard.result_status:
                sys.exit(0)
                
    controller = AppController()
    controller.run()
