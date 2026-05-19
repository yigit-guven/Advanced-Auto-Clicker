
MAIN_STYLE = """
QMainWindow {
    background-color: #0f172a;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QLabel#Title {
    font-size: 24px;
    font-weight: bold;
    color: #22d3ee;
    margin-bottom: 10px;
}

QFrame#Card {
    background-color: #1e293b;
    border-radius: 12px;
    border: 1px solid #334155;
    padding: 10px;
}

QPushButton {
    background-color: #334155;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #475569;
}

QPushButton#Primary {
    background-color: #22d3ee;
    color: #0f172a;
}

QPushButton#Primary:hover {
    background-color: #67e8f9;
}

QPushButton#Danger {
    background-color: #f43f5e;
    color: #ffffff;
}

QPushButton#Danger:hover {
    background-color: #fb7185;
}

QPushButton#GhostDanger {
    background-color: #334155;
    color: white;
    border: 1px solid #475569;
    border-radius: 4px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#GhostDanger:hover {
    color: white;
    background-color: #f43f5e;
    border: 1px solid #f43f5e;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px;
    color: #f8fafc;
}

QScrollArea {
    border: none;
    background-color: #0f172a;
}

QWidget#ListWidget {
    background-color: #0f172a;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid #334155;
    selection-background-color: #22d3ee;
    selection-color: #0f172a;
    color: #f8fafc;
}

QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QFrame#UpdateBanner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #b45309);
    border-radius: 8px;
    border: 1px solid #f59e0b;
}

QPushButton#UpdateBtn {
    background-color: #0f172a;
    color: #fbbf24;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 12px;
    border: 1px solid #fbbf24;
}

QPushButton#UpdateBtn:hover {
    background-color: #1e293b;
    color: #ffffff;
}

QPushButton#OrderBtn {
    background-color: #334155;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    padding: 0px;
}

QPushButton#OrderBtn:hover {
    background-color: #475569;
    color: #22d3ee;
}
"""

OVERLAY_STYLE = """
QLabel {
    background-color: rgba(34, 211, 238, 0.2);
    border: 2px solid #22d3ee;
    border-radius: 25px;
    color: #ffffff;
    font-weight: bold;
    font-size: 18px;
    qproperty-alignment: 'AlignCenter';
}
"""
