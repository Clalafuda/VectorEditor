from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor
from ..items.polyline_item import PolylineItem
from .tool_base import Tool

class PolylineTool(Tool):
    """Инструмент создания ломаной линии"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Polyline Tool"
        self.points = []
        self.current_polyline = None
        self.scene = None
        self.drawing = False
    
    def activate(self):
        if hasattr(self.document, 'parent'):
            self.scene = self.document.parent()
    
    def mouse_pressed(self, pos: QPointF, modifiers):
        if not self.drawing:
            # Начинаем новую ломаную
            self.points = [pos]
            self.current_polyline = PolylineItem(self.points)
            self.current_polyline.stroke_color = QColor(0, 0, 255)
            if self.scene:
                self.scene.add_preview_item(self.current_polyline)
            self.drawing = True
        else:
            # Добавляем точку
            self.points.append(pos)
            self.current_polyline.set_points(self.points)
            self.current_polyline.update()
    
    def mouse_moved(self, pos: QPointF, modifiers):
        if self.drawing and self.current_polyline and len(self.points) > 0:
            # Временная линия от последней точки к курсору
            preview_points = self.points + [pos]
            self.current_polyline.set_points(preview_points)
            self.current_polyline.update()
    
    def mouse_released(self, pos: QPointF, modifiers):
        pass  # Завершаем по двойному клику или Enter
    
    def key_pressed(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.finish_polyline()
        elif event.key() == Qt.Key_Escape:
            self.cancel_polyline()
    
    def finish_polyline(self):
        """Завершить создание ломаной"""
        if self.drawing and len(self.points) >= 2:
            if self.scene:
                self.scene.remove_preview_item(self.current_polyline)
            
            final_polyline = PolylineItem(self.points)
            final_polyline.stroke_color = QColor(0, 0, 0)
            self.document.add_item_to_active_layer(final_polyline)
        
        self.reset()
    
    def cancel_polyline(self):
        """Отменить создание ломаной"""
        if self.drawing and self.scene and self.current_polyline:
            self.scene.remove_preview_item(self.current_polyline)
        self.reset()
    
    def reset(self):
        self.points = []
        self.current_polyline = None
        self.drawing = False