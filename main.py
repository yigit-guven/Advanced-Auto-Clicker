
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from pynput import keyboard
import pyautogui

from dashboard import DashboardWindow
from overlay import OverlayWindow
from engine import engine

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

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.points = []
        
        self.dashboard = DashboardWindow()
        self.overlay = OverlayWindow()
        self.hotkeys = HotkeyListener()
        self.bridge = EngineBridge()
        engine.on_active_change = self.bridge.active_change.emit
        
        # Connect Bridge Signals
        self.bridge.active_change.connect(self.overlay.highlight_point)
        
        # Connect Dashboard Signals
        self.dashboard.start_requested.connect(self.start_engine)
        self.dashboard.stop_requested.connect(self.stop_engine)
        self.dashboard.clear_requested.connect(self.clear_points)
        self.dashboard.point_updated.connect(self.update_point)
        self.dashboard.point_removed.connect(self.remove_point)
        
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
            "duration": 1.0
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
            self.dashboard.refresh_list(self.points)

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
    controller = AppController()
    controller.run()
