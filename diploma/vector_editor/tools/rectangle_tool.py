from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor
from ..items import RectangleItem
from .tool_base import Tool

class RectangleTool(Tool):
    """Инструмент создания прямоугольников"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Rectangle Tool"
        self.start_pos = None
        self.current_rect = None
        
    def mouse_pressed(self, pos: QPointF, modifiers):
        """Начало создания прямоугольника"""
        self.start_pos = pos
        
        # Создаем временный прямоугольник
        self.current_rect = RectangleItem(QRectF(pos.x(), pos.y(), 0, 0))
        self.current_rect.stroke_color = QColor(0, 0, 255)  # Синий для предпросмотра
        self.document.add_preview_item(self.current_rect)
        
    def mouse_moved(self, pos: QPointF, modifiers):
        """Изменение размера прямоугольника"""
        if self.start_pos and self.current_rect:
            # Обновляем размер прямоугольника
            rect = QRectF(self.start_pos, pos).normalized()
            self.current_rect.rect = rect
            self.current_rect.update()
            # Обновляем отображение (временный объект должен быть добавлен на сцену)
            # Для простоты пока не реализуем предпросмотр
            
    def mouse_released(self, pos: QPointF, modifiers):
        """Завершение создания прямоугольника"""
        if self.start_pos and self.current_rect:
            self.document.remove_preview_item(self.current_rect)
            # Создаем финальный прямоугольник
            rect = QRectF(self.start_pos, pos).normalized()
            
            # Не создаем слишком маленькие прямоугольники
            if rect.width() > 5 and rect.height() > 5:
                final_rect = RectangleItem(rect)
                final_rect.stroke_color = QColor(0, 0, 0)  # Черный
                self.document.add_item_to_active_layer(final_rect)
                
            self.current_rect = None
            self.start_pos = None