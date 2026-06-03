from PyQt5.QtWidgets import QGraphicsScene, QRubberBand
from PyQt5.QtCore import Qt, QRectF,QPointF,QRect
from PyQt5.QtGui import QPen, QColor, QPainter

class Scene(QGraphicsScene):
    """Сцена для отображения векторных объектов"""
    
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self.setSceneRect(0, 0, 800, 600)
        self.preview_items = []
        self.show_grid = True
        
        # Подключение сигналов документа
        #document.items_changed.connect(self.update_scene)
        document.item_removed.connect(self.on_item_removed)
        document.item_added.connect(self.on_item_added)
        document.selection_changed.connect(self.update_selection)
        document.preview_added.connect(self.add_preview_item)
        document.preview_removed.connect(self.remove_preview_item)
        document.preview_clear.connect(self.clear_preview)
        document.request_item_at.connect(self.on_request_item_at)
        
        document.rubber_band_start.connect(self.on_rubber_band_start)
        document.rubber_band_update.connect(self.on_rubber_band_update)
        document.rubber_band_finish.connect(self.on_rubber_band_finish)

        self.view=None
        # Устанавливаем ссылку на сцену в документе (для инструментов)
        document.parent = lambda: self
        
        
        self.update_scene()
    def set_view(self,view):
        self.view=view
    def on_rubber_band_start(self,pos):
        """Начало резиновой рамки"""
        self.rubber_band_start = pos
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.view)
        
        view_pos = self.view.mapFromScene(pos)
        self.rubber_band.setGeometry(QRect(view_pos, view_pos))
        self.rubber_band.show()
    def on_rubber_band_update(self, pos):
        """Обновление размера рамки"""
        if self.rubber_band and self.rubber_band_start:
            rect = QRectF(self.rubber_band_start, pos).normalized()

            top_left_view = self.view.mapFromScene(rect.topLeft())
            bottom_right_view = self.view.mapFromScene(rect.bottomRight())
            
            view_rect = QRect(top_left_view, bottom_right_view)
            self.rubber_band.setGeometry(view_rect)

    def on_rubber_band_finish(self, pos, modifiers):
        """Завершение рамки — выделение объектов"""
        if self.rubber_band and self.rubber_band_start:
            rect = QRectF(self.rubber_band_start, pos).normalized()
            items = self.items(rect)
            if not modifiers & Qt.ControlModifier:
                self.document.clear_selection()
            for item in items:
                if hasattr(item, 'name'):
                    self.document.select_item(item, add_to_selection=True)
            
            self.rubber_band.deleteLater()
            self.rubber_band = None
            self.rubber_band_start = None
    def on_item_added(self, item):
        """Добавление одного объекта"""
        print(f"Scene.on_item_added: {item}, id={id(item)}")
        print(f"Scene: adding {item}")  # для отладки
        if item.parentItem() is None: # Only add top-level items to the scene
            self.addItem(item)

    def on_item_removed(self, item):
        """Удаление одного объекта"""
        print(f"Scene: removing {item}")  # для отладки
        self.removeItem(item)

    def on_items_cleared(self):
        """Очистка всей сцены"""
        self.clear()

    def update_scene(self):
        """Обновление сцены из документа"""
        """Обновление сцены из документа"""
        # Очищаем только постоянные элементы, но сохраняем временные
        for item in self.items():
            if item not in self.preview_items:
                self.removeItem(item)

        # Добавляем все постоянные элементы из документа
        for item in self.document.items:
            if item not in self.items():
                self.addItem(item)
    def on_request_items_in_rect(self,rect):
        items=self.items(rect)
        result=[item for item in items if hasattr(item,'name')]
        self.document.items_in_rect_found.emit(result)
    def update_selection(self):
        """Обновление выделения"""
        # Снимаем выделение со всех объектов
        for item in self.items():
            item.setSelected(False)
            
        # Выделяем выбранные объекты
        for item in self.document.selected_items:
            item.setSelected(True)
    def add_preview_item(self, item):
        """Добавление временного элемента для предпросмотра"""
        self.preview_items.append(item)
        self.addItem(item)

    def remove_preview_item(self, item):
        """Удаление временного элемента"""
        if item in self.preview_items:
            self.preview_items.remove(item)
            self.removeItem(item)
    def clear_preview(self):
        """"Очистка превью"""
        self.preview_items=[]
    def on_request_item_at(self,pos: QPointF):
        items=self.items(pos)
        for item in items:
            if hasattr(item,'name'):
                self.document.item_at_found.emit(item)
        self.document.item_at_found.emit(None)

    def drawBackground(self, painter, rect):
        """Отрисовка фона (сетка)"""
        super().drawBackground(painter, rect)
        
        if not getattr(self, 'show_grid', True):
            return
            
        # Рисуем сетку
        pen = QPen(QColor(200, 200, 200), 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        
        # Преобразуем float в int для рисования линий
        left = int(rect.left()) - (int(rect.left()) % 20)
        top = int(rect.top()) - (int(rect.top()) % 20)
        right = int(rect.right())
        bottom = int(rect.bottom())
        
        # Вертикальные линии
        x = left
        while x < right:
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += 20
            
        # Горизонтальные линии
        y = top
        while y < bottom:
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += 20