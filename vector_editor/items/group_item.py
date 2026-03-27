from PyQt5.QtWidgets import QGraphicsItemGroup,QGraphicsItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

class GroupItem(QGraphicsItemGroup):
    """Группа объектов"""
    
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.name = "Group"
        
        # Добавляем объекты в группу
        if items:
            for item in items:
                self.addToGroup(item)
        
        # Группа должна быть выделяема и перемещаема
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
    
    def boundingRect(self):
        """Объединённый bounding rect всех объектов в группе"""
        return self.childrenBoundingRect()
    
    def paint(self, painter, option, widget=None):
        # Группа сама не рисуется, рисуются её дети
        # Но нужно показать рамку при выделении
        if self.isSelected():
            painter.save()
            painter.setPen(QPen(QColor(0, 150, 255), 2))
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(self.boundingRect())
            painter.restore()