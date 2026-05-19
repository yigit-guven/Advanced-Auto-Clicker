
import sys
import os
import shutil
import time
import subprocess
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QPalette, QColor
from pynput import keyboard
import pyautogui

from dashboard import DashboardWindow
from overlay import OverlayWindow
from engine import engine

def handle_exe_deduplication():
    # Only run if packaged as a PyInstaller executable
    if not getattr(sys, 'frozen', False):
        return

    current_exe_path = os.path.abspath(sys.executable)
    current_exe_dir = os.path.dirname(current_exe_path)
    current_exe_name = os.path.basename(current_exe_path)
    
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
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        try:
            if key == keyboard.Key.f7:
                self.capture_signal.emit()
            elif key == keyboard.Key.f6:
                self.toggle_signal.emit()
            elif key == keyboard.Key.f8:
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

class AppController:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
            setup_dark_theme(self.app)
        
        self.points = []
        
        self.dashboard = DashboardWindow()
        self.overlay = OverlayWindow()
        self.hotkeys = HotkeyListener()
        self.bridge = EngineBridge()
        engine.on_active_change = self.bridge.active_change.emit
        
        # Connect Bridge Signals
        self.bridge.active_change.connect(self.overlay.highlight_point)
        
        # Check for updates asynchronously
        self.update_checker = UpdateChecker("1.0.2")
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
        
        # Connect Overlay Signals
        self.overlay.point_moved.connect(self.move_point)
        self.overlay.point_removed.connect(self.remove_point)
        
        # Connect Hotkey Signals
        self.hotkeys.capture_signal.connect(self.capture_point)
        self.hotkeys.toggle_signal.connect(self.toggle_engine)
        self.hotkeys.clear_signal.connect(self.clear_points)
        
        self.dashboard.show()

    def capture_point(self):
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

    def update_point(self, index, data):
        if 0 <= index < len(self.points):
            self.points[index] = data
            self.overlay.update_points(self.points)

    def move_point(self, index, x, y):
        if 0 <= index < len(self.points):
            self.points[index]["x"] = x
            self.points[index]["y"] = y
            self.dashboard.update_point_coords(index, x, y)

    def move_point_up(self, index):
        if 0 < index < len(self.points):
            self.points[index], self.points[index - 1] = self.points[index - 1], self.points[index]
            self.refresh_ui()

    def move_point_down(self, index):
        if 0 <= index < len(self.points) - 1:
            self.points[index], self.points[index + 1] = self.points[index + 1], self.points[index]
            self.refresh_ui()

    def remove_point(self, index):
        if 0 <= index < len(self.points):
            self.points.pop(index)
            self.refresh_ui()

    def clear_points(self):
        self.points = []
        self.refresh_ui()
        self.stop_engine()

    def refresh_ui(self):
        self.dashboard.refresh_list(self.points)
        self.overlay.update_points(self.points)

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

if __name__ == "__main__":
    handle_exe_deduplication()
    
    # Check if we should show the installer wizard
    if getattr(sys, 'frozen', False) and "--cleanup" not in sys.argv:
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        installed_dir = os.path.join(local_appdata, "Programs", "AdvancedAutoClicker")
        installed_exe = os.path.join(installed_dir, "AdvancedAutoClicker.exe")
        
        current_exe = os.path.abspath(sys.executable)
        
        # If we are NOT running the installed version, open the installer wizard
        if current_exe.lower() != installed_exe.lower():
            app = QApplication(sys.argv)
            setup_dark_theme(app)
            
            from installer import InstallerWindow
            wizard = InstallerWindow()
            wizard.exec()
            
            # If the user completed the installation, the installer spawned the new process.
            # We exit the current process.
            if wizard.result_status:
                sys.exit(0)
                
    controller = AppController()
    controller.run()
