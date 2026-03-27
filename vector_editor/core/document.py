from PyQt5.QtCore import QObject, pyqtSignal,QPointF
from PyQt5.QtWidgets import QUndoStack
from .commands import GroupItemsCommand,UngroupItemsCommand
from ..items.group_item import GroupItem
class Document(QObject):
    """Модель документа - хранит все объекты"""
    
    items_changed = pyqtSignal()
    item_added=pyqtSignal(object)
    item_removed=pyqtSignal(object)
    selection_changed = pyqtSignal()
    preview_added=pyqtSignal(object)
    preview_removed=pyqtSignal(object)
    preview_clear=pyqtSignal()
    request_item_at = pyqtSignal(QPointF)
    item_at_found = pyqtSignal(object)

    layers_changed = pyqtSignal()

    rubber_band_start = pyqtSignal(QPointF)      # начать рамку
    rubber_band_update = pyqtSignal(QPointF)     # обновить размер
    rubber_band_finish = pyqtSignal(QPointF, int)


    def __init__(self):
        super().__init__()
        self.items = []  # Все объекты на сцене
        self.selected_items = []  # Выделенные объекты
        self.filename = None
        self.modified = False

        self.layers = []  
        self.active_layer = None
        self.add_layer("Слой 1")

        self.undo_stack=QUndoStack()
        self.undo_stack.setUndoLimit(50)
    
    def add_layer(self, name="Слой"):
        """Создать новый слой"""
        from ..items.layer_item import LayerItem
        layer = LayerItem(name)
        self.layers.append(layer)
        self._add_item(layer)
        self.reorder_layers()
        if self.active_layer is None:
            self.active_layer = layer
        return layer
    
    def reorder_layers(self):
        """Обновить z-order слоёв на сцене"""
        # Слои в списке идут сверху вниз (последний — верхний)
        for i, layer in enumerate(self.layers):
            # Устанавливаем z-value
            layer.setZValue(i)

    def remove_layer(self, layer):
        """Удалить слой (объекты перемещаются в активный слой)"""
        if layer in self.layers:
            # Перемещаем объекты в активный слой
            for child in layer.childItems():
                if self.active_layer:
                    self.active_layer.add_item(child)
                else:
                    child.setParentItem(None)
            self.layers.remove(layer)
            self._remove_item(layer)

    def set_active_layer(self, layer):
        """Установить активный слой"""
        if layer in self.layers:
            self.active_layer = layer

    def add_item_to_active_layer(self, item):
        """Добавить объект в активный слой"""
        if self.active_layer:
            self.active_layer.add_item(item)
        elif self.layers:
            self.layers[0].add_item(item)
        else:
            layer=self.add_layer("Слой 1")
            layer.add_item(item)
        self.add_item(item)
    
    def push_command(self,command):
        """"Добавить команду в стек"""
        self.undo_stack.push(command)
    def undo(self):
        """"Отменить последнее действие"""
        if self.undo_stack.canUndo():
            self.undo_stack.undo()
    def redo(self):
        """"Повторить отменённое действие"""
        if self.undo_stack.canRedo():
            self.undo_stack.redo()
    def clear_undo_stack(self):
        """"Очистить стек"""
        self.undo_stack.clear()
    def _add_item(self,item):
        """"Внутреннее добавление (без команды)"""
        print(f"_add_item: emitting item_added for {item}")
        self.items.append(item)
        self.modified=True
        #self.items_changed.emit()
        if item.parentItem() is None:
            self.item_added.emit(item)
        self.layers_changed.emit()
    def _remove_item(self,item,No_scene_change=False):
        """"Внутреннее удаление (без команды)"""
        print(f"_remove_item: emitting item_removed for {item}")
        if item in self.items:
            
            self.items.remove(item)
            # if item.parentItem() is None:
            if not No_scene_change:
                self.item_removed.emit(item)
            #self.items_changed.emit()
            if item in self.selected_items:
                self.selected_items.remove(item)
                self.modified=True
                self.selection_changed.emit()
            self.layers_changed.emit()
        
    def add_item(self, item,create_command=True):
        """Добавление объекта в документ"""
        if create_command:
            from .commands import AddItemCommand
            cmd=AddItemCommand(self,item)
            self.undo_stack.push(cmd)
        else:    
            self._add_item(item)

    def add_preview_item(self,item):
        self.preview_added.emit(item)
    def remove_preview_item(self,item):
        self.preview_removed.emit(item)

    def remove_item(self, item, create_command=True):
        """Удаление объекта из документа"""
        if create_command:
            from .commands import RemoveItemCommand
            cmd=RemoveItemCommand(self, item)
            self.undo_stack.push(cmd)
        else:
            self._remove_item(item)
            
    def clear(self):
        """Очистка документа"""
        self.items.clear()
        self.selected_items.clear()
        self.preivew_clear.emit()
        self.modified = False
        self.filename = None
        self.items_changed.emit()
        self.selection_changed.emit()
        self.clear_undo_stack()
        
    def select_item(self, item, add_to_selection=False):
        """Выделение объекта"""
        if not add_to_selection:
            self.clear_selection()
        
        if item and item not in self.selected_items:
            self.selected_items.append(item)
            item.setSelected(True)
            self.selection_changed.emit()
            
    def unselect_item(self, item):
        """Снятие выделения"""
        if item and item in self.selected_items:
            self.selected_items.remove(item)
            item.setSelected(False)
            self.selection_changed.emit()

    def clear_selection(self):
        """Снятие выделения"""
        for item in self.selected_items:
            item.setSelected(False)
        self.selected_items.clear()
        self.selection_changed.emit()

    def group_items(self, items):
        """Сгруппировать объекты"""
        if len(items) >= 2:
            cmd = GroupItemsCommand(self, items)
            self.push_command(cmd)

    def ungroup_items(self, group):
        """Разгруппировать объект"""
        if isinstance(group, GroupItem):
            cmd = UngroupItemsCommand(self, group)
            self.push_command(cmd)
    
