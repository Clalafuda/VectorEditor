from PyQt5.QtWidgets import (QDockWidget, QTreeWidget, QTreeWidgetItem,
                             QMenu, QInputDialog, QMessageBox, QAbstractItemView, QApplication, QGraphicsItem,
                             QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QToolButton) # Added QLabel, QHBoxLayout, QToolButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
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
        
        main_layout.addWidget(self.tree_widget) # Add tree widget to the layout
        
        # Create buttons
        add_layer_button = QPushButton("Добавить слой", self)
        
        # Add buttons to the layout
        main_layout.addWidget(add_layer_button)
        
        self.setWidget(central_widget) # Set the central widget for the dock
        
        self.tree_widget.itemChanged.connect(self._on_item_changed)
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        
        # Connect button signals
        add_layer_button.clicked.connect(self._add_layer)
        
        self._populate_layers()

    def _populate_layers(self):
        self.tree_widget.clear()
        for layer in self._document.layers:
            self._add_layer_to_tree(layer)
            # Expand the layer item by default
            item = self.tree_widget.findItems(layer.name, Qt.MatchExactly, 0)[0] # Assuming unique layer names
            if item:
                item.setExpanded(True)

    def _add_layer_to_tree(self, layer):
        item = QTreeWidgetItem(self.tree_widget, [layer.name])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(0, Qt.UserRole, layer)
        self.tree_widget.addTopLevelItem(item)
        for child_item in layer.childItems():
            self._add_child_item_to_tree(item, child_item)

    def _add_child_item_to_tree(self, parent_item, child_item_data):
        item = QTreeWidgetItem(parent_item, [child_item_data.name])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(0, Qt.UserRole, child_item_data)
        parent_item.addChild(item)

    def _on_item_changed(self, item, column):
        layer = item.data(0, Qt.UserRole)
        if isinstance(layer, LayerItem) and item.text(column) != layer.name:
            layer.name = item.text(column)

    def _add_layer(self):
        name, ok = QInputDialog.getText(self, "Новый слой", "Введите имя слоя:")
        if ok and name:
            self._document.add_layer(name)
            self._populate_layers()


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
