
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QScrollArea, QFrame, 
                             QComboBox, QDoubleSpinBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from styles import MAIN_STYLE

class PointConfigCard(QFrame):
    removed = pyqtSignal(int)
    updated = pyqtSignal(int, dict)

    def __init__(self, index, data):
        super().__init__()
        self.setObjectName("Card")
        self.index = index
        self.data = data
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # Header Row: #Index | Position | Delete
        top_layout = QHBoxLayout()
        idx_label = QLabel(f"ACTION #{index + 1}")
        idx_label.setStyleSheet("font-weight: 800; color: #22d3ee; font-size: 16px;")
        
        coord_label = QLabel(f"📍 {data['x']}, {data['y']}")
        coord_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        
        del_btn = QPushButton("X")
        del_btn.setObjectName("GhostDanger")
        del_btn.setFixedSize(32, 32)
        del_btn.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        del_btn.setToolTip("Delete this action")
        del_btn.clicked.connect(lambda: self.removed.emit(self.index))
        
        top_layout.addWidget(idx_label)
        top_layout.addStretch()
        top_layout.addWidget(coord_label)
        top_layout.addSpacing(10)
        top_layout.addWidget(del_btn)
        main_layout.addLayout(top_layout)

        # Settings Row
        settings_layout = QHBoxLayout()
        
        # Action Group
        v_action = QVBoxLayout()
        v_action.addWidget(QLabel("Type"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Left Click", "Right Click", "Double Click", "Hold Left", "Hold Right", "Key Press", "Hold Key"])
        action_map = {
            "left_click": 0, "right_click": 1, "double_click": 2, 
            "hold_left": 3, "hold_right": 4, "key_press": 5, "hold_key": 6
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
        
        settings_layout.addLayout(self.v_extra, 1)
        
        main_layout.addLayout(settings_layout)
        self._update_visibility()

    def _update_visibility(self):
        action = self.action_combo.currentText()
        is_key = "Key" in action
        is_hold = "Hold" in action
        
        self.key_input.setVisible(is_key)
        self.dur_spin.setVisible(is_hold)
        self.extra_label.setVisible(is_key or is_hold)
        if is_key: self.extra_label.setText("Key")
        elif is_hold: self.extra_label.setText("Duration")

    def _on_change(self):
        self._update_visibility()
        action_keys = ["left_click", "right_click", "double_click", "hold_left", "hold_right", "key_press", "hold_key"]
        new_data = {
            **self.data,
            "action": action_keys[self.action_combo.currentIndex()],
            "delay_before": self.delay_spin.value(),
            "key": self.key_input.text(),
            "duration": self.dur_spin.value()
        }
        self.updated.emit(self.index, new_data)

class DashboardWindow(QMainWindow):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    point_updated = pyqtSignal(int, dict)
    point_removed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Auto Clicker")
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
        title = QLabel("ADVANCED AUTO CLICKER")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Design your sequence, then press F6 to run")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px; margin-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
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

    def refresh_list(self, points):
        # Clear layout
        for i in reversed(range(self.list_layout.count())): 
            self.list_layout.itemAt(i).widget().setParent(None)
            
        for i, pt in enumerate(points):
            card = PointConfigCard(i, pt)
            card.removed.connect(self.point_removed.emit)
            card.updated.connect(self.point_updated.emit)
            self.list_layout.addWidget(card)
