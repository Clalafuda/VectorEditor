from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QKeyEvent

class Tool:
    """Базовый класс для всех инструментов"""
    
    def __init__(self, document):
        self.document = document
        self.name = "Base Tool"
        
    def mouse_pressed(self, pos: QPointF, modifiers):
        """Обработка нажатия мыши"""
        pass
        
    def mouse_moved(self, pos: QPointF, modifiers):
        """Обработка движения мыши"""
        pass
        
    def mouse_released(self, pos: QPointF, modifiers):
        """Обработка отпускания мыши"""
        pass
        
    def key_pressed(self, event: QKeyEvent):
        """Обработка нажатия клавиш"""
        pass
        
    def activate(self):
        """Активация инструмента"""
        pass
        
    def deactivate(self):
        """Деактивация инструмента"""
        pass
    