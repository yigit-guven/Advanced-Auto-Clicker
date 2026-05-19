
import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QScrollArea, QFrame, 
                             QComboBox, QDoubleSpinBox, QLineEdit, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from styles import MAIN_STYLE

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

class PointConfigCard(QFrame):
    removed = pyqtSignal(int)
    updated = pyqtSignal(int, dict)
    moved_up = pyqtSignal(int)
    moved_down = pyqtSignal(int)

    def __init__(self, index, data, total_count):
        super().__init__()
        self.setObjectName("Card")
        self.index = index
        self.data = data
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # Header Row: #Index | Position | Order Buttons | Delete
        top_layout = QHBoxLayout()
        idx_label = QLabel(f"ACTION #{index + 1}")
        idx_label.setStyleSheet("font-weight: 800; color: #22d3ee; font-size: 16px;")
        
        self.coord_label = QLabel(f"📍 {data['x']}, {data['y']}")
        self.coord_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        
        # Reorder buttons
        up_btn = QPushButton("▲")
        up_btn.setObjectName("OrderBtn")
        up_btn.setFixedSize(28, 28)
        up_btn.setToolTip("Move up")
        up_btn.clicked.connect(lambda: self.moved_up.emit(self.index))
        if index == 0:
            up_btn.setEnabled(False)
            up_btn.setStyleSheet("color: #475569; background-color: #1e293b; border: 1px solid #334155;")
            
        down_btn = QPushButton("▼")
        down_btn.setObjectName("OrderBtn")
        down_btn.setFixedSize(28, 28)
        down_btn.setToolTip("Move down")
        down_btn.clicked.connect(lambda: self.moved_down.emit(self.index))
        if index == total_count - 1:
            down_btn.setEnabled(False)
            down_btn.setStyleSheet("color: #475569; background-color: #1e293b; border: 1px solid #334155;")
        
        del_btn = QPushButton("X")
        del_btn.setObjectName("GhostDanger")
        del_btn.setFixedSize(32, 32)
        del_btn.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        del_btn.setToolTip("Delete this action")
        del_btn.clicked.connect(lambda: self.removed.emit(self.index))
        
        top_layout.addWidget(idx_label)
        top_layout.addStretch()
        top_layout.addWidget(self.coord_label)
        top_layout.addSpacing(10)
        top_layout.addWidget(up_btn)
        top_layout.addWidget(down_btn)
        top_layout.addSpacing(5)
        top_layout.addWidget(del_btn)
        main_layout.addLayout(top_layout)

        # Settings Row
        settings_layout = QHBoxLayout()
        
        # Action Group
        v_action = QVBoxLayout()
        v_action.addWidget(QLabel("Type"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Left Click", "Right Click", "Double Click", "Hold Left", "Hold Right", "Key Press", "Hold Key", "Type Text"])
        action_map = {
            "left_click": 0, "right_click": 1, "double_click": 2, 
            "hold_left": 3, "hold_right": 4, "key_press": 5, "hold_key": 6, "type_text": 7
        }
        self.action_combo.setCurrentIndex(action_map.get(data.get('action', 'left_click'), 0))
        self.action_combo.currentIndexChanged.connect(self._on_change)
        v_action.addWidget(self.action_combo)
        settings_layout.addLayout(v_action, 2)
        
        # Delay Group
        v_delay = QVBoxLayout()
        v_delay.addWidget(QLabel("Wait (s)"))
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0, 3600)
        self.delay_spin.setValue(data.get('delay_before', 0.1))
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setSuffix("s")
        self.delay_spin.valueChanged.connect(self._on_change)
        v_delay.addWidget(self.delay_spin)
        settings_layout.addLayout(v_delay, 1)
        
        # Extra Settings Group (Key or Duration)
        self.v_extra = QVBoxLayout()
        self.extra_label = QLabel("Extra")
        self.v_extra.addWidget(self.extra_label)
        
        self.key_input = QLineEdit(data.get('key', 'f'))
        self.key_input.setPlaceholderText("e.g. 'a', 'space'")
        self.key_input.textChanged.connect(self._on_change)
        self.v_extra.addWidget(self.key_input)
        
        self.dur_spin = QDoubleSpinBox()
        self.dur_spin.setRange(0.1, 3600)
        self.dur_spin.setSuffix("s hold")
        self.dur_spin.setValue(data.get('duration', 1.0))
        self.dur_spin.valueChanged.connect(self._on_change)
        self.v_extra.addWidget(self.dur_spin)

        self.text_input = QLineEdit(data.get('text', 'Hello World!'))
        self.text_input.setPlaceholderText("Enter sentence...")
        self.text_input.textChanged.connect(self._on_change)
        self.v_extra.addWidget(self.text_input)

        self.enter_check = QCheckBox("Press Enter")
        self.enter_check.setChecked(data.get('press_enter', False))
        self.enter_check.stateChanged.connect(self._on_change)
        self.v_extra.addWidget(self.enter_check)
        
        settings_layout.addLayout(self.v_extra, 1)
        
        main_layout.addLayout(settings_layout)
        self._update_visibility()

    def _update_visibility(self):
        action = self.action_combo.currentText()
        is_key = "Key" in action
        is_hold = "Hold" in action
        is_type = "Type Text" in action
        
        self.key_input.setVisible(is_key)
        self.dur_spin.setVisible(is_hold)
        self.text_input.setVisible(is_type)
        self.enter_check.setVisible(is_type)
        
        self.extra_label.setVisible(is_key or is_hold or is_type)
        if is_key: self.extra_label.setText("Key")
        elif is_hold: self.extra_label.setText("Duration")
        elif is_type: self.extra_label.setText("Text")

    def _on_change(self):
        self._update_visibility()
        action_keys = ["left_click", "right_click", "double_click", "hold_left", "hold_right", "key_press", "hold_key", "type_text"]
        new_data = {
            **self.data,
            "action": action_keys[self.action_combo.currentIndex()],
            "delay_before": self.delay_spin.value(),
            "key": self.key_input.text(),
            "duration": self.dur_spin.value(),
            "text": self.text_input.text(),
            "press_enter": self.enter_check.isChecked()
        }
        self.updated.emit(self.index, new_data)

    def update_coordinates(self, x, y):
        self.data['x'] = x
        self.data['y'] = y
        self.coord_label.setText(f"📍 {x}, {y}")

class DashboardWindow(QMainWindow):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    point_updated = pyqtSignal(int, dict)
    point_removed = pyqtSignal(int)
    point_moved_up = pyqtSignal(int)
    point_moved_down = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.cards = []
        self.setWindowTitle("Advanced Auto Clicker v1.0.2")
        self.setWindowIcon(QIcon(get_resource_path("icon.png")))
        self.setMinimumSize(550, 700)
        self.setStyleSheet(MAIN_STYLE)
        
        # Make window always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Section
        header_layout = QVBoxLayout()
        title = QLabel("ADVANCED AUTO CLICKER v1.0.2")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Design your sequence, then press F6 to run")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px; margin-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        # Update Banner (Hidden by default)
        self.update_banner = QFrame()
        self.update_banner.setObjectName("UpdateBanner")
        update_banner_layout = QHBoxLayout(self.update_banner)
        update_banner_layout.setContentsMargins(15, 10, 15, 10)
        
        self.update_label = QLabel("🚀 Update Available!")
        self.update_label.setStyleSheet("color: #0f172a; font-weight: bold; font-size: 13px; background: transparent;")
        
        self.update_btn = QPushButton("Download Now")
        self.update_btn.setObjectName("UpdateBtn")
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        update_banner_layout.addWidget(self.update_label)
        update_banner_layout.addStretch()
        update_banner_layout.addWidget(self.update_btn)
        self.update_banner.hide()
        main_layout.addWidget(self.update_banner)
        
        # Global Controls
        ctrl_card = QFrame()
        ctrl_card.setObjectName("Card")
        ctrl_card.setStyleSheet("background-color: #1e293b; border: 2px solid #334155;")
        ctrl_layout = QHBoxLayout(ctrl_card)
        
        self.status_btn = QPushButton("START SEQUENCE (F6)")
        self.status_btn.setObjectName("Primary")
        self.status_btn.setFixedHeight(50)
        self.status_btn.clicked.connect(self._toggle_status)
        
        clear_btn = QPushButton("RESET ALL (F8)")
        clear_btn.setObjectName("Danger")
        clear_btn.setFixedHeight(50)
        clear_btn.clicked.connect(self.clear_requested.emit)
        
        ctrl_layout.addWidget(self.status_btn, 2)
        ctrl_layout.addWidget(clear_btn, 1)
        main_layout.addWidget(ctrl_card)
        
        # Quick Guide
        guide_layout = QHBoxLayout()
        guide_layout.setContentsMargins(5, 10, 5, 10)
        def create_badge(text, color):
            l = QLabel(text)
            l.setStyleSheet(f"background-color: {color}; color: #0f172a; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;")
            return l

        guide_layout.addWidget(create_badge("F7", "#22d3ee"))
        guide_layout.addWidget(QLabel("Add Point"))
        guide_layout.addStretch()
        guide_layout.addWidget(create_badge("F6", "#fbbf24"))
        guide_layout.addWidget(QLabel("Run/Stop"))
        guide_layout.addStretch()
        guide_layout.addWidget(create_badge("F8", "#f43f5e"))
        guide_layout.addWidget(QLabel("Clear"))
        main_layout.addLayout(guide_layout)
        
        # Points List Header
        list_header = QLabel("ACTIONS IN SEQUENCE")
        list_header.setStyleSheet("font-weight: bold; color: #64748b; font-size: 12px; margin-top: 10px;")
        main_layout.addWidget(list_header)

        # Points List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.list_widget = QWidget()
        self.list_widget.setObjectName("ListWidget")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(15)
        self.scroll.setWidget(self.list_widget)
        main_layout.addWidget(self.scroll)
        
        self.is_running = False

    def _toggle_status(self):
        if self.is_running:
            self.stop_requested.emit()
        else:
            self.start_requested.emit()

    def set_running_state(self, running: bool):
        self.is_running = running
        self.status_btn.setText("STOP (F6)" if running else "START (F6)")
        self.status_btn.setStyleSheet("background-color: #f43f5e;" if running else "background-color: #22d3ee;")

    def show_update_notification(self, latest_version, download_url):
        self.update_label.setText(f"🚀 New Version Available: {latest_version}!")
        self.update_banner.show()
        
        # Disconnect any previous connections to avoid multiple opens
        try:
            self.update_btn.clicked.disconnect()
        except TypeError:
            pass
            
        import webbrowser
        self.update_btn.clicked.connect(lambda: webbrowser.open(download_url))

    def refresh_list(self, points):
        # Clear layout and delete widgets properly to prevent orphan windows
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
        self.cards = []
            
        total_count = len(points)
        for i, pt in enumerate(points):
            card = PointConfigCard(i, pt, total_count)
            card.removed.connect(self.point_removed.emit)
            card.updated.connect(self.point_updated.emit)
            card.moved_up.connect(self.point_moved_up.emit)
            card.moved_down.connect(self.point_moved_down.emit)
            self.list_layout.addWidget(card)
            self.cards.append(card)

    def update_point_coords(self, index, x, y):
        if 0 <= index < len(self.cards):
            self.cards[index].update_coordinates(x, y)
