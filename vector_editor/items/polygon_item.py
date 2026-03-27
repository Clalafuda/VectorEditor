# vector_editor/items/polygon_item.py

from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPainterPath
from .base_item import VectorItem

class PolygonItem(VectorItem):
    """Многоугольник (замкнутый)"""
    
    def __init__(self, points=None, parent=None):
        super().__init__(parent)
        self.points = points if points else []
        self.name = "Polygon"
    
    def boundingRect(self):
        if not self.points:
            return QRectF()
        
        min_x = min(p.x() for p in self.points)
        min_y = min(p.y() for p in self.points)
        max_x = max(p.x() for p in self.points)
        max_y = max(p.y() for p in self.points)
        
        margin = self.stroke_width / 2
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y).adjusted(-margin, -margin, margin, margin)
    
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if len(self.points) < 3:
            return
        
        # Рисуем контур
        for i in range(len(self.points) - 1):
            painter.drawLine(self.points[i], self.points[i + 1])
        painter.drawLine(self.points[-1], self.points[0])
        
        # Рисуем заливку
        if self.fill_color.alpha() > 0 and len(self.points) >= 3:
            painter.setBrush(self.fill_color)
            path = QPainterPath()
            path.moveTo(self.points[0])
            for p in self.points[1:]:
                path.lineTo(p)
            path.closeSubpath()
            painter.fillPath(path, self.fill_color)
    
    def shape(self):
        path = QPainterPath()
        if self.points:
            path.moveTo(self.points[0])
            for p in self.points[1:]:
                path.lineTo(p)
            path.closeSubpath()
        return path
    
    def add_point(self, point):
        self.points.append(point)
        self.update()
    
    def set_points(self, points):
        self.points = points
        self.update()