# vector_editor/items/line_item.py

from PyQt5.QtCore import QLineF, QRectF, QPointF
from PyQt5.QtGui import QPainterPath
from .base_item import VectorItem

class LineItem(VectorItem):
    """Линия"""
    
    def __init__(self, start=QPointF(0, 0), end=QPointF(100, 100), parent=None):
        super().__init__(parent)
        self.start = start
        self.end = end
        self.name = "Line"
    
    def boundingRect(self):
        margin = self.stroke_width / 2
        return QRectF(self.start, self.end).normalized().adjusted(-margin, -margin, margin, margin)
    
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.drawLine(self.start, self.end)
    
    def shape(self):
        path = QPainterPath()
        path.moveTo(self.start)
        path.lineTo(self.end)
        return path