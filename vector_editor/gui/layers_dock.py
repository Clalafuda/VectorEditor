from PyQt5.QtWidgets import (QDockWidget, QTreeWidget, QTreeWidgetItem,
                             QMenu, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ..items.layer_item import LayerItem
class LayersDock(QDockWidget):
    def __init__(self, document, parent=None):
        super().__init__("Слои", parent)
        self.document = document
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.on_context_menu)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.setWidget(self.tree)
        
        # Подписка на изменения
        document.layers_changed.connect(self.update_tree)
        document.item_added.connect(self.on_item_added)
        document.item_removed.connect(self.on_item_removed)
        document.selection_changed.connect(self.update_selection)

        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QTreeWidget.DragOnly)
        
        self.update_tree()
    
    def update_tree(self):
        """Обновить дерево слоёв"""
        # self.tree.clear()
        
        # for layer in self.document.layers:
        #     layer_item = QTreeWidgetItem([layer.name])
        #     layer_item.setData(0, Qt.UserRole, layer)
        #     layer_item.setIcon(0, QIcon.fromTheme("layer"))
            
        #     # Чекбокс видимости
        #     layer_item.setFlags(layer_item.flags() | Qt.ItemIsUserCheckable)
        #     layer_item.setCheckState(0, Qt.Checked if layer.visible else Qt.Unchecked)
            
        #     # Добавляем объекты слоя
        #     for child in layer.childItems():
        #         if hasattr(child, 'name'):
        #             child_item = QTreeWidgetItem([child.name])
        #             child_item.setData(0, Qt.UserRole, child)
        #             child_item.setIcon(0, QIcon.fromTheme("shape"))
        #             layer_item.addChild(child_item)
            
        #     self.tree.addTopLevelItem(layer_item)
        self.tree.clear()
    
        for i, layer in enumerate(self.document.layers):
            layer_item = QTreeWidgetItem([layer.name])
            layer_item.setData(0, Qt.UserRole, i)  # ← храним индекс
            layer_item.setIcon(0, QIcon.fromTheme("layer"))
            
            # Чекбокс видимости
            layer_item.setFlags(layer_item.flags() | Qt.ItemIsUserCheckable)
            layer_item.setCheckState(0, Qt.Checked if layer.visible else Qt.Unchecked)
            
            # Жирный шрифт для активного слоя
            if layer == self.document.active_layer:
                font = layer_item.font(0)
                font.setBold(True)
                layer_item.setFont(0, font)
            
            # Дочерние объекты
            for child in layer.childItems():
                if hasattr(child, 'name'):
                    child_item = QTreeWidgetItem([child.name])
                    child_item.setData(0, Qt.UserRole, id(child))  # храним id объекта
                    child_item.setIcon(0, QIcon.fromTheme("shape"))
                    layer_item.addChild(child_item)
            
            self.tree.addTopLevelItem(layer_item)
    
    def on_item_added(self, item):
        """При добавлении объекта — обновить дерево"""
        self.update_tree()
    
    def on_item_removed(self, item):
        """При удалении объекта — обновить дерево"""
        self.update_tree()
    
    def update_selection(self):
        """Подсветить выделенные объекты в дереве"""
        # Обходим все элементы и подсвечиваем выделенные
        pass
    
    def on_item_clicked(self, item, column):
        """Клик по элементу"""
        # obj = item.data(0, Qt.UserRole)
        # if isinstance(obj, LayerItem):
        #     # Устанавливаем активный слой
        #     self.document.set_active_layer(obj)
        #     print(f"Active layer set to: {obj.name}")  # для отладки
        #     # Если клик на чекбокс видимости
        #     if item.flags() & Qt.ItemIsUserCheckable:
        #         if isinstance(obj, LayerItem):
        #             visible = item.checkState(0) == Qt.Checked
        #             obj.set_visible(visible)
        
        # # Выделение объекта
        # if hasattr(obj, 'setSelected'):
        #     self.document.clear_selection()
        #     obj.setSelected(True)
        data = item.data(0, Qt.UserRole)
    
        if isinstance(data, int):
            if 0 <= data < len(self.document.layers):
                layer = self.document.layers[data]
                
                self.document.set_active_layer(layer)
                
                if item.flags() & Qt.ItemIsUserCheckable:
                    visible = item.checkState(0) == Qt.Checked
                    layer.set_visible(visible)
                
                self.update_tree()  
        
        elif isinstance(data, int):
            for layer in self.document.layers:
                for child in layer.childItems():
                    if id(child) == data:
                        self.document.clear_selection()
                        child.setSelected(True)
                        return
    
    def on_item_double_clicked(self, item, column):
        """Двойной клик — переименование"""
        obj = item.data(0, Qt.UserRole)
        new_name, ok = QInputDialog.getText(self, "Переименовать", "Новое имя:", text=item.text(0))
        if ok and new_name:
            item.setText(0, new_name)
            if hasattr(obj, 'name'):
                obj.name = new_name
    
    def on_context_menu(self, position):
        """Контекстное меню"""
        # menu = QMenu()
        # menu.addAction("Создать слой", self.add_layer)
        # menu.addAction("Удалить слой", self.delete_layer)
        # menu.exec_(self.tree.viewport().mapToGlobal(position))
        print("on_context_menu called at", position)
        current = self.tree.currentItem()
        if not current:
            return
        
        obj = current.data(0, Qt.UserRole)
        menu = QMenu()
        
        # Для слоя
        if isinstance(obj, LayerItem):
            menu.addAction("Создать слой", self.add_layer)
            menu.addAction("Удалить слой", self.delete_layer)
            menu.addAction("Переименовать", lambda: self.on_item_double_clicked(current, 0))
        
        # Для обычного объекта
        elif hasattr(obj, 'name'):
            menu.addAction("Удалить", lambda: self.delete_object(obj))
            menu.addAction("Переименовать", lambda: self.on_item_double_clicked(current, 0))
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    def delete_object(self, obj):
        """Удалить объект"""
        # Спрашиваем подтверждение
        reply = QMessageBox.question(self, "Удалить объект",
            f"Удалить '{getattr(obj, 'name', 'объект')}'?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.document.remove_item(obj)

    def add_layer(self):
        """Создать новый слой"""
        name, ok = QInputDialog.getText(self, "Новый слой", "Имя слоя:")
        if ok and name:
            self.document.add_layer(name)
            self.update_tree()
    
    def delete_layer(self):
        """Удалить текущий слой"""
        current = self.tree.currentItem()
        if current:
            layer = current.data(0, Qt.UserRole)
            if isinstance(layer, LayerItem):
                reply = QMessageBox.question(self, "Удалить слой",
                    f"Удалить слой '{layer.name}'? Объекты будут перемещены в активный слой.",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.document.remove_layer(layer)
                    self.update_tree()
    
    def dragMoveEvent(self, event):
        """Разрешаем перемещение только над слоями"""
        target = self.tree.itemAt(event.pos())
        if target and isinstance(target.data(0, Qt.UserRole), LayerItem):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Обработка перемещения слоёв"""
        # # Получаем перемещаемый элемент
        # dragged = self.tree.currentItem()
        # if not dragged:
        #     event.ignore()
        #     return
        
        # # Получаем целевой элемент
        # target = self.tree.itemAt(event.pos())
        # if not target:
        #     event.ignore()
        #     return
        
        # # Получаем объекты
        # dragged_layer = dragged.data(0, Qt.UserRole)
        # target_layer = target.data(0, Qt.UserRole)
        
        # # Проверяем, что оба — слои
        # if not isinstance(dragged_layer, LayerItem) or not isinstance(target_layer, LayerItem):
        #     event.ignore()
        #     return
        
        # # Находим индексы
        # if dragged_layer in self.document.layers and target_layer in self.document.layers:
        #     old_index = self.document.layers.index(dragged_layer)
        #     new_index = self.document.layers.index(target_layer)
            
        #     # Перемещаем в списке
        #     self.document.layers.pop(old_index)
        #     self.document.layers.insert(new_index, dragged_layer)
            
        #     # Обновляем порядок на сцене
        #     self.document.reorder_layers()
            
        #     # Обновляем дерево
        #     self.update_tree()
        
        # event.accept()
        current = self.tree.currentItem()
        if not current:
            event.ignore()
            return
        
        # Получаем целевой элемент
        target = self.tree.itemAt(event.pos())
        if not target:
            event.ignore()
            return
        
        # Получаем индексы
        dragged_data = current.data(0, Qt.UserRole)
        target_data = target.data(0, Qt.UserRole)
        
        # Проверяем, что оба — слои (индексы)
        if (isinstance(dragged_data, int) and isinstance(target_data, int) and
            0 <= dragged_data < len(self.document.layers) and
            0 <= target_data < len(self.document.layers)):
            
            old_index = dragged_data
            new_index = target_data
            
            # Перемещаем в списке
            layer = self.document.layers.pop(old_index)
            self.document.layers.insert(new_index, layer)
            
            # Обновляем порядок на сцене
            self.document.reorder_layers()
            
            # Обновляем дерево
            self.update_tree()
            
            event.accept()
        else:
            event.ignore()