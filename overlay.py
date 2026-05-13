
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QRegion
from styles import OVERLAY_STYLE

class OverlayCircle(QFrame):
    moved = pyqtSignal(int, int, int)  # index, x, y
    removed = pyqtSignal(int)

    def __init__(self, parent, x, y, index):
        super().__init__(parent)
        self.index = index
        self.setFixedSize(80, 80)  # Larger to accommodate buttons
        self.move(x - 40, y - 40)
        
        # Main Circle Label
        self.circle = QLabel(str(index + 1), self)
        self.circle.setFixedSize(50, 50)
        self.circle.move(15, 15)
        self.circle.setStyleSheet(OVERLAY_STYLE)
        self.circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Delete Button (Top Right)
        self.del_btn = QPushButton("×", self)
        self.del_btn.setFixedSize(22, 22)
        self.del_btn.move(50, 0)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: #f43f5e;
                color: white;
                border-radius: 11px;
                font-weight: bold;
                border: 2px solid #0f172a;
            }
            QPushButton:hover { background-color: #fb7185; }
        """)
        self.del_btn.clicked.connect(lambda: self.removed.emit(self.index))
        self.del_btn.hide()
        
        # Drag Handle (Bottom Left)
        self.drag_handle = QLabel("✥", self)
        self.drag_handle.setFixedSize(22, 22)
        self.drag_handle.move(5, 50)
        self.drag_handle.setStyleSheet("""
            background-color: #22d3ee;
            color: #0f172a;
            border-radius: 11px;
            font-weight: bold;
            border: 2px solid #0f172a;
            qproperty-alignment: 'AlignCenter';
        """)
        self.drag_handle.hide()
        
        self.dragging = False
        self.drag_start_pos = QPoint()

    def enterEvent(self, event):
        if not self.window().is_running:
            self.del_btn.show()
            self.drag_handle.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.del_btn.hide()
        self.drag_handle.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.window().is_running:
            # Check if clicking near drag handle (bottom left)
            if QRect(0, 40, 40, 40).contains(event.pos()):
                self.dragging = True
                self.drag_start_pos = event.globalPosition().toPoint() - self.pos()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_start_pos
            self.move(new_pos)
            # Notify parent of coordinate change (center of 50x50 circle)
            self.moved.emit(self.index, new_pos.x() + 40, new_pos.y() + 40)
            self.window().update_mask()
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)

    def set_active(self, active=True):
        if active:
            self.circle.setStyleSheet(OVERLAY_STYLE + "border: 4px solid #f472b6; background-color: rgba(244, 114, 182, 0.4);")
        else:
            self.circle.setStyleSheet(OVERLAY_STYLE)

class OverlayWindow(QWidget):
    point_moved = pyqtSignal(int, int, int)
    point_removed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        self.circles = []
        self.is_running = False
        self.update_mask()

    def set_running(self, running):
        self.is_running = running
        if running:
            self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, False)
        self.show() # Refresh flags
        self.update_mask()

    def update_mask(self):
        if self.is_running:
            # When running, the whole window is transparent for input anyway
            self.setMask(QRegion()) 
            return
            
        # When not running, we only want the circles to be interactive
        region = QRegion()
        for c in self.circles:
            region = region.united(QRegion(c.geometry()))
        self.setMask(region)

    def update_points(self, points):
        # Clear old circles
        for c in self.circles:
            c.deleteLater()
        self.circles = []
        
        # Add new circles
        for i, pt in enumerate(points):
            circle = OverlayCircle(self, pt['x'], pt['y'], i)
            circle.moved.connect(self.point_moved.emit)
            circle.removed.connect(self.point_removed.emit)
            circle.show()
            self.circles.append(circle)
        self.update_mask()

    def highlight_point(self, index):
        for i, circle in enumerate(self.circles):
            circle.set_active(i == index)
