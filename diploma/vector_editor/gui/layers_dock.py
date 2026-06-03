from PyQt5.QtWidgets import (QDockWidget, QTreeWidget, QTreeWidgetItem,
                             QMenu, QInputDialog, QMessageBox, QAbstractItemView, QApplication, QGraphicsItem,
                             QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QToolButton) # Added QLabel, QHBoxLayout, QToolButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette
from ..items.layer_item import LayerItem


class LayersDock(QDockWidget):
    def __init__(self, document, parent=None):
        super().__init__("Layers", parent)

        self._document = document
        
        # Create a central widget and layout for the dock
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(["Layers"])
        self.tree_widget.setSelectionMode(QAbstractItemView.ExtendedSelection) # Allow multiple selections
        self.tree_widget.setIndentation(10) # Adjust indentation for better appearance
        
        # Включаем drag and drop в QTreeWidget
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)
        self.tree_widget.setDragDropMode(QAbstractItemView.InternalMove)
        
        # Перегружаем drag parameters и dropEvent
        self.tree_widget.dragEnterEvent = self._tree_dragEnterEvent
        self.tree_widget.dragMoveEvent = self._tree_dragMoveEvent
        self.tree_widget.dropEvent = self._tree_dropEvent
        
        main_layout.addWidget(self.tree_widget) # Add tree widget to the layout
        
        # Create buttons
        add_layer_button = QPushButton("Добавить слой", self)
        
        # Add buttons to the layout
        main_layout.addWidget(add_layer_button)
        
        self.setWidget(central_widget) # Set the central widget for the dock
        
        self.tree_widget.itemChanged.connect(self._on_item_changed)
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._on_context_menu)
        
        # Connect button signals
        add_layer_button.clicked.connect(self._add_layer)
        
        self._populate_layers()

    def _on_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item:
            menu = QMenu(self)
            remove_action = menu.addAction("Remove")
            action = menu.exec_(self.tree_widget.mapToGlobal(position))
            if action == remove_action:
                item_data = item.data(0, Qt.UserRole)
                self._remove_item_from_tree(item_data)

    def _populate_layers(self):
        self.tree_widget.clear()
        for layer in self._document.layers:
            tree_item = self._add_layer_to_tree(layer)
            # Expand the layer item by default
            if tree_item:
                tree_item.setExpanded(True)

    def _add_layer_to_tree(self, layer):
        item = QTreeWidgetItem(self.tree_widget)
        item.setText(0, layer.name) # Set text for editing
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(0, Qt.UserRole, layer)
        self.tree_widget.addTopLevelItem(item)
        
        # The custom widget is removed to allow direct editing of the QTreeWidgetItem text.
        # The QLabel update will happen in _on_item_changed.
        # widget = self._create_item_widget(layer.name, layer)
        # self.tree_widget.setItemWidget(item, 0, widget)
        # item.setForeground(0, QApplication.palette().color(QPalette.Window)) # Hide default text
        
        for child_item in layer.childItems():
            self._add_child_item_to_tree(item, child_item)
        return item

    def _add_child_item_to_tree(self, parent_item, child_item_data):
        item = QTreeWidgetItem(parent_item)
        item.setText(0, child_item_data.name) # Set text for editing
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(0, Qt.UserRole, child_item_data)
        parent_item.addChild(item)

        # The custom widget is removed to allow direct editing of the QTreeWidgetItem text.
        # The QLabel update will happen in _on_item_changed.
        # widget = self._create_item_widget(child_item_data.name, child_item_data)
        # self.tree_widget.setItemWidget(item, 0, widget)
        # item.setForeground(0, QApplication.palette().color(QPalette.Window)) # Hide default text
        return item

    def _on_item_changed(self, item, column):
        # When an item's text is changed via editing in the tree widget
        data = item.data(0, Qt.UserRole)
        if hasattr(data, 'name'):
            old_name = getattr(data, 'name')
            new_name = item.text(column)
            if old_name != new_name:
                from vector_editor.core.commands import ChangePropertyCommand
                cmd = ChangePropertyCommand(data, 'name', old_name, new_name)
                self._document.push_command(cmd)
            else:
                # If the name hasn't actually changed, revert the tree widget item to old name
                # to prevent unnecessary command pushes or visual glitches.
                # This is important because itemChanged is emitted even if text is same.
                item.setText(column, old_name)

    def _add_layer(self):
        name, ok = QInputDialog.getText(self, "Новый слой", "Введите имя слоя:")
        if ok and name:
            self._document.add_layer(name)
            self._populate_layers()

    def _remove_item_from_tree(self, item_data):
        reply = QMessageBox.question(self, 'Удалить', 
                                     f"Вы уверены, что хотите удалить '{item_data.name}'?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if isinstance(item_data, LayerItem):
                self._document.remove_layer(item_data)
            else:
                self._document.remove_item(item_data)
            self._populate_layers() # Refresh the tree after removal

    def _on_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        modifiers = QApplication.keyboardModifiers()
        
        if isinstance(data, LayerItem):
            layer = data
            if layer in self._document.layers:
                self._document.set_active_layer(layer)
                
                if modifiers & Qt.ControlModifier:
                    # Ctrl-click on a layer: toggle selection of its children
                    for doc_item in layer.childItems():
                        if doc_item in self._document.selected_items:
                            self._document.unselect_item(doc_item)
                        else:
                            self._document.select_item(doc_item, add_to_selection=True)
                else:
                    # Single click on a layer: clear selection and select all its children
                    self._document.clear_selection()
                    for doc_item in layer.childItems():
                        self._document.select_item(doc_item, add_to_selection=True)
            else:
                # If the layer is no longer valid, deselect the item and refresh the layers
                self.tree_widget.setCurrentItem(None)
                self._populate_layers() # Refresh the tree to remove stale items
        else: # It's a regular QGraphicsItem
            doc_item = data
            # Also set its parent layer as active
            if hasattr(doc_item, 'parentItem') and isinstance(doc_item.parentItem(), LayerItem):
                self._document.set_active_layer(doc_item.parentItem())

            if modifiers & Qt.ControlModifier:
                # Ctrl-click on an item: toggle its selection
                if doc_item in self._document.selected_items:
                    self._document.unselect_item(doc_item)
                else:
                    self._document.select_item(doc_item, add_to_selection=True)
            else:
                # Single click on an item: clear selection and select only this item
                self._document.clear_selection()
                self._document.select_item(doc_item, add_to_selection=False) # Select only this item

    def _update_layers(self):
        self._populate_layers()

    def _select_item_for_layer(self, layer):
        """Выбирает элемент в дереве, соответствующий заданному слою."""
        self.tree_widget.blockSignals(True) # Block signals to prevent _on_item_selection_changed from being called
        found_item = None
        # Iterate through top-level items
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item.data(0, Qt.UserRole) == layer:
                found_item = item
                break
        
        if found_item:
            self.tree_widget.setCurrentItem(found_item)
        else:
            self.tree_widget.setCurrentItem(None)
        self.tree_widget.blockSignals(False) # Unblock signals


    def _select_item_in_tree(self):
        """Выбирает элементы в дереве, соответствующие выделенным объектам в документе."""
        self.tree_widget.blockSignals(True) # Block signals to prevent _on_item_clicked from being called
        
        # Clear existing selection in the tree widget
        self.tree_widget.clearSelection()

        for selected_doc_item in self._document.selected_items:
            # Iterate through all items in the tree to find the matching QTreeWidgetItem
            # This can be optimized if there's a direct mapping or a dictionary
            for i in range(self.tree_widget.topLevelItemCount()):
                layer_tree_item = self.tree_widget.topLevelItem(i)
                layer_data = layer_tree_item.data(0, Qt.UserRole)
                
                # Check if the selected item is a layer itself
                if layer_data == selected_doc_item:
                    layer_tree_item.setSelected(True)
                    # self.tree_widget.setCurrentItem(layer_tree_item) # Removed to allow multiple selections
                    break # Found the layer, move to next selected_doc_item
                
                # Check children of the layer
                for j in range(layer_tree_item.childCount()):
                    child_tree_item = layer_tree_item.child(j)
                    child_data = child_tree_item.data(0, Qt.UserRole)
                    if child_data == selected_doc_item:
                        child_tree_item.setSelected(True)
                        # self.tree_widget.setCurrentItem(child_tree_item) # Removed to allow multiple selections
                        layer_tree_item.setExpanded(True) # Expand parent layer if child is selected
                        break # Found the child, move to next selected_doc_item
        
        self.tree_widget.blockSignals(False) # Unblock signals

    def _tree_dragEnterEvent(self, event):
        if event.source() == self.tree_widget:
            event.acceptProposedAction()
        else:
            event.ignore()

    def _tree_dragMoveEvent(self, event):
        if event.source() == self.tree_widget:
            event.acceptProposedAction()
        else:
            event.ignore()

    def _tree_dropEvent(self, event):
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            event.ignore()
            return

        # Нам нужно понять, КУДА мы перетаскиваем. 
        # tree_widget.itemAt(event.pos()) возвращает элемент под мышкой.
        target_item = self.tree_widget.itemAt(event.pos())
        
        # Определяем положение перетаскивания относительно target_item (выше, на него, ниже)
        drop_pos = self.tree_widget.dropIndicatorPosition()
        
        # Разделим выделенные элементы на Слои и Фигуры
        dragged_layers = []
        dragged_shapes = []
        for item in selected_items:
            data = item.data(0, Qt.UserRole)
            if isinstance(data, LayerItem):
                dragged_layers.append(item)
            else:
                dragged_shapes.append(item)

        # Сценарий 1: Драг слоев (изменение порядка слоев)
        if dragged_layers:
            # Запрещено тащить слои внутрь других слоев или фигур
            # Список всех слоев до изменений
            old_layers = self._document.layers.copy()
            new_layers = old_layers.copy()

            # Удаляем перемещаемые слои из временного списка слоев
            move_layers_data = [item.data(0, Qt.UserRole) for item in dragged_layers]
            for layer_data in move_layers_data:
                if layer_data in new_layers:
                    new_layers.remove(layer_data)

            # Находим целевой индекс для вставки
            if target_item:
                target_data = target_item.data(0, Qt.UserRole)
                # Если target_data не LayerItem, найдем его родительский слой
                if not isinstance(target_data, LayerItem):
                    parent_item = target_item.parent()
                    if parent_item:
                        target_data = parent_item.data(0, Qt.UserRole)
                    else:
                        target_data = None
                
                if isinstance(target_data, LayerItem) and target_data in new_layers:
                    dest_idx = new_layers.index(target_data)
                    # Если drop_pos - ниже элемента, то вставляем ПОСЛЕ этого элемента
                    from PyQt5.QtWidgets import QAbstractItemView
                    if drop_pos == QAbstractItemView.BelowItem:
                        dest_idx += 1
                else:
                    dest_idx = len(new_layers)
            else:
                dest_idx = len(new_layers)

            # Вставляем перетаскиваемые слои в позицию dest_idx
            for layer_data in reversed(move_layers_data):
                new_layers.insert(dest_idx, layer_data)

            # Если порядок изменился, запускаем команду!
            if old_layers != new_layers:
                from vector_editor.core.commands import ReorderLayersCommand
                cmd = ReorderLayersCommand(self._document, old_layers, new_layers)
                self._document.push_command(cmd)
                self._populate_layers()
            
            event.acceptProposedAction()
            return

        # Сценарий 2: Драг фигур (перемещение между слоями или урегулирование порядка внутри слоя)
        if dragged_shapes:
            if not target_item:
                event.ignore()
                return

            target_data = target_item.data(0, Qt.UserRole)
            
            # Определяем целевой слой и желаемую позицию (индекс) внутри него
            target_layer = None
            insert_index = None

            from PyQt5.QtWidgets import QAbstractItemView
            if isinstance(target_data, LayerItem):
                target_layer = target_data
                if drop_pos == QAbstractItemView.OnItem:
                    # Перетащили НА слой -> помещаем в конец этого слоя
                    insert_index = len(target_layer.childItems())
                elif drop_pos == QAbstractItemView.AboveItem:
                    # Перетащили чуть выше слоя -> помещаем в начало этого слоя
                    insert_index = 0
                elif drop_pos == QAbstractItemView.BelowItem:
                    # Перетащили чуть ниже слоя -> помещаем в начало этого слоя (или конец, но logical - в начало)
                    insert_index = 0
            else:
                # Перетащили на/около другой фигуры
                parent_tree_item = target_item.parent()
                if parent_tree_item:
                    target_layer = parent_tree_item.data(0, Qt.UserRole)
                    # Находим индекс фигуры под курсором в ее слое
                    sibling_items = target_layer.childItems()
                    if target_data in sibling_items:
                        idx = sibling_items.index(target_data)
                        if drop_pos == QAbstractItemView.AboveItem:
                            insert_index = idx
                        elif drop_pos == QAbstractItemView.BelowItem:
                            insert_index = idx + 1
                        else: # OnItem
                            insert_index = idx

            if target_layer is None:
                event.ignore()
                return

            # Список перемещаемых объектов QGraphicsItem
            shapes_data = [item.data(0, Qt.UserRole) for item in dragged_shapes]
            
            # Строим новую последовательность детей для целевого слоя
            current_children = target_layer.childItems()
            # Удаляем перетаскиваемые фигуры из списка детей (если они там были)
            new_children_order = [child for child in current_children if child not in shapes_data]
            
            # Корректируем insert_index
            if insert_index is None:
                insert_index = len(new_children_order)
            else:
                insert_index = min(max(0, insert_index), len(new_children_order))

            # Вставляем перетаскиваемые фигуры
            for shape in reversed(shapes_data):
                new_children_order.insert(insert_index, shape)

            # Проверяем, изменилось ли что-то
            # Изменился ли порядок (или слой)
            is_changed = False
            for shape in shapes_data:
                if shape.parentItem() != target_layer:
                    is_changed = True
                    break
            if not is_changed:
                # Если слой тот же, проверяем порядок детей
                if current_children != new_children_order:
                    is_changed = True

            if is_changed:
                from vector_editor.core.commands import MoveAndReorderItemsCommand
                cmd = MoveAndReorderItemsCommand(self._document, shapes_data, target_layer, new_children_order)
                self._document.push_command(cmd)
                self._populate_layers()

            event.acceptProposedAction()
            return
