from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor
from ..items.polygon_item import PolygonItem
from .tool_base import Tool

class PolygonTool(Tool):
    """Инструмент создания многоугольника"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Polygon Tool"
        self.points = []
        self.current_polygon = None
        self.scene = None
        self.drawing = False
    
    def activate(self):
        if hasattr(self.document, 'parent'):
            self.scene = self.document.parent()
    
    def mouse_pressed(self, pos: QPointF, modifiers):
        if not self.drawing:
            # Начинаем новый многоугольник
            self.points = [pos]
            self.current_polygon = PolygonItem(self.points)
            self.current_polygon.stroke_color = QColor(0, 0, 255)
            if self.scene:
                self.scene.add_preview_item(self.current_polygon)
            self.drawing = True
        else:
            # Добавляем точку
            self.points.append(pos)
            self.current_polygon.set_points(self.points)
            self.current_polygon.update()
    
    def mouse_moved(self, pos: QPointF, modifiers):
        if self.drawing and self.current_polygon and len(self.points) > 0:
            # Временная линия от последней точки к курсору
            preview_points = self.points + [pos]
            self.current_polygon.set_points(preview_points)
            self.current_polygon.update()
    
    def mouse_released(self, pos: QPointF, modifiers):
        pass
    
    def key_pressed(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.finish_polygon()
        elif event.key() == Qt.Key_Escape:
            self.cancel_polygon()
    
    def finish_polygon(self):
        """Завершить создание многоугольника (замкнуть)"""
        if self.drawing and len(self.points) >= 3:
            if self.scene:
                self.scene.remove_preview_item(self.current_polygon)
            
            final_polygon = PolygonItem(self.points)
            final_polygon.stroke_color = QColor(0, 0, 0)
            self.document.add_item_to_active_layer(final_polygon)
        
        self.reset()
    
    def cancel_polygon(self):
        """Отменить создание многоугольника"""
        if self.drawing and self.scene and self.current_polygon:
            self.scene.remove_preview_item(self.current_polygon)
        self.reset()
    
    def reset(self):
        self.points = []
        self.current_polygon = None
        self.drawing = False