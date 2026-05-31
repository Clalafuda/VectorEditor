from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, 
                             QLabel, QSpinBox, QDoubleSpinBox, 
                             QColorDialog, QPushButton, QLineEdit)
from PyQt5.QtCore import Qt, QPointF,QRectF
from ..core.commands import ChangePropertyCommand, ChangeRectCommand, MoveItemsCommand, ChangeRotationCommand
from ..items.group_item import GroupItem
class PropertiesDock(QDockWidget):
    def __init__(self,document,parent=None):
        super().__init__("Свойства",parent)
        self.document=document

        self.current_item= None
        self._updating=False

        self.create_widgets()

        document.selection_changed.connect(self.on_selection_changed)

        self.setWidget(self.main_widget)

    def create_widgets(self):
        """"Создаёт виджеты для свойств"""
        self.main_widget=QWidget()
        layout=QVBoxLayout()

        layout.addWidget(QLabel("Имя:"))
        self.name_edit=QLineEdit()
        self.name_edit.editingFinished.connect(self.on_name_changed)
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Позиция:"))
        pos_layout=QVBoxLayout()
        
        self.x_spin=QDoubleSpinBox()
        self.x_spin.setRange(-10000,10000)
        self.x_spin.valueChanged.connect(self.on_position_changed)

        self.y_spin=QDoubleSpinBox()
        self.y_spin.setRange(-10000,10000)
        self.y_spin.valueChanged.connect(self.on_position_changed)

        pos_layout.addWidget(self.x_spin)
        pos_layout.addWidget(self.y_spin)
        layout.addLayout(pos_layout)

        layout.addWidget(QLabel("Размер:"))
        size_layout = QVBoxLayout()
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 10000)
        self.width_spin.valueChanged.connect(self.on_size_changed)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 10000)
        self.height_spin.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)
        
        layout.addWidget(QLabel("Поворот"))
        self.rotation_spin=QDoubleSpinBox()
        self.rotation_spin.setRange(-360,360)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.valueChanged.connect(self.on_rotation_changed)
        layout.addWidget(self.rotation_spin)

        # Цвет заливки
        layout.addWidget(QLabel("Заливка:"))
        self.fill_color_btn = QPushButton()
        self.fill_color_btn.clicked.connect(self.on_fill_color_clicked)
        layout.addWidget(self.fill_color_btn)
        
        # Цвет обводки
        layout.addWidget(QLabel("Обводка:"))
        self.stroke_color_btn = QPushButton()
        self.stroke_color_btn.clicked.connect(self.on_stroke_color_clicked)
        layout.addWidget(self.stroke_color_btn)
        
        # Толщина обводки
        layout.addWidget(QLabel("Толщина:"))
        self.stroke_width_spin = QDoubleSpinBox()
        self.stroke_width_spin.setRange(0.1, 100)
        self.stroke_width_spin.valueChanged.connect(self.on_stroke_width_changed)
        layout.addWidget(self.stroke_width_spin)
        
        layout.addStretch()
        self.main_widget.setLayout(layout)

    def on_selection_changed(self):
        """"Обновление панели при смене выделения"""
        selected=self.document.selected_items

        if len(selected)==1:
            self.current_item=selected[0]
            self.setEnabled(True)
            self.update_from_item()
        elif len(selected)>1:
            self.current_item=None
            self.setEnabled(False)
        else:
            self.current_item=None
            self.setEnabled(False)

    def update_from_item(self):
        if not self.current_item or self._updating:
            return
        
        self._updating=True
        self.name_edit.blockSignals(True)
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.stroke_width_spin.blockSignals(True)
        self.rotation_spin.blockSignals(True)

        is_group = isinstance(self.current_item, GroupItem)

        if is_group:
            child_count = len(self.current_item.childItems())
            self.name_edit.setText(f"Группа ({child_count} объектов)")
            self.name_edit.setEnabled(False)
        else:
            self.name_edit.setText(getattr(self.current_item, 'name', ''))
            self.name_edit.setEnabled(True)

       # self.name_edit.setText(getattr(self.current_item,'name',''))

        pos=self.current_item.pos()
        self.x_spin.setValue(pos.x())
        self.y_spin.setValue(pos.y())
        self.x_spin.setEnabled(True)
        self.y_spin.setEnabled(True)

        # if hasattr(self.current_item,'rect'):
        #     rect=self.current_item.rect
        #     self.width_spin.setValue(rect.width())
        #     self.height_spin.setValue(rect.height())
        
        if is_group:
            rect = self.current_item.boundingRect()
            self.width_spin.setValue(rect.width())
            self.height_spin.setValue(rect.height())
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
        elif hasattr(self.current_item, 'rect'):
            rect = self.current_item.rect
            self.width_spin.setValue(rect.width())
            self.height_spin.setValue(rect.height())
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
        else:
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)

        # Цвета
        # fill_color = getattr(self.current_item, 'fill_color', None)
        # if fill_color:
        #     self.fill_color_btn.setStyleSheet(f"background-color: {fill_color.name()}")

        if is_group:
            self.fill_color_btn.setEnabled(False)
            self.stroke_color_btn.setEnabled(False)
            self.stroke_width_spin.setEnabled(False)
        else:
            # Цвет заливки
            fill_color = getattr(self.current_item, 'fill_color', None)
            if fill_color:
                self.fill_color_btn.setStyleSheet(f"background-color: {fill_color.name()}")
            self.fill_color_btn.setEnabled(True)
        
        stroke_color = getattr(self.current_item, 'stroke_color', None)
        if stroke_color:
            self.stroke_color_btn.setStyleSheet(f"background-color: {stroke_color.name()}")
        self.stroke_color_btn.setEnabled(True)

        # Толщина обводки
        self.stroke_width_spin.setValue(getattr(self.current_item, 'stroke_width', 1.0))
        self.stroke_width_spin.setEnabled(True)
        # Поворот
        self.rotation_spin.setValue(self.current_item.rotation())
        self.rotation_spin.setEnabled(True)
        # Разблокируем сигналы
        self.name_edit.blockSignals(False)
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)
        self.stroke_width_spin.blockSignals(False)
        self.rotation_spin.blockSignals(False)
        self._updating=False
    def on_name_changed(self):
        if self.current_item and not self._updating:
            old_name = getattr(self.current_item,'name','')
            new_name=self.name_edit.text()
            if old_name !=new_name:
                cmd=ChangePropertyCommand(self.current_item,'name',old_name,new_name)
                self.document.push_command(cmd)

    def on_position_changed(self):
        if self.current_item and not self._updating:
            old_pos=self.current_item.pos()
            new_pos=QPointF(self.x_spin.value(),self.y_spin.value())
            if old_pos != new_pos:
                cmd= MoveItemsCommand(self.document,[self.current_item],[old_pos],[new_pos])
                self.document.push_command(cmd)
            

    def on_size_changed(self):
        if self.current_item and not self._updating and hasattr(self.current_item,'rect'):
            if isinstance(self.current_item, GroupItem):
                return
            old_rect=self.current_item.rect
            new_rect=QRectF(old_rect.x(),old_rect.y(),self.width_spin.value(),self.height_spin.value())
            if old_rect !=new_rect:
                cmd=ChangeRectCommand(self.current_item,old_rect,new_rect)
                self.document.push_command(cmd)
            pass

    def on_fill_color_clicked(self):
        if self.current_item and not self._updating:
            if isinstance(self.current_item, GroupItem):
                return
            old_color=self.current_item.fill_color
            color=QColorDialog.getColor(old_color)
            if color.isValid() and color !=old_color:
                cmd = ChangePropertyCommand(self.current_item,'fill_color',old_color,color)
                self.document.push_command(cmd)
                self.update_from_item()
                

    def on_stroke_color_clicked(self):
        if self.current_item and not self._updating:
            if isinstance(self.current_item, GroupItem):
                return
            old_color=self.current_item.stroke_color
            color=QColorDialog.getColor(old_color)
            if color.isValid() and color!=old_color:
                cmd = ChangePropertyCommand(self.current_item,'stroke_color',old_color,color)
                self.document.push_command(cmd)
                self.update_from_item()

    def on_stroke_width_changed(self):
        if self.current_item and not self._updating:
            if isinstance(self.current_item, GroupItem):
                return
            old_width = self.current_item.stroke_width
            new_width = self.stroke_width_spin.value()
            if old_width != new_width:
                cmd = ChangePropertyCommand(self.current_item, 'stroke_width', old_width, new_width)
                self.document.push_command(cmd)
    
    def on_rotation_changed(self):
        if self.current_item and not self._updating:
            old_rot = self.current_item.rotation()
            new_rot = self.rotation_spin.value()
            if old_rot != new_rot:
                cmd = ChangeRotationCommand(self.current_item, old_rot, new_rot)
                self.document.push_command(cmd)