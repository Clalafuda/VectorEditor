import math
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QUndoCommand
from ..items.group_item import GroupItem
from ..items.layer_item import LayerItem

class AddItemCommand(QUndoCommand):
    """Команда добавления объекта"""
    def __init__ (self,document,item):
        super().__init__("Добавить фигуру")
        self.document=document
        self.item=item
        self.layer = item.parentItem() # Store the layer

    def redo(self):
        if self.layer:
            self.layer.add_item(self.item) # Re-parent to layer
        self.document._add_item(self.item)
    
    def undo(self):
        self.document._remove_item(self.item)
        if self.layer:
            self.layer.remove_item(self.item) # Remove from layer

class RemoveItemCommand(QUndoCommand):
    """Команда удаления объекта"""
    def __init__ (self,document,item):
        super().__init__("Удалить фигуру")
        self.document=document
        self.item=item
        self.layer = item.parentItem() # Store the layer

    def redo(self):
        if self.layer:
            self.layer.remove_item(self.item) # Remove from layer
        self.document._remove_item(self.item)
    def undo(self):
        if self.layer:
            self.layer.add_item(self.item) # Re-parent to layer
        self.document._add_item(self.item)

class AddLayerCommand(QUndoCommand):
    def __init__(self, document, layer):
        super().__init__("Добавить слой")
        self.document = document
        self.layer = layer

    def redo(self):
        self.document._add_layer(self.layer)

    def undo(self):
        self.document._remove_layer(self.layer, No_scene_change=True)

class MoveItemToLayerCommand(QUndoCommand):
    """Команда перемещения объекта во вновь заданный слой и позицию внутри этого слоя"""
    def __init__(self, document, item, target_layer, target_index=None):
        super().__init__("Переместить фигуру в слой")
        self.document = document
        self.item = item
        self.old_layer = item.parentItem()
        self.target_layer = target_layer
        
        # Запоминаем старый индекс среди детей старого слоя
        if self.old_layer:
            self.old_index = self.old_layer.childItems().index(item)
        else:
            self.old_index = None

        self.target_index = target_index

    def redo(self):
        # Удаляем из старого слоя
        if self.old_layer:
            self.old_layer.remove_item(self.item)
        
        # Добавляем в новый слой
        self.target_layer.add_item(self.item)
        
        # Если задан индекс, перемещаем ребёнка в нужную позицию в иерархии QGraphicsItem
        if self.target_index is not None:
            # childItems() возвращает список детей в порядке их добавления / z-order.
            # Мы можем переупорядочить стек PyQt внутри target_layer.
            children = self.target_layer.childItems()
            if self.item in children:
                children.remove(self.item)
                children.insert(self.target_index, self.item)
                # Чтобы применить этот порядок к z-value или унаследованной цепочке событий отрисовки,
                # PyQt использует порядок добавления или относительные z-value.
                # Для QGraphicsItem порядок отрисовки детей без явных ZValue определяется порядком добавления/стека parent.
                # Сделаем переустановку parent у всех детей в правильном порядке, чтобы дерево графических объектов обновилось.
                for child in children:
                    child.setParentItem(None)
                for child in children:
                    self.target_layer.add_item(child)
        
        # Оповестим об изменении слоев
        self.document.layers_changed.emit()

    def undo(self):
        # Удаляем из нового слоя
        self.target_layer.remove_item(self.item)
        
        # Возвращаем в старый слой
        if self.old_layer:
            self.old_layer.add_item(self.item)
            if self.old_index is not None:
                children = self.old_layer.childItems()
                if self.item in children:
                    children.remove(self.item)
                    children.insert(self.old_index, self.item)
                    for child in children:
                        child.setParentItem(None)
                    for child in children:
                        self.old_layer.add_item(child)
        
        # Оповестим об изменении слоев
        self.document.layers_changed.emit()

class MoveAndReorderItemsCommand(QUndoCommand):
    """Команда перемещения и упорядочивания объектов между и внутри слоев"""
    def __init__(self, document, shapes, target_layer, target_children_order):
        super().__init__("Переместить и упорядочить фигуры")
        self.document = document
        self.shapes = shapes.copy()
        self.target_layer = target_layer
        self.target_children_order = target_children_order.copy()
        
        # Сохраняем исходное состояние каждого слоя, из которого берутся фигуры
        self.source_layers = {}
        for shape in self.shapes:
            src_layer = shape.parentItem()
            if src_layer and src_layer not in self.source_layers:
                self.source_layers[src_layer] = src_layer.childItems().copy()

    def redo(self):
        # 1. Отвязываем перемещаемые фигуры от старых слоев
        for shape in self.shapes:
            src_layer = shape.parentItem()
            if src_layer:
                src_layer.remove_item(shape)
                
        # 2. Выстраиваем в новом порядке в целевом слое
        for shape in self.target_children_order:
            self.target_layer.add_item(shape)

        self.document.layers_changed.emit()

    def undo(self):
        # 1. Удаляем перенесенные фигуры из целевого слоя
        for shape in self.shapes:
            if shape.parentItem() == self.target_layer:
                self.target_layer.remove_item(shape)
                
        # 2. Восстанавливаем порядок во всех затрагиваемых исходных слоях
        for src_layer, original_order in self.source_layers.items():
            for shape in original_order:
                src_layer.add_item(shape)

        self.document.layers_changed.emit()


class ReorderLayersCommand(QUndoCommand):
    """Команда изменения порядка слоев в документе"""
    def __init__(self, document, old_layers, new_layers):
        super().__init__("Изменить порядок слоев")
        self.document = document
        self.old_layers = old_layers.copy()
        self.new_layers = new_layers.copy()

    def redo(self):
        self.document.layers = self.new_layers.copy()
        self.document.reorder_layers()
        self.document.layers_changed.emit()

    def undo(self):
        self.document.layers = self.old_layers.copy()
        self.document.reorder_layers()
        self.document.layers_changed.emit()

class ReorderItemsCommand(QUndoCommand):
    """Команда изменения порядка фигур внутри одного слоя"""
    def __init__(self, document, layer, old_items, new_items):
        super().__init__("Изменить порядок фигур")
        self.document = document
        self.layer = layer
        self.old_items = old_items.copy()
        self.new_items = new_items.copy()

    def redo(self):
        # Переупорядочиваем детей у слоя
        for child in self.new_items:
            child.setParentItem(None)
        for child in self.new_items:
            self.layer.add_item(child)
        self.document.layers_changed.emit()

    def undo(self):
        for child in self.old_items:
            child.setParentItem(None)
        for child in self.old_items:
            self.layer.add_item(child)
        self.document.layers_changed.emit()

class RemoveLayerCommand(QUndoCommand):
    def __init__(self, document, layer):
        super().__init__("Удалить слой")
        self.document = document
        self.layer = layer
        self.removed_items = [] # Store all items that were in the layer

    def redo(self):
        # Store child items before removing the layer
        self.removed_items = self.layer.childItems()
        
        # Remove all child items from the document
        for item in self.removed_items:
            self.document._remove_item(item)
        
        # Finally, remove the layer itself
        self.document._remove_layer(self.layer)

    def undo(self):
        # Add the layer back
        self.document._add_layer(self.layer)
        
        # Add all previously removed child items back to the layer and document
        for item in self.removed_items:
            item.setParentItem(self.layer) # Re-parent to the layer
            self.document._add_item(item)
        
        self.document.set_active_layer(self.layer) # Re-activate the layer after undo

class MoveItemsCommand(QUndoCommand):
    """Команда перемещения объектов"""
    def __init__(self,document,items,old_positions,new_positions):
        super().__init__("Переместить")
        self.document=document
        self.items=items
        self.old_positions=old_positions
        self.new_positions=new_positions

    def redo(self):
        for item, pos in zip(self.items,self.new_positions):
            item.setPos(pos)
    def undo(self):
        for item, pos in zip(self.items,self.old_positions):
            item.setPos(pos)

class ChangePropertyCommand(QUndoCommand):
    """Команда изменения свойств объекта"""""
    def __init__(self,item,property_name,old_value,new_value):
        super().__init__(f"Изменить{property_name}")
        self.item=item
        self.property_name=property_name
        self.old_value=old_value
        self.new_value=new_value

    def redo(self):
        setattr(self.item,self.property_name,self.new_value)
        if hasattr(self.item, 'update_shadow_effect'):
            self.item.update_shadow_effect()
        self.item.update()
    
    def undo(self):
        setattr(self.item,self.property_name,self.old_value)
        if hasattr(self.item, 'update_shadow_effect'):
            self.item.update_shadow_effect()
        self.item.update()

class ChangeRectCommand(QUndoCommand):
    def __init__(self,item,old_rect,new_rect):
        super().__init__("Изменить размер")
        self.item = item
        self.old_rect=old_rect
        self.new_rect=new_rect
    def redo(self):
        self.item.rect=self.new_rect
        self.item.update()
    def undo(self):
        self.item.rect=self.old_rect
        self.item.update()

class ChangeRotationCommand(QUndoCommand):
    def __init__(self, item, old_rotation, new_rotation):
        super().__init__("Повернуть")
        self.item = item
        self.old_rotation = old_rotation
        self.new_rotation = new_rotation
    
    def redo(self):
        self.item.setRotation(self.new_rotation)
        self.item.update()
    
    def undo(self):
        self.item.setRotation(self.old_rotation)
        self.item.update()

class GroupItemsCommand(QUndoCommand):
    def __init__(self, document, items):
        super().__init__("Сгруппировать")
        self.document = document
        self.items = items.copy()
        self.group = None

        self.absolute_positions = []
        self.absolute_rotations = []
        self.absolute_scales = []
    
    def redo(self):
        print(f"GroupItemsCommand.redo: creating group")
        self.group = GroupItem()

        parent = None
        for item in self.items:
            if parent is None:
                parent = item.parentItem()
            elif item.parentItem() != parent:
                parent = None
                break

        if parent:
            self.group.setParentItem(parent)
        #print(f"Group has {len(self.group.childItems())} children")
        #print(f"GroupItemsCommand.redo: self.items has {len(self.items)} items")

        for item in self.items:
            abs_pos = item.pos()
            abs_rot = item.rotation()
            abs_scale = item.scale()
            
            self.absolute_positions.append(abs_pos)
            self.absolute_rotations.append(abs_rot)
            self.absolute_scales.append(abs_scale)

            item.setParentItem(self.group)
            item.setPos(abs_pos)
            item.setRotation(abs_rot)
            item.setScale(abs_scale)
        
        self.document._add_item(self.group)
        for item in self.items:
            self.document._remove_item(item,True)
        
        
    
    def undo(self):
        # Извлечь объекты из группы
        parent_group = self.group.parentItem()
        for item,abs_pos,abs_rot,abs_scale in zip( self.items, self.absolute_positions, self.absolute_rotations,self.absolute_scales):
            if item.parentItem():
                item.setParentItem(None)
            item.setPos(abs_pos)
            item.setRotation(abs_rot)
            item.setScale(abs_scale)
            self.document._add_item(item)

        

        self.document._remove_item(self.group)
        self.group = None


class UngroupItemsCommand(QUndoCommand):
    def __init__(self, document, group):
        super().__init__("Разгруппировать")
        self.document = document
        self.group = group
        self.items = []
        self.absolute_positions=[]
        self.absolute_rotations=[]
        self.absolute_scales=[]
    
    def redo(self):
        # 1. Сохраняем детей
        self.items = self.group.childItems()
        parent_group = self.group.parentItem()

        group_pos=self.group.pos()
        group_rot=self.group.rotation()
        group_scale=self.group.scale()

        self.absolute_positions=[]
        self.absolute_rotations=[]
        self.absolute_scales=[]

        for item in self.items:

            local_pos=item.pos()
            local_rot=item.rotation()
            local_scale=item.scale()

            abs_pos=local_pos
            if group_rot !=0:
                rad =group_rot*math.pi/180
                cos =math.cos(rad)
                sin=math.sin(rad)
                abs_pos=QPointF(
                    local_pos.x()*cos-local_pos.y()*sin,
                    local_pos.x()*sin+local_pos.y()*cos
                )
            abs_rot=local_rot + group_rot
            abs_pos = abs_pos * group_scale 
            abs_pos += group_pos
            abs_scale = local_scale*group_scale

            self.absolute_positions.append(abs_pos)
            self.absolute_rotations.append(abs_rot)
            self.absolute_scales.append(abs_scale)

            item.setParentItem(None)
            if parent_group:
                item.setParentItem(parent_group)
            item.setPos(abs_pos)
            item.setRotation(abs_rot)
            item.setScale(abs_scale)

            self.document._add_item(item)
        self.document._remove_item(self.group)
        # # 2. Извлекаем объекты из группы
        # for item in self.items:
        #     item.setParentItem(None)
        
        # # 3. Добавляем объекты в документ
        # for item in self.items:
        #     self.document._add_item(item)
        
        # # 4. Удаляем группу
        # self.document._remove_item(self.group)
    
    def undo(self):
        # # 1. Добавляем группу в документ
        # self.document._add_item(self.group)
        
        # # 2. Перемещаем объекты обратно в группу
        # for item in self.items:
        #     item.setParentItem(self.group)
        
        # # 3. Удаляем объекты из документа
        # for item in self.items:
        #     self.document._remove_item(item)
        group_pos=self.group.pos()
        group_rot=self.group.rotation()
        group_scale=self.group.scale()
        parent_group = self.group.parentItem()

        for item, abs_pos,abs_rot,abs_scale in zip(
            self.items,self.absolute_positions,self.absolute_rotations,self.absolute_scales
        ):
            self.document._remove_item(item)
            
            local_pos=(abs_pos-group_pos)/group_scale if group_scale !=0 else abs_pos-group_pos
            
            if group_rot !=0:
                rad= -group_rot*math.pi/180
                cos=math.cos(rad)
                sin=math.sin(rad)
                local_pos=QPointF(
                    local_pos.x()*cos - local_pos.y()*sin,
                    local_pos.x()*sin + local_pos.y()*cos
                )
            abs_pos = abs_pos * group_scale  # ← масштаб
            abs_pos += group_pos
            local_rot =abs_rot-group_rot
            local_scale = abs_scale / group_scale if group_scale != 0 else 1
            if item.parentItem():
                item.setParentItem(None)
            item.setParentItem(self.group)
            item.setPos(local_pos)
            item.setRotation(local_rot)
            item.setScale(local_scale)
        
        self.document._add_item(self.group)