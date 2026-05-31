# vector_editor/items/clip_path_item.py

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath

class ClipPathItem(QGraphicsItem):
    """Обтравочный контур — сам не рисуется, но обрезает целевые объекты"""
    
    def __init__(self, path=None, parent=None):
        super().__init__(parent)
        self.path = path if path else QPainterPath()
        self.targets = []  # объекты, которые этим обрезаются
        self.name = "ClipPath"
        
        # Не выделяется и не перемещается
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
    
    def boundingRect(self):
        return self.path.boundingRect()
    
    def paint(self, painter, option, widget=None):
        # ClipPath сам не рисуется
        # Но при выделении можно показать пунктирный контур
        if self.isSelected():
            painter.save()
            pen = QPen(QColor(0, 150, 255), 1)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawPath(self.path)
            painter.restore()
    
    def set_path(self, path):
        self.path = path
        self.update()
        for target in self.targets:
            target.update()
    
    def add_target(self, item):
        if item not in self.targets:
            self.targets.append(item)
            item.set_clip_path(self)
    
    def remove_target(self, item):
        if item in self.targets:
            self.targets.remove(item)
            if item.clip_path == self:
                item.set_clip_path(None)