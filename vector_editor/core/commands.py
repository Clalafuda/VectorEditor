import math
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QUndoCommand
from ..items.group_item import GroupItem

class AddItemCommand(QUndoCommand):
    """Команда добавления объекта"""
    def __init__ (self,document,item):
        super().__init__("Добавить фигуру")
        self.document=document
        self.item=item

    def redo(self):
        self.document._add_item(self.item)
    
    def undo(self):
        self.document._remove_item(self.item)

class RemoveItemCommand(QUndoCommand):
    """Команда удаления объекта"""
    def __init__ (self,document,item):
        super().__init__("Удалить фигуру")
        self.document=document
        self.item=item
    def redo(self):
        self.document._remove_item(self.item)
    def undo(self):
        self.document._remove_item(self.item)

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
        self.item.update()
    
    def undo(self):
        setattr(self.item,self.property_name,self.old_value)
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