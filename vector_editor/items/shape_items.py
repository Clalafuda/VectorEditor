from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainterPath
from .base_item import VectorItem

class RectangleItem(VectorItem):
    """Прямоугольник"""
    
    def __init__(self, rect=QRectF(0, 0, 100, 100), parent=None):
        super().__init__(parent)
        self.rect = rect
        self.name = "Rectangle"
        
    def boundingRect(self):
        """Границы объекта"""
        margin = self.stroke_width / 2
        return self.rect.adjusted(-margin, -margin, margin, margin)
    
    def paint(self, painter, option, widget=None):
        """Отрисовка прямоугольника"""
        super().paint(painter, option, widget)
        painter.drawRect(self.rect)
        
    def shape(self):
        """Форма для обнаружения столкновений"""
        path = QPainterPath()
        path.addRect(self.rect)
        return path


class EllipseItem(VectorItem):
    """Эллипс"""
    
    def __init__(self, rect=QRectF(0, 0, 100, 100), parent=None):
        super().__init__(parent)
        self.rect = rect
        self.name = "Ellipse"
        
    def boundingRect(self):
        """Границы объекта"""
        margin = self.stroke_width / 2
        return self.rect.adjusted(-margin, -margin, margin, margin)
    
    def paint(self, painter, option, widget=None):
        """Отрисовка эллипса"""
        super().paint(painter, option, widget)
        painter.drawEllipse(self.rect)
        
    def shape(self):
        """Форма для обнаружения столкновений"""
        path = QPainterPath()
        path.addEllipse(self.rect)
        return path