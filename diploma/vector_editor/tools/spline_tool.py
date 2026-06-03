from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor
from ..items.spline_item import SplineItem
from .tool_base import Tool

class SplineTool(Tool):
    """Инструмент создания сплайн-кривой"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Spline Tool"
        self.points = []
        self.current_spline = None
        self.scene = None
        self.drawing = False
    
    def activate(self):
        if hasattr(self.document, 'parent'):
            self.scene = self.document.parent()
    
    def mouse_pressed(self, pos: QPointF, modifiers):
        if not self.drawing:
            # Начинаем новую сплайн-кривую
            self.points = [pos]
            self.current_spline = SplineItem(self.points, tension=0.5)
            self.current_spline.stroke_color = QColor(0, 0, 255)  # Синий во время рисования
            self.current_spline.stroke_width = 2.0
            if self.scene:
                self.scene.add_preview_item(self.current_spline)
            self.drawing = True
        else:
            # Добавляем новую опорную точку сплайна
            self.points.append(pos)
            self.current_spline.set_points(self.points)
            self.current_spline.update()
    
    def mouse_moved(self, pos: QPointF, modifiers):
        if self.drawing and self.current_spline and len(self.points) > 0:
            # Временное пролонгирование сплайна до курсора
            preview_points = self.points + [pos]
            self.current_spline.set_points(preview_points)
            self.current_spline.update()
    
    def mouse_released(self, pos: QPointF, modifiers):
        pass  # Завершение по нажатию Enter / клавиши
        
    def key_pressed(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.finish_spline()
        elif event.key() == Qt.Key_Escape:
            self.cancel_spline()
            
    def finish_spline(self):
        """Завершить сплайн и добавить на активный слой"""
        if self.drawing and len(self.points) >= 2:
            if self.scene:
                self.scene.remove_preview_item(self.current_spline)
                
            final_spline = SplineItem(self.points, tension=0.5)
            final_spline.stroke_color = QColor(0, 50, 180)  # Тёмно-синий/голубой дефолтный цвет
            final_spline.stroke_width = 2.0
            self.document.add_item_to_active_layer(final_spline)
            
            # Сразу выделяем его
            self.document.select_item(final_spline, add_to_selection=False)
            
        self.reset()
        
    def cancel_spline(self):
        """Отменить построение сплайны"""
        if self.drawing and self.scene and self.current_spline:
            self.scene.remove_preview_item(self.current_spline)
        self.reset()
        
    def reset(self):
        self.points = []
        self.current_spline = None
        self.drawing = False