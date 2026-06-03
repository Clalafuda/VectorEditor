from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor
from ..items.function_item import FunctionItem
from .tool_base import Tool

class FunctionTool(Tool):
    """Инструмент создания математических графиков (функций)"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Function Tool"
        self.start_pos = None
        self.current_item = None
        
    def mouse_pressed(self, pos: QPointF, modifiers):
        """Начало создания области для графика"""
        self.start_pos = pos
        
        # Создаем временную функцию для предпросмотра
        self.current_item = FunctionItem(QRectF(pos.x(), pos.y(), 0, 0), "x^2 + y^2 = 25")
        self.current_item.stroke_color = QColor(0, 0, 255)  # Синий во время перетаскивания
        self.document.add_preview_item(self.current_item)
        
    def mouse_moved(self, pos: QPointF, modifiers):
        """Изменение размера области графика"""
        if self.start_pos and self.current_item:
            rect = QRectF(self.start_pos, pos).normalized()
            self.current_item.rect = rect
            self.current_item.update()
            
    def mouse_released(self, pos: QPointF, modifiers):
        """Завершение создания графика"""
        if self.start_pos and self.current_item:
            self.document.remove_preview_item(self.current_item)
            rect = QRectF(self.start_pos, pos).normalized()
            
            # Избегаем создания микроскопических графиков
            if rect.width() > 10 and rect.height() > 10:
                final_item = FunctionItem(rect, "x^2 + y^2 = 25")
                final_item.stroke_color = QColor(100, 50, 200)  # Приятный фиолетовый по дефолту
                final_item.stroke_width = 2.0
                self.document.add_item_to_active_layer(final_item)
                
                # Сразу выделяем созданный график, чтобы пользователь мог писать уравнение
                self.document.select_item(final_item, add_to_selection=False)
                
            self.current_item = None
            self.start_pos = None