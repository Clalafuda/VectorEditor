# vector_editor/items/layer_item.py

from PyQt5.QtWidgets import QGraphicsItemGroup,QGraphicsItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush

class LayerItem(QGraphicsItemGroup):
    """Слой — специальная группа с видимостью и блокировкой"""
    
    def __init__(self, name="Слой", parent=None):
        super().__init__(parent)
        self.name = name
        self.visible = True
        self.locked = False
        
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
    
    def set_visible(self, visible):
        """Установить видимость слоя"""
        self.visible = visible
        for child in self.childItems():
            child.setVisible(visible)
    
    def set_locked(self, locked):
        """Установить блокировку слоя"""
        self.locked = locked
        for child in self.childItems():
            child.setFlag(QGraphicsItem.ItemIsSelectable, not locked)
            child.setFlag(QGraphicsItem.ItemIsMovable, not locked)
    
    def add_item(self, item):
        """Добавить объект в слой"""
        item.setParentItem(self)
        item.setVisible(self.visible)
        if self.locked:
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemIsMovable, False)
    
    def remove_item(self, item):
        """Удалить объект из слоя"""
        item.setParentItem(None)
    
    def paint(self, painter, option, widget=None):
        # Слой не рисуется
        pass