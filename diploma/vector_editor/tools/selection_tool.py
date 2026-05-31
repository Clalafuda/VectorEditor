from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsItemGroup
from .tool_base import Tool
from ..items.group_item import GroupItem
class SelectionTool(Tool):
    """Инструмент выделения"""
    
    def __init__(self, document):
        super().__init__(document)
        self.name = "Selection Tool"
        self.drag_start = None
        self.is_dragging = False
        self.rubber_band_active=False

        self._pending_pos= None
        self._pending_modifiers= None
        
        self.rubber_band= None
        self.rubber_band_start= None

        self._pending_rect=None
        self._pending_modifiers=None

        self._drag_items=[]
        self._drag_start_positions={}

        document.item_at_found.connect(self.on_item_at_found)
    def mouse_pressed(self, pos: QPointF, modifiers):
        """Нажатие мыши - выделение объектов"""
        self._pending_pos=pos
        self._pending_modifiers=modifiers
        
        self.document.request_item_at.emit(pos)
    def on_item_at_found(self,item):
        """Получен объект или None"""
        if self._pending_modifiers is None:
            return
        modifiers=self._pending_modifiers
        pos=self._pending_pos        
        if item:
            while item.parentItem() and isinstance(item.parentItem(), GroupItem):
                item = item.parentItem()
            if (modifiers & Qt.ControlModifier):
                if (item in self.document.selected_items):
                    self.document.unselect_item(item)
                else:
                    self.document.select_item(item,add_to_selection=True)
            else:
                if (item not in self.document.selected_items):
                    self.document.select_item(item,add_to_selection=False)
                self._drag_items=self.document.selected_items.copy()
                self._drag_start_positions={it: it.pos() for it in self._drag_items}
                self.drag_start=pos
                self.is_dragging= True
   
        else:    
            # Очистка выбора
            if not (modifiers & Qt.ControlModifier):
                self.document.clear_selection()
            self.rubber_band_active=True
            self.document.rubber_band_start.emit(pos)
        self._pending_pos= None
        self._pending_modifiers=None     
    
        
    def mouse_moved(self, pos: QPointF, modifiers):
        """Движение мыши - перемещение выделенных объектов"""
        if self.rubber_band_active:
            self.document.rubber_band_update.emit(pos)
            return
        if self.is_dragging and self.drag_start:
            # Перемещение выделенных объектов
            delta = pos - self.drag_start
            for item in self.document.selected_items:
                item.setPos(item.pos() + delta)
            self.drag_start = pos
            
    def mouse_released(self, pos: QPointF, modifiers):
        """Отпускание мыши"""
        if self.rubber_band_active:
            self.document.rubber_band_finish.emit(pos,modifiers)
            self.rubber_band_active=False
        if self.is_dragging and self._drag_items:
            new_positions=[item.pos() for item in self._drag_items]
            #print (new_positions)
            old_positions=[self._drag_start_positions[item] for item in self._drag_items]
           # print (old_positions)
            if old_positions!=new_positions:
                from ..core.commands import MoveItemsCommand
                cmd=MoveItemsCommand(
                    self.document,
                    self._drag_items,
                    old_positions,
                    new_positions
                )
                self.document.push_command(cmd)
        self._drag_items=[]
        self._drag_start_positions={}

        self.is_dragging = False
        self.drag_start = None

        self._pending_pos=None
        self._pending_modifiers=None