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
