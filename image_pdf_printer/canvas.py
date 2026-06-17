import sys
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter, QCursor
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
    QGraphicsSimpleTextItem, QGraphicsItem
)

class DraggablePageItem(QGraphicsRectItem):
    """
    A draggable rectangle representing a single printed page on the image canvas.
    Movement is constrained based on grid locking (lock horizontal or lock vertical).
    Supports aspect-ratio-locked resizing by dragging edges/corners.
    """
    def __init__(self, rect, row_idx, col_idx, page_num, parent=None):
        super().__init__(rect, parent)
        self.row_idx = row_idx
        self.col_idx = col_idx
        self.page_num = page_num
        
        # Dragging control flags
        self.lock_x = True
        self.lock_y = False
        self.fixed_x = rect.x()
        self.fixed_y = rect.y()
        self.boundary_rect = None  # QRectF of the image bounds
        self.on_changed_callback = None
        
        # Resize state
        self.resize_mode = 0  # 0=None, 1=TL, 2=TR, 3=BL, 4=BR, 5=L, 6=R, 7=T, 8=B
        self.is_resizing = False
        self.initial_rect = None
        self.initial_pos = None
        self.press_scene_pos = None
        
        # Configure flags for interaction
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        
        # Visual styling
        self.normal_color = QColor(0, 122, 255, 40)      # Semi-transparent blue
        self.hover_color = QColor(0, 122, 255, 75)       # Brighter blue on hover
        self.border_color = QColor(0, 122, 255)
        
        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(self.border_color, 2, Qt.PenStyle.DashLine))
        self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))

    def set_constraints(self, lock_x, lock_y, fixed_x, fixed_y, boundary_rect):
        """
        Configure the movement constraints.
        """
        self.lock_x = lock_x
        self.lock_y = lock_y
        self.fixed_x = fixed_x
        self.fixed_y = fixed_y
        self.boundary_rect = boundary_rect
        
        # Clamp initial position if needed
        self.setPos(self.itemChange(QGraphicsItem.GraphicsItemChange.ItemPositionChange, self.pos()))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            if getattr(self, "is_resizing", False):
                # Bypass locked grid alignment during active resize dragging
                return value
                
            new_pos = value  # QPointF
            
            # Target coordinates in item's parent space
            target_x = self.fixed_x if self.lock_x else new_pos.x()
            target_y = self.fixed_y if self.lock_y else new_pos.y()
            
            # Apply boundary constraints relative to the image
            if self.boundary_rect:
                w = self.rect().width()
                h = self.rect().height()
                bx = self.boundary_rect.x()
                by = self.boundary_rect.y()
                bw = self.boundary_rect.width()
                bh = self.boundary_rect.height()
                
                # Keep the rectangle within the image boundaries
                target_x = max(bx, min(target_x, bx + bw - w))
                target_y = max(by, min(target_y, by + bh - h))
            
            final_pos = QPointF(target_x, target_y)
            if self.on_changed_callback:
                self.on_changed_callback(self, final_pos)
            return final_pos
            
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        if not self.isSelected():
            self.setBrush(QBrush(self.hover_color))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            self.setBrush(QBrush(self.normal_color))
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        if self.isSelected():
            pos = event.pos()
            w = self.rect().width()
            h = self.rect().height()
            border = 8.0
            
            on_left = pos.x() < border
            on_right = pos.x() > w - border
            on_top = pos.y() < border
            on_bottom = pos.y() > h - border
            
            if on_left and on_top:
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif on_right and on_bottom:
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif on_right and on_top:
                self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif on_left and on_bottom:
                self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif on_left or on_right:
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            elif on_top or on_bottom:
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isSelected():
            pos = event.pos()
            w = self.rect().width()
            h = self.rect().height()
            border = 8.0
            
            on_left = pos.x() < border
            on_right = pos.x() > w - border
            on_top = pos.y() < border
            on_bottom = pos.y() > h - border
            
            self.resize_mode = 0
            if on_left and on_top:
                self.resize_mode = 1
            elif on_right and on_top:
                self.resize_mode = 2
            elif on_left and on_bottom:
                self.resize_mode = 3
            elif on_right and on_bottom:
                self.resize_mode = 4
            elif on_left:
                self.resize_mode = 5
            elif on_right:
                self.resize_mode = 6
            elif on_top:
                self.resize_mode = 7
            elif on_bottom:
                self.resize_mode = 8
                
            if self.resize_mode > 0:
                self.is_resizing = True
                self.initial_rect = self.rect()
                self.initial_pos = self.pos()
                self.press_scene_pos = event.scenePos()
                event.accept()
                return
                
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if getattr(self, "is_resizing", False) and self.resize_mode > 0:
            curr_scene_pos = event.scenePos()
            dx = curr_scene_pos.x() - self.press_scene_pos.x()
            dy = curr_scene_pos.y() - self.press_scene_pos.y()
            
            W = self.initial_rect.width()
            H = self.initial_rect.height()
            X = self.initial_pos.x()
            Y = self.initial_pos.y()
            
            ratio = H / W
            
            # Default values
            w_new = W
            h_new = H
            x_new = X
            y_new = Y
            
            mode = self.resize_mode
            
            # Calculate new size maintaining aspect ratio
            if mode == 6:  # Right
                w_new = max(20.0, W + dx)
                h_new = w_new * ratio
            elif mode == 8:  # Bottom
                h_new = max(20.0, H + dy)
                w_new = h_new / ratio
            elif mode == 4:  # Bottom-Right
                scale = max(0.1, ((W + dx) / W + (H + dy) / H) / 2.0)
                w_new = W * scale
                h_new = H * scale
            elif mode == 5:  # Left
                w_new = max(20.0, W - dx)
                h_new = w_new * ratio
                x_new = X + (W - w_new)
                y_new = Y + (H - h_new)
            elif mode == 7:  # Top
                h_new = max(20.0, H - dy)
                w_new = h_new / ratio
                x_new = X + (W - w_new)
                y_new = Y + (H - h_new)
            elif mode == 1:  # Top-Left
                scale = max(0.1, ((W - dx) / W + (H - dy) / H) / 2.0)
                w_new = W * scale
                h_new = H * scale
                x_new = X + (W - w_new)
                y_new = Y + (H - h_new)
            elif mode == 2:  # Top-Right
                scale = max(0.1, ((W + dx) / W + (H - dy) / H) / 2.0)
                w_new = W * scale
                h_new = H * scale
                y_new = Y + (H - h_new)
            elif mode == 3:  # Bottom-Left
                scale = max(0.1, ((W - dx) / W + (H + dy) / H) / 2.0)
                w_new = W * scale
                h_new = H * scale
                x_new = X + (W - w_new)
                
            # Boundary Clamping
            if self.boundary_rect:
                bx = self.boundary_rect.x()
                by = self.boundary_rect.y()
                bw = self.boundary_rect.width()
                bh = self.boundary_rect.height()
                
                # Check limits depending on fixed points
                if x_new < bx:
                    if mode in [1, 3, 5, 7]:  # right side is fixed
                        max_w = (X + W) - bx
                        w_new = min(w_new, max_w)
                        h_new = w_new * ratio
                        x_new = (X + W) - w_new
                        if mode in [1, 5, 7]:
                            y_new = (Y + H) - h_new
                    else:
                        x_new = bx
                        
                if y_new < by:
                    if mode in [1, 2, 5, 7]:  # bottom side is fixed
                        max_h = (Y + H) - by
                        h_new = min(h_new, max_h)
                        w_new = h_new / ratio
                        y_new = (Y + H) - h_new
                        if mode in [1, 5, 7]:
                            x_new = (X + W) - w_new
                    else:
                        y_new = by
                        
                if x_new + w_new > bx + bw:
                    w_new = bx + bw - x_new
                    h_new = w_new * ratio
                    
                if y_new + h_new > by + bh:
                    h_new = by + bh - y_new
                    w_new = h_new / ratio
            
            # Apply changes
            self.setPos(x_new, y_new)
            self.setRect(QRectF(0, 0, w_new, h_new))
            
            if self.on_changed_callback:
                self.on_changed_callback(self, QPointF(x_new, y_new))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if getattr(self, "is_resizing", False):
            self.is_resizing = False
            self.resize_mode = 0
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        # Draw the standard rectangle (brush and pen)
        super().paint(painter, option, widget)
        
        # Draw a custom overlay label in the center of the page rectangle
        rect = self.rect()
        painter.save()
        
        # Label text
        label = f"Page {self.page_num}\n({self.col_idx+1}, {self.row_idx+1})"
        
        # Setup font
        font = QFont("Outfit", 12, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Calculate label size and position
        metrics = painter.fontMetrics()
        lines = label.split('\n')
        text_w = max(metrics.horizontalAdvance(line) for line in lines)
        text_h = metrics.height() * len(lines)
        
        padding_x = 12
        padding_y = 8
        bg_w = text_w + padding_x * 2
        bg_h = text_h + padding_y * 2
        
        bg_x = rect.x() + (rect.width() - bg_w) / 2
        bg_y = rect.y() + (rect.height() - bg_h) / 2
        
        # Draw pill background
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(30, 30, 30, 220)))  # Dark background
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.drawRoundedRect(QRectF(bg_x, bg_y, bg_w, bg_h), 8, 8)
        
        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255)))
        for i, line in enumerate(lines):
            line_w = metrics.horizontalAdvance(line)
            lx = bg_x + (bg_w - line_w) / 2
            ly = bg_y + padding_y + metrics.ascent() + i * metrics.height()
            painter.drawText(QPointF(lx, ly), line)
            
        painter.restore()


class InteractiveGraphicsView(QGraphicsView):
    """
    QGraphicsView with support for smooth mouse wheel zoom and right-click pan.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform |
            QPainter.RenderHint.TextAntialiasing
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        # Pan state
        self._pan_active = False
        self._pan_start_pos = None
        self.zoom_changed_callback = None

    def wheelEvent(self, event):
        # Zoom parameters
        zoom_factor = 1.15
        if event.angleDelta().y() < 0:
            zoom_factor = 1.0 / zoom_factor
            
        # Calculate current scale
        current_scale = self.transform().m11()
        
        # Check scale bounds (5% to 40x)
        if 0.05 < current_scale * zoom_factor < 40.0:
            self.scale(zoom_factor, zoom_factor)
            if self.zoom_changed_callback:
                self.zoom_changed_callback(self.transform().m11())
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # Start panning
            self._pan_active = True
            self._pan_start_pos = event.position().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan_active:
            # Pan logic
            delta = event.position().toPoint() - self._pan_start_pos
            self._pan_start_pos = event.position().toPoint()
            
            # Scroll scrollbars
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self._pan_active:
            self._pan_active = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)
