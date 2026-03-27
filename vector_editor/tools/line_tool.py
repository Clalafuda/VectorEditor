from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor
from ..items.line_item import LineItem
from .tool_base import Tool

class LineTool(Tool):
    def __init__(self, document):
        super().__init__(document)
        self.name = "Line Tool"
        self.start_pos = None
        self.current_line = None
        self.scene = None
    
    def activate(self):
        if hasattr(self.document, 'parent'):
            self.scene = self.document.parent()
    
    def mouse_pressed(self, pos: QPointF, modifiers):
        self.start_pos = pos
        self.current_line = LineItem(pos, pos)
        self.current_line.stroke_color = QColor(0, 0, 255)
        if self.scene:
            self.scene.add_preview_item(self.current_line)
    
    def mouse_moved(self, pos: QPointF, modifiers):
        if self.start_pos and self.current_line:
            self.current_line.end = pos
            self.current_line.update()
    
    def mouse_released(self, pos: QPointF, modifiers):
        if self.start_pos and self.current_line:
            if self.scene:
                self.scene.remove_preview_item(self.current_line)
            
            if self.start_pos != pos:
                final_line = LineItem(self.start_pos, pos)
                final_line.stroke_color = QColor(0, 0, 0)
                self.document.add_item_to_active_layer(final_line)
            
            self.current_line = None
            self.start_pos = None