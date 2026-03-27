from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

class VectorItem(QGraphicsItem):
    """Базовый класс для всех векторных объектов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Базовые свойства
        self.stroke_color = QColor(0, 0, 0)  # Черный
        self.fill_color = QColor(255, 255, 255, 0)  # Прозрачный
        self.stroke_width = 1.0
        
        # Флаги интерактивности
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Метаданные
        self.name = "Vector Item"

    def set_clip_path(self, clip_path):
        self._clip_path = clip_path
        self.update()
    
    def get_clip_path(self):
        return self._clip_path

    clip_path = property(get_clip_path, set_clip_path)

    def boundingRect(self):
        """Должен быть переопределен в дочерних классах"""
        return QRectF()
    
    def paint(self, painter, option, widget=None):
        """Базовая отрисовка - настраивает перо и кисть"""
        # Настройка пера (контур)
        pen = QPen(self.stroke_color, self.stroke_width)
        if (self.isSelected()):
            pen.setColor(QColor(0, 100, 255))  # Синий контур
            pen.setWidth(int(self.stroke_width + 2))  # Чуть толще
        

        pen.setCosmetic(True)  # Толщина не зависит от масштаба
        painter.setPen(pen)
        
            
        # Настройка кисти (заливка)
        brush = QBrush(self.fill_color)
        painter.setBrush(brush)
        
    def itemChange(self, change, value):
        """Обработка изменений объекта"""
        if change == QGraphicsItem.ItemPositionChange:
            # Позиция изменилась
            pass
        return super().itemChange(change, value)