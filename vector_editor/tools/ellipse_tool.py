from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor
from ..items import EllipseItem
from .tool_base import Tool

class EllipseTool(Tool):
    """Инструмент создания эллипсов"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Ellipse Tool"
        self.start_pos = None
        self.current_ellipse = None
    def activate(self):
        if hasattr(self.document, 'parent'):
            self.scene = self.document.parent()
    def mouse_pressed(self, pos: QPointF, modifiers):
        """Начало создания эллипса"""
        self.start_pos = pos
        
        # Создаем временный эллипс
        self.current_ellipse = EllipseItem(QRectF(pos.x(), pos.y(), 0, 0))
        self.current_ellipse.stroke_color = QColor(0, 0, 255)  # Синий для предпросмотра
        self.document.add_preview_item(self.current_ellipse)
    def mouse_moved(self, pos: QPointF, modifiers):
        """Изменение размера эллипса"""
        if self.start_pos and self.current_ellipse:
            # Обновляем размер эллипса
            rect = QRectF(self.start_pos, pos).normalized()
            self.current_ellipse.rect = rect
            self.current_ellipse.update()
            
    def mouse_released(self, pos: QPointF, modifiers):
        """Завершение создания эллипса"""
        if self.start_pos and self.current_ellipse:
            self.document.remove_preview_item(self.current_ellipse)
            # Создаем финальный эллипс
            rect = QRectF(self.start_pos, pos).normalized()
            
            # Не создаем слишком маленькие эллипсы
            if rect.width() > 5 and rect.height() > 5:
                final_ellipse = EllipseItem(rect)
                final_ellipse.stroke_color = QColor(0, 0, 0)  # Черный
                self.document.add_item_to_active_layer(final_ellipse)
                
            self.current_ellipse = None
            self.start_pos = None