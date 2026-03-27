from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QMouseEvent, QPainter

class SceneView(QGraphicsView):
    """Представление для отображения сцены"""
    
    def __init__(self, scene, tool_manager, parent=None):
        super().__init__(scene, parent)
        self.tool_manager = tool_manager
        self.document = scene.document
        
        # Настройки представления
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Масштаб
        self.scale_factor = 1.0
        self.zoom_speed = 1.2
        
    def wheelEvent(self, event):
        """Масштабирование колесиком мыши"""
        zoom_in = event.angleDelta().y() > 0
        
        if zoom_in:
            factor = self.zoom_speed
        else:
            factor = 1 / self.zoom_speed
            
        new_scale = self.scale_factor * factor
        
        # Ограничение масштаба
        if 0.1 <= new_scale <= 10:
            self.scale(factor, factor)
            self.scale_factor = new_scale
            
    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши"""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.tool_manager.mouse_pressed(scene_pos, event.modifiers())

        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка движения мыши"""
        scene_pos = self.mapToScene(event.pos())
        self.tool_manager.mouse_moved(scene_pos, event.modifiers())

        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обработка отпускания мыши"""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.tool_manager.mouse_released(scene_pos, event.modifiers())
        
    def keyPressEvent(self, event):
        """Обработка нажатия клавиш"""
        self.tool_manager.key_pressed(event)
        super().keyPressEvent(event)