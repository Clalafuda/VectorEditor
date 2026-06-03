from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, 
                             QLabel, QSpinBox, QDoubleSpinBox, 
                             QColorDialog, QPushButton, QLineEdit,
                             QCheckBox, QComboBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QPointF,QRectF
from PyQt5.QtGui import QColor
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
        
        # Тип заливки
        layout.addWidget(QLabel("Тип заливки:"))
        self.fill_type_combo = QComboBox()
        self.fill_type_combo.addItems(["Сплошной", "Линейный градиент", "Радиальный градиент"])
        self.fill_type_combo.currentIndexChanged.connect(self.on_fill_type_changed)
        layout.addWidget(self.fill_type_combo)
        
        # Параметры градиента
        self.grad_start_btn_label = QLabel("Начало градиента:")
        self.grad_color_start_btn = QPushButton()
        self.grad_color_start_btn.clicked.connect(self.on_grad_color_start_clicked)
        
        self.grad_end_btn_label = QLabel("Конец градиента:")
        self.grad_color_end_btn = QPushButton()
        self.grad_color_end_btn.clicked.connect(self.on_grad_color_end_clicked)
        
        self.grad_angle_label = QLabel("Угол градиента (°):")
        self.grad_angle_spin = QDoubleSpinBox()
        self.grad_angle_spin.setRange(-360.0, 360.0)
        self.grad_angle_spin.valueChanged.connect(self.on_grad_angle_changed)
        
        self.grad_radius_label = QLabel("Радиус градиента:")
        self.grad_radius_spin = QDoubleSpinBox()
        self.grad_radius_spin.setRange(0.01, 10.0)
        self.grad_radius_spin.setSingleStep(0.05)
        self.grad_radius_spin.valueChanged.connect(self.on_grad_radius_changed)
        
        # --- Продвинутые SVG свойства градиента ---
        self.grad_spread_label = QLabel("Метод распространения (Spread):")
        self.grad_spread_combo = QComboBox()
        self.grad_spread_combo.addItems(["Pad (Растянуть)", "Reflect (Отразить)", "Repeat (Повторить)"])
        self.grad_spread_combo.currentIndexChanged.connect(self.on_grad_spread_changed)
        
        self.grad_stops_label = QLabel("Цветовые точки SVG ( 0.0:#color; ... ):")
        self.grad_stops_edit = QLineEdit()
        self.grad_stops_edit.setPlaceholderText("0.0:#ffffff; 1.0:#000000")
        self.grad_stops_edit.editingFinished.connect(self.on_grad_stops_changed)
        
        # Координаты линейного градиента
        self.grad_x1_label = QLabel("x1 (0.0 - 1.0):")
        self.grad_x1_spin = QDoubleSpinBox()
        self.grad_x1_spin.setRange(-10.0, 10.0)
        self.grad_x1_spin.setSingleStep(0.05)
        self.grad_x1_spin.valueChanged.connect(self.on_grad_coords_changed)

        self.grad_y1_label = QLabel("y1 (0.0 - 1.0):")
        self.grad_y1_spin = QDoubleSpinBox()
        self.grad_y1_spin.setRange(-10.0, 10.0)
        self.grad_y1_spin.setSingleStep(0.05)
        self.grad_y1_spin.valueChanged.connect(self.on_grad_coords_changed)

        self.grad_x2_label = QLabel("x2 (0.0 - 1.0):")
        self.grad_x2_spin = QDoubleSpinBox()
        self.grad_x2_spin.setRange(-10.0, 10.0)
        self.grad_x2_spin.setSingleStep(0.05)
        self.grad_x2_spin.valueChanged.connect(self.on_grad_coords_changed)

        self.grad_y2_label = QLabel("y2 (0.0 - 1.0):")
        self.grad_y2_spin = QDoubleSpinBox()
        self.grad_y2_spin.setRange(-10.0, 10.0)
        self.grad_y2_spin.setSingleStep(0.05)
        self.grad_y2_spin.valueChanged.connect(self.on_grad_coords_changed)

        # Координаты радиального градиента
        self.grad_cx_label = QLabel("Центр cx (0.0 - 1.0):")
        self.grad_cx_spin = QDoubleSpinBox()
        self.grad_cx_spin.setRange(-10.0, 10.0)
        self.grad_cx_spin.setSingleStep(0.05)
        self.grad_cx_spin.valueChanged.connect(self.on_grad_radial_coords_changed)

        self.grad_cy_label = QLabel("Центр cy (0.0 - 1.0):")
        self.grad_cy_spin = QDoubleSpinBox()
        self.grad_cy_spin.setRange(-10.0, 10.0)
        self.grad_cy_spin.setSingleStep(0.05)
        self.grad_cy_spin.valueChanged.connect(self.on_grad_radial_coords_changed)

        self.grad_r_label = QLabel("Радиус r (0.0 - 1.0):")
        self.grad_r_spin = QDoubleSpinBox()
        self.grad_r_spin.setRange(0.0, 10.0)
        self.grad_r_spin.setSingleStep(0.05)
        self.grad_r_spin.valueChanged.connect(self.on_grad_radial_coords_changed)

        self.grad_fx_label = QLabel("Фокус fx (0.0 - 1.0):")
        self.grad_fx_spin = QDoubleSpinBox()
        self.grad_fx_spin.setRange(-10.0, 10.0)
        self.grad_fx_spin.setSingleStep(0.05)
        self.grad_fx_spin.valueChanged.connect(self.on_grad_radial_coords_changed)

        self.grad_fy_label = QLabel("Фокус fy (0.0 - 1.0):")
        self.grad_fy_spin = QDoubleSpinBox()
        self.grad_fy_spin.setRange(-10.0, 10.0)
        self.grad_fy_spin.setSingleStep(0.05)
        self.grad_fy_spin.valueChanged.connect(self.on_grad_radial_coords_changed)

        layout.addWidget(self.grad_start_btn_label)
        layout.addWidget(self.grad_color_start_btn)
        layout.addWidget(self.grad_end_btn_label)
        layout.addWidget(self.grad_color_end_btn)
        layout.addWidget(self.grad_angle_label)
        layout.addWidget(self.grad_angle_spin)
        layout.addWidget(self.grad_radius_label)
        layout.addWidget(self.grad_radius_spin)
        
        # Добавление продвинутых виджетов градиента
        layout.addWidget(self.grad_spread_label)
        layout.addWidget(self.grad_spread_combo)
        layout.addWidget(self.grad_stops_label)
        layout.addWidget(self.grad_stops_edit)
        
        layout.addWidget(self.grad_x1_label)
        layout.addWidget(self.grad_x1_spin)
        layout.addWidget(self.grad_y1_label)
        layout.addWidget(self.grad_y1_spin)
        layout.addWidget(self.grad_x2_label)
        layout.addWidget(self.grad_x2_spin)
        layout.addWidget(self.grad_y2_label)
        layout.addWidget(self.grad_y2_spin)
        
        layout.addWidget(self.grad_cx_label)
        layout.addWidget(self.grad_cx_spin)
        layout.addWidget(self.grad_cy_label)
        layout.addWidget(self.grad_cy_spin)
        layout.addWidget(self.grad_r_label)
        layout.addWidget(self.grad_r_spin)
        layout.addWidget(self.grad_fx_label)
        layout.addWidget(self.grad_fx_spin)
        layout.addWidget(self.grad_fy_label)
        layout.addWidget(self.grad_fy_spin)
        
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

        # --- Свойства падающей тени ---
        self.shadow_sep = QLabel("--- Падающая тень ---")
        layout.addWidget(self.shadow_sep)
        
        self.shadow_check = QCheckBox("Включить тень")
        self.shadow_check.stateChanged.connect(self.on_shadow_enable_changed)
        layout.addWidget(self.shadow_check)
        
        self.shadow_color_label = QLabel("Цвет тени:")
        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.clicked.connect(self.on_shadow_color_clicked)
        
        self.shadow_blur_label = QLabel("Размытие тени:")
        self.shadow_blur_spin = QDoubleSpinBox()
        self.shadow_blur_spin.setRange(0, 100)
        self.shadow_blur_spin.valueChanged.connect(self.on_shadow_params_changed)
        
        self.shadow_dx_label = QLabel("Смещение dx:")
        self.shadow_dx_spin = QDoubleSpinBox()
        self.shadow_dx_spin.setRange(-100, 100)
        self.shadow_dx_spin.valueChanged.connect(self.on_shadow_params_changed)
        
        self.shadow_dy_label = QLabel("Смещение dy:")
        self.shadow_dy_spin = QDoubleSpinBox()
        self.shadow_dy_spin.setRange(-100, 100)
        self.shadow_dy_spin.valueChanged.connect(self.on_shadow_params_changed)
        
        layout.addWidget(self.shadow_color_label)
        layout.addWidget(self.shadow_color_btn)
        layout.addWidget(self.shadow_blur_label)
        layout.addWidget(self.shadow_blur_spin)
        layout.addWidget(self.shadow_dx_label)
        layout.addWidget(self.shadow_dx_spin)
        layout.addWidget(self.shadow_dy_label)
        layout.addWidget(self.shadow_dy_spin)

        # Параметры неявной функции
        self.func_sep = QLabel("--- Математическая функция ---")
        layout.addWidget(self.func_sep)
        
        self.func_expr_label = QLabel("Уравнение (F(x,y) = G(x,y)):")
        layout.addWidget(self.func_expr_label)
        self.equation_edit = QLineEdit()
        self.equation_edit.editingFinished.connect(self.on_equation_changed)
        layout.addWidget(self.equation_edit)
        
        self.xmin_label = QLabel("x min:")
        self.xmin_spin = QDoubleSpinBox()
        self.xmin_spin.setRange(-10000, 10000)
        self.xmin_spin.valueChanged.connect(self.on_limits_changed)
        
        self.xmax_label = QLabel("x max:")
        self.xmax_spin = QDoubleSpinBox()
        self.xmax_spin.setRange(-10000, 10000)
        self.xmax_spin.valueChanged.connect(self.on_limits_changed)
        
        self.ymin_label = QLabel("y min:")
        self.ymin_spin = QDoubleSpinBox()
        self.ymin_spin.setRange(-10000, 10000)
        self.ymin_spin.valueChanged.connect(self.on_limits_changed)
        
        self.ymax_label = QLabel("y max:")
        self.ymax_spin = QDoubleSpinBox()
        self.ymax_spin.setRange(-10000, 10000)
        self.ymax_spin.valueChanged.connect(self.on_limits_changed)
        
        layout.addWidget(self.xmin_label)
        layout.addWidget(self.xmin_spin)
        layout.addWidget(self.xmax_label)
        layout.addWidget(self.xmax_spin)
        layout.addWidget(self.ymin_label)
        layout.addWidget(self.ymin_spin)
        layout.addWidget(self.ymax_label)
        layout.addWidget(self.ymax_spin)
        
        self.set_function_widgets_visible(False)

        # Параметры сплайна
        self.spline_sep = QLabel("--- Настройки сплайна ---")
        layout.addWidget(self.spline_sep)
        
        self.tension_label = QLabel("Натяжение сплайна (Tension):")
        layout.addWidget(self.tension_label)
        self.tension_spin = QDoubleSpinBox()
        self.tension_spin.setRange(0.0, 2.0)
        self.tension_spin.setSingleStep(0.1)
        self.tension_spin.valueChanged.connect(self.on_spline_tension_changed)
        layout.addWidget(self.tension_spin)
        
        self.closed_check = QCheckBox("Замкнутый сплайн")
        self.closed_check.stateChanged.connect(self.on_spline_closed_changed)
        layout.addWidget(self.closed_check)
        
        self.set_spline_widgets_visible(False)
        
        # --- Свойства Clip-path (Обрезка) ---
        self.clip_sep = QLabel("--- Обрезка контуром (Clip-Path) ---")
        layout.addWidget(self.clip_sep)
        
        self.clip_mode_label = QLabel("Логика обрезки:")
        layout.addWidget(self.clip_mode_label)
        
        self.clip_mode_combo = QComboBox()
        self.clip_mode_combo.addItems(["Пересечение (AND)", "Объединение (OR)"])
        self.clip_mode_combo.currentIndexChanged.connect(self.on_clip_mode_changed)
        layout.addWidget(self.clip_mode_combo)
        
        self.clip_list_widget = QListWidget()
        self.clip_list_widget.setFixedHeight(120)
        self.clip_list_widget.itemChanged.connect(self.on_clip_list_item_changed)
        layout.addWidget(self.clip_list_widget)
        
        self.set_clip_widgets_visible(False)
        
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
            self.set_function_widgets_visible(False)
            self.set_spline_widgets_visible(False)
            self.set_clip_widgets_visible(False)
            self.update_gradient_field_visibilities()
        else:
            self.current_item=None
            self.setEnabled(False)
            self.set_function_widgets_visible(False)
            self.set_spline_widgets_visible(False)
            self.set_clip_widgets_visible(False)
            self.update_gradient_field_visibilities()

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
        self.equation_edit.blockSignals(True)
        self.xmin_spin.blockSignals(True)
        self.xmax_spin.blockSignals(True)
        self.ymin_spin.blockSignals(True)
        self.ymax_spin.blockSignals(True)
        self.tension_spin.blockSignals(True)
        self.closed_check.blockSignals(True)
        self.fill_type_combo.blockSignals(True)
        self.grad_angle_spin.blockSignals(True)
        self.grad_radius_spin.blockSignals(True)
        
        self.grad_spread_combo.blockSignals(True)
        self.grad_stops_edit.blockSignals(True)
        self.grad_x1_spin.blockSignals(True)
        self.grad_y1_spin.blockSignals(True)
        self.grad_x2_spin.blockSignals(True)
        self.grad_y2_spin.blockSignals(True)
        self.grad_cx_spin.blockSignals(True)
        self.grad_cy_spin.blockSignals(True)
        self.grad_r_spin.blockSignals(True)
        self.grad_fx_spin.blockSignals(True)
        self.grad_fy_spin.blockSignals(True)
        
        self.shadow_check.blockSignals(True)
        self.shadow_blur_spin.blockSignals(True)
        self.shadow_dx_spin.blockSignals(True)
        self.shadow_dy_spin.blockSignals(True)
        self.clip_list_widget.blockSignals(True)
        self.clip_mode_combo.blockSignals(True)

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

        from ..items.function_item import FunctionItem
        is_function = isinstance(self.current_item, FunctionItem)
        self.set_function_widgets_visible(is_function)
        if is_function:
            self.equation_edit.setText(self.current_item.expression)
            self.xmin_spin.setValue(self.current_item.x_min)
            self.xmax_spin.setValue(self.current_item.x_max)
            self.ymin_spin.setValue(self.current_item.y_min)
            self.ymax_spin.setValue(self.current_item.y_max)

        from ..items.spline_item import SplineItem
        is_spline = isinstance(self.current_item, SplineItem)
        self.set_spline_widgets_visible(is_spline)
        if is_spline:
            self.tension_spin.setValue(self.current_item.tension)
            self.closed_check.setChecked(self.current_item.closed)

        self.set_clip_widgets_visible(not is_group)

        if not is_group:
            # Заполняем clip_list_widget
            self.clip_list_widget.blockSignals(True)
            self.clip_list_widget.clear()
            
            from ..items.layer_item import LayerItem
            current_clips = getattr(self.current_item, '_clip_paths', [])
            
            for item in self.document.items:
                if item != self.current_item and not isinstance(item, (LayerItem, GroupItem)) and hasattr(item, 'name'):
                    name_text = f"{item.name} (id: {id(item) % 1000})"
                    list_item = QListWidgetItem(name_text)
                    list_item.setData(Qt.UserRole, item)
                    
                    if item in current_clips:
                        list_item.setCheckState(Qt.Checked)
                    else:
                        list_item.setCheckState(Qt.Unchecked)
                        
                    self.clip_list_widget.addItem(list_item)
            
            self.clip_list_widget.blockSignals(False)
            
            # Заполняем clip_mode_combo
            self.clip_mode_combo.blockSignals(True)
            clip_mode = getattr(self.current_item, 'clip_mode', 'and')
            if clip_mode == 'or':
                self.clip_mode_combo.setCurrentIndex(1)
            else:
                self.clip_mode_combo.setCurrentIndex(0)
            self.clip_mode_combo.blockSignals(False)
            
            # Настройка градиента
            f_type = getattr(self.current_item, 'fill_type', 'solid')
            if f_type == 'solid':
                self.fill_type_combo.setCurrentIndex(0)
            elif f_type == 'linear':
                self.fill_type_combo.setCurrentIndex(1)
            elif f_type == 'radial':
                self.fill_type_combo.setCurrentIndex(2)
                
            c_start = getattr(self.current_item, 'grad_color_start', QColor(255, 255, 255))
            c_end = getattr(self.current_item, 'grad_color_end', QColor(0, 0, 0))
            self.grad_color_start_btn.setStyleSheet(f"background-color: {c_start.name()}")
            self.grad_color_end_btn.setStyleSheet(f"background-color: {c_end.name()}")
            
            self.grad_angle_spin.setValue(getattr(self.current_item, 'grad_angle', 0.0))
            self.grad_radius_spin.setValue(getattr(self.current_item, 'grad_radius', 0.5))
            
            # Продвинутые SVG градиенты
            spread_str = getattr(self.current_item, 'grad_spread', 'pad')
            if spread_str == 'pad':
                self.grad_spread_combo.setCurrentIndex(0)
            elif spread_str == 'reflect':
                self.grad_spread_combo.setCurrentIndex(1)
            elif spread_str == 'repeat':
                self.grad_spread_combo.setCurrentIndex(2)
                
            self.grad_stops_edit.setText(getattr(self.current_item, 'grad_stops', ''))
            
            self.grad_x1_spin.setValue(getattr(self.current_item, 'grad_x1', 0.0))
            self.grad_y1_spin.setValue(getattr(self.current_item, 'grad_y1', 0.0))
            self.grad_x2_spin.setValue(getattr(self.current_item, 'grad_x2', 1.0))
            self.grad_y2_spin.setValue(getattr(self.current_item, 'grad_y2', 0.0))
            
            self.grad_cx_spin.setValue(getattr(self.current_item, 'grad_cx', 0.5))
            self.grad_cy_spin.setValue(getattr(self.current_item, 'grad_cy', 0.5))
            self.grad_r_spin.setValue(getattr(self.current_item, 'grad_r', 0.5))
            self.grad_fx_spin.setValue(getattr(self.current_item, 'grad_fx', 0.5))
            self.grad_fy_spin.setValue(getattr(self.current_item, 'grad_fy', 0.5))
            
            # Тень
            has_shadow = getattr(self.current_item, 'shadow_enable', False)
            self.shadow_check.setChecked(has_shadow)
            
            shadow_c = getattr(self.current_item, 'shadow_color', QColor(0, 0, 0, 128))
            self.shadow_color_btn.setStyleSheet(f"background-color: {shadow_c.name()}")
            
            self.shadow_blur_spin.setValue(getattr(self.current_item, 'shadow_blur', 8.0))
            self.shadow_dx_spin.setValue(getattr(self.current_item, 'shadow_dx', 4.0))
            self.shadow_dy_spin.setValue(getattr(self.current_item, 'shadow_dy', 4.0))

        self.update_gradient_field_visibilities()

        # Разблокируем сигналы
        self.name_edit.blockSignals(False)
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)
        self.stroke_width_spin.blockSignals(False)
        self.rotation_spin.blockSignals(False)
        self.equation_edit.blockSignals(False)
        self.xmin_spin.blockSignals(False)
        self.xmax_spin.blockSignals(False)
        self.ymin_spin.blockSignals(False)
        self.ymax_spin.blockSignals(False)
        self.tension_spin.blockSignals(False)
        self.closed_check.blockSignals(False)
        self.fill_type_combo.blockSignals(False)
        self.grad_angle_spin.blockSignals(False)
        self.grad_radius_spin.blockSignals(False)
        
        self.grad_spread_combo.blockSignals(False)
        self.grad_stops_edit.blockSignals(False)
        self.grad_x1_spin.blockSignals(False)
        self.grad_y1_spin.blockSignals(False)
        self.grad_x2_spin.blockSignals(False)
        self.grad_y2_spin.blockSignals(False)
        self.grad_cx_spin.blockSignals(False)
        self.grad_cy_spin.blockSignals(False)
        self.grad_r_spin.blockSignals(False)
        self.grad_fx_spin.blockSignals(False)
        self.grad_fy_spin.blockSignals(False)
        
        self.shadow_check.blockSignals(False)
        self.shadow_blur_spin.blockSignals(False)
        self.shadow_dx_spin.blockSignals(False)
        self.shadow_dy_spin.blockSignals(False)
        self.clip_list_widget.blockSignals(False)
        self.clip_mode_combo.blockSignals(False)
        
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

    def set_function_widgets_visible(self, visible):
        self.func_sep.setVisible(visible)
        self.func_expr_label.setVisible(visible)
        self.equation_edit.setVisible(visible)
        self.xmin_label.setVisible(visible)
        self.xmin_spin.setVisible(visible)
        self.xmax_label.setVisible(visible)
        self.xmax_spin.setVisible(visible)
        self.ymin_label.setVisible(visible)
        self.ymin_spin.setVisible(visible)
        self.ymax_label.setVisible(visible)
        self.ymax_spin.setVisible(visible)

    def on_equation_changed(self):
        if self.current_item and not self._updating:
            from ..items.function_item import FunctionItem
            if isinstance(self.current_item, FunctionItem):
                old_expr = self.current_item.expression
                new_expr = self.equation_edit.text()
                if old_expr != new_expr:
                    cmd = ChangePropertyCommand(self.current_item, 'expression', old_expr, new_expr)
                    self.document.push_command(cmd)

    def on_limits_changed(self):
        if self.current_item and not self._updating:
            from ..items.function_item import FunctionItem
            if isinstance(self.current_item, FunctionItem):
                old_xmin = self.current_item.x_min
                new_xmin = self.xmin_spin.value()
                if old_xmin != new_xmin:
                    cmd = ChangePropertyCommand(self.current_item, 'x_min', old_xmin, new_xmin)
                    self.document.push_command(cmd)
                    
                old_xmax = self.current_item.x_max
                new_xmax = self.xmax_spin.value()
                if old_xmax != new_xmax:
                    cmd = ChangePropertyCommand(self.current_item, 'x_max', old_xmax, new_xmax)
                    self.document.push_command(cmd)
                    
                old_ymin = self.current_item.y_min
                new_ymin = self.ymin_spin.value()
                if old_ymin != new_ymin:
                    cmd = ChangePropertyCommand(self.current_item, 'y_min', old_ymin, new_ymin)
                    self.document.push_command(cmd)
                    
                old_ymax = self.current_item.y_max
                new_ymax = self.ymax_spin.value()
                if old_ymax != new_ymax:
                    cmd = ChangePropertyCommand(self.current_item, 'y_max', old_ymax, new_ymax)
                    self.document.push_command(cmd)

    def set_spline_widgets_visible(self, visible):
        self.spline_sep.setVisible(visible)
        self.tension_label.setVisible(visible)
        self.tension_spin.setVisible(visible)
        self.closed_check.setVisible(visible)

    def set_clip_widgets_visible(self, visible):
        self.clip_sep.setVisible(visible)
        self.clip_mode_label.setVisible(visible)
        self.clip_mode_combo.setVisible(visible)
        self.clip_list_widget.setVisible(visible)

    def on_clip_mode_changed(self, index):
        if self.current_item and not self._updating:
            target_mode = 'or' if index == 1 else 'and'
            old_mode = getattr(self.current_item, 'clip_mode', 'and')
            if old_mode != target_mode:
                cmd = ChangePropertyCommand(self.current_item, 'clip_mode', old_mode, target_mode)
                self.document.push_command(cmd)

    def on_clip_list_item_changed(self, item):
        if self.current_item and not self._updating:
            new_clips = []
            for i in range(self.clip_list_widget.count()):
                list_item = self.clip_list_widget.item(i)
                if list_item.checkState() == Qt.Checked:
                    new_clips.append(list_item.data(Qt.UserRole))
            
            old_clips = getattr(self.current_item, '_clip_paths', [])
            if old_clips != new_clips:
                cmd = ChangePropertyCommand(self.current_item, 'clip_paths', old_clips, new_clips)
                self.document.push_command(cmd)

    def on_spline_tension_changed(self):
        if self.current_item and not self._updating:
            from ..items.spline_item import SplineItem
            if isinstance(self.current_item, SplineItem):
                old_tension = self.current_item.tension
                new_tension = self.tension_spin.value()
                if old_tension != new_tension:
                    cmd = ChangePropertyCommand(self.current_item, 'tension', old_tension, new_tension)
                    self.document.push_command(cmd)

    def on_spline_closed_changed(self):
        if self.current_item and not self._updating:
            from ..items.spline_item import SplineItem
            if isinstance(self.current_item, SplineItem):
                old_closed = self.current_item.closed
                new_closed = self.closed_check.isChecked()
                if old_closed != new_closed:
                    cmd = ChangePropertyCommand(self.current_item, 'closed', old_closed, new_closed)
                    self.document.push_command(cmd)

    def set_complex_gradient_widgets_visible(self, show_linear, show_radial):
        any_grad = show_linear or show_radial
        self.grad_spread_label.setVisible(any_grad)
        self.grad_spread_combo.setVisible(any_grad)
        self.grad_stops_label.setVisible(any_grad)
        self.grad_stops_edit.setVisible(any_grad)
        
        self.grad_x1_label.setVisible(show_linear)
        self.grad_x1_spin.setVisible(show_linear)
        self.grad_y1_label.setVisible(show_linear)
        self.grad_y1_spin.setVisible(show_linear)
        self.grad_x2_label.setVisible(show_linear)
        self.grad_x2_spin.setVisible(show_linear)
        self.grad_y2_label.setVisible(show_linear)
        self.grad_y2_spin.setVisible(show_linear)
        
        self.grad_cx_label.setVisible(show_radial)
        self.grad_cx_spin.setVisible(show_radial)
        self.grad_cy_label.setVisible(show_radial)
        self.grad_cy_spin.setVisible(show_radial)
        self.grad_r_label.setVisible(show_radial)
        self.grad_r_spin.setVisible(show_radial)
        self.grad_fx_label.setVisible(show_radial)
        self.grad_fx_spin.setVisible(show_radial)
        self.grad_fy_label.setVisible(show_radial)
        self.grad_fy_spin.setVisible(show_radial)

    def update_gradient_field_visibilities(self):
        if not self.current_item:
            self.fill_type_combo.setVisible(False)
            self.grad_start_btn_label.setVisible(False)
            self.grad_color_start_btn.setVisible(False)
            self.grad_end_btn_label.setVisible(False)
            self.grad_color_end_btn.setVisible(False)
            self.grad_angle_label.setVisible(False)
            self.grad_angle_spin.setVisible(False)
            self.grad_radius_label.setVisible(False)
            self.grad_radius_spin.setVisible(False)
            self.set_complex_gradient_widgets_visible(False, False)
            return
            
        is_group = isinstance(self.current_item, GroupItem)
        if is_group:
            self.fill_type_combo.setVisible(False)
            self.grad_start_btn_label.setVisible(False)
            self.grad_color_start_btn.setVisible(False)
            self.grad_end_btn_label.setVisible(False)
            self.grad_color_end_btn.setVisible(False)
            self.grad_angle_label.setVisible(False)
            self.grad_angle_spin.setVisible(False)
            self.grad_radius_label.setVisible(False)
            self.grad_radius_spin.setVisible(False)
            self.set_complex_gradient_widgets_visible(False, False)
            return

        self.fill_type_combo.setVisible(True)
        fill_type = getattr(self.current_item, 'fill_type', 'solid')
        self.grad_start_btn_label.setVisible(fill_type in ('linear', 'radial'))
        self.grad_color_start_btn.setVisible(fill_type in ('linear', 'radial'))
        self.grad_end_btn_label.setVisible(fill_type in ('linear', 'radial'))
        self.grad_color_end_btn.setVisible(fill_type in ('linear', 'radial'))
        self.grad_angle_label.setVisible(fill_type == 'linear')
        self.grad_angle_spin.setVisible(fill_type == 'linear')
        self.grad_radius_label.setVisible(fill_type == 'radial')
        self.grad_radius_spin.setVisible(fill_type == 'radial')
        
        self.set_complex_gradient_widgets_visible(fill_type == 'linear', fill_type == 'radial')

    def on_fill_type_changed(self, index):
        if self.current_item and not self._updating:
            types = ['solid', 'linear', 'radial']
            new_type = types[index]
            old_type = getattr(self.current_item, 'fill_type', 'solid')
            if old_type != new_type:
                cmd = ChangePropertyCommand(self.current_item, 'fill_type', old_type, new_type)
                self.document.push_command(cmd)
                self.update_gradient_field_visibilities()

    def update_stop_color_in_str(self, stops_str, target_offset, new_color_hex):
        if not stops_str:
            return f"{target_offset}:{new_color_hex}"
        
        parts = []
        found = False
        for stop_item in stops_str.split(';'):
            if not stop_item.strip():
                continue
            subparts = stop_item.split(':')
            if len(subparts) == 2:
                try:
                    offset = float(subparts[0].strip())
                    if abs(offset - target_offset) < 1e-5:
                        parts.append(f"{target_offset}:{new_color_hex}")
                        found = True
                    else:
                        parts.append(stop_item.strip())
                except ValueError:
                    parts.append(stop_item.strip())
            else:
                parts.append(stop_item.strip())
                
        if not found:
            if target_offset == 0.0:
                parts.insert(0, f"0.0:{new_color_hex}")
            elif target_offset == 1.0:
                parts.append(f"1.0:{new_color_hex}")
            else:
                parts.append(f"{target_offset}:{new_color_hex}")
                
        return "; ".join(parts)

    def extract_colors_from_stops_str(self, stops_str):
        if not stops_str:
            return None, None
        start_color_str = None
        end_color_str = None
        min_offset = 999.0
        max_offset = -999.0
        for stop_item in stops_str.split(';'):
            if not stop_item.strip():
                continue
            subparts = stop_item.split(':')
            if len(subparts) == 2:
                try:
                    offset = float(subparts[0].strip())
                    color_val = subparts[1].strip()
                    if offset < min_offset:
                        min_offset = offset
                        start_color_str = color_val
                    if offset > max_offset:
                        max_offset = offset
                        end_color_str = color_val
                except ValueError:
                    pass
        return start_color_str, end_color_str

    def on_grad_color_start_clicked(self):
        if self.current_item and not self._updating:
            old_color = getattr(self.current_item, 'grad_color_start', QColor(255, 255, 255))
            color = QColorDialog.getColor(old_color)
            if color.isValid() and color != old_color:
                self.document.undo_stack.beginMacro("Изменить начало градиента")
                try:
                    # 1. Обновляем базовый цвет
                    cmd1 = ChangePropertyCommand(self.current_item, 'grad_color_start', old_color, color)
                    self.document.push_command(cmd1)
                    
                    # 2. Синхронизируем со строкой Stops
                    old_stops = getattr(self.current_item, 'grad_stops', '')
                    new_stops = self.update_stop_color_in_str(old_stops, 0.0, color.name())
                    if old_stops != new_stops:
                        cmd2 = ChangePropertyCommand(self.current_item, 'grad_stops', old_stops, new_stops)
                        self.document.push_command(cmd2)
                finally:
                    self.document.undo_stack.endMacro()
                    
                self.update_from_item()

    def on_grad_color_end_clicked(self):
        if self.current_item and not self._updating:
            old_color = getattr(self.current_item, 'grad_color_end', QColor(0, 0, 0))
            color = QColorDialog.getColor(old_color)
            if color.isValid() and color != old_color:
                self.document.undo_stack.beginMacro("Изменить конец градиента")
                try:
                    # 1. Обновляем базовый цвет
                    cmd1 = ChangePropertyCommand(self.current_item, 'grad_color_end', old_color, color)
                    self.document.push_command(cmd1)
                    
                    # 2. Синхронизируем со строкой Stops
                    old_stops = getattr(self.current_item, 'grad_stops', '')
                    new_stops = self.update_stop_color_in_str(old_stops, 1.0, color.name())
                    if old_stops != new_stops:
                        cmd2 = ChangePropertyCommand(self.current_item, 'grad_stops', old_stops, new_stops)
                        self.document.push_command(cmd2)
                finally:
                    self.document.undo_stack.endMacro()
                    
                self.update_from_item()

    def on_grad_angle_changed(self):
        if self.current_item and not self._updating:
            old_angle = getattr(self.current_item, 'grad_angle', 0.0)
            new_angle = self.grad_angle_spin.value()
            if old_angle != new_angle:
                cmd = ChangePropertyCommand(self.current_item, 'grad_angle', old_angle, new_angle)
                self.document.push_command(cmd)

    def on_grad_radius_changed(self):
        if self.current_item and not self._updating:
            old_radius = getattr(self.current_item, 'grad_radius', 0.5)
            new_radius = self.grad_radius_spin.value()
            if old_radius != new_radius:
                cmd = ChangePropertyCommand(self.current_item, 'grad_radius', old_radius, new_radius)
                self.document.push_command(cmd)

    def on_grad_spread_changed(self, index):
        if self.current_item and not self._updating:
            spread_options = ['pad', 'reflect', 'repeat']
            new_spread = spread_options[index]
            old_spread = getattr(self.current_item, 'grad_spread', 'pad')
            if old_spread != new_spread:
                cmd = ChangePropertyCommand(self.current_item, 'grad_spread', old_spread, new_spread)
                self.document.push_command(cmd)

    def on_grad_stops_changed(self):
        if self.current_item and not self._updating:
            new_stops = self.grad_stops_edit.text()
            old_stops = getattr(self.current_item, 'grad_stops', '')
            if old_stops != new_stops:
                self.document.undo_stack.beginMacro("Изменить точки градиента")
                try:
                    cmd = ChangePropertyCommand(self.current_item, 'grad_stops', old_stops, new_stops)
                    self.document.push_command(cmd)
                    
                    # Синхронизируем базовые цвета с изменениями в Stops
                    start_c_str, end_c_str = self.extract_colors_from_stops_str(new_stops)
                    if start_c_str:
                        try:
                            color = QColor(start_c_str)
                            if color.isValid():
                                old_c_start = getattr(self.current_item, 'grad_color_start', QColor(255, 255, 255))
                                if old_c_start != color:
                                    self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_color_start', old_c_start, color))
                        except Exception:
                            pass
                    if end_c_str:
                        try:
                            color = QColor(end_c_str)
                            if color.isValid():
                                old_c_end = getattr(self.current_item, 'grad_color_end', QColor(0, 0, 0))
                                if old_c_end != color:
                                    self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_color_end', old_c_end, color))
                        except Exception:
                            pass
                finally:
                    self.document.undo_stack.endMacro()
                
                self.update_from_item()

    def on_grad_coords_changed(self):
        if self.current_item and not self._updating:
            old_x1 = getattr(self.current_item, 'grad_x1', 0.0)
            old_y1 = getattr(self.current_item, 'grad_y1', 0.0)
            old_x2 = getattr(self.current_item, 'grad_x2', 1.0)
            old_y2 = getattr(self.current_item, 'grad_y2', 0.0)
            
            new_x1 = self.grad_x1_spin.value()
            new_y1 = self.grad_y1_spin.value()
            new_x2 = self.grad_x2_spin.value()
            new_y2 = self.grad_y2_spin.value()
            
            if old_x1 != new_x1:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_x1', old_x1, new_x1))
            if old_y1 != new_y1:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_y1', old_y1, new_y1))
            if old_x2 != new_x2:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_x2', old_x2, new_x2))
            if old_y2 != new_y2:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_y2', old_y2, new_y2))

    def on_grad_radial_coords_changed(self):
        if self.current_item and not self._updating:
            old_cx = getattr(self.current_item, 'grad_cx', 0.5)
            old_cy = getattr(self.current_item, 'grad_cy', 0.5)
            old_r = getattr(self.current_item, 'grad_r', 0.5)
            old_fx = getattr(self.current_item, 'grad_fx', 0.5)
            old_fy = getattr(self.current_item, 'grad_fy', 0.5)
            
            new_cx = self.grad_cx_spin.value()
            new_cy = self.grad_cy_spin.value()
            new_r = self.grad_r_spin.value()
            new_fx = self.grad_fx_spin.value()
            new_fy = self.grad_fy_spin.value()
            
            if old_cx != new_cx:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_cx', old_cx, new_cx))
            if old_cy != new_cy:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_cy', old_cy, new_cy))
            if old_r != new_r:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_r', old_r, new_r))
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_radius', old_r, new_r))
            if old_fx != new_fx:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_fx', old_fx, new_fx))
            if old_fy != new_fy:
                self.document.push_command(ChangePropertyCommand(self.current_item, 'grad_fy', old_fy, new_fy))

    def on_shadow_enable_changed(self, state):
        if self.current_item and not self._updating:
            old_enable = getattr(self.current_item, 'shadow_enable', False)
            new_enable = (state == Qt.Checked)
            if old_enable != new_enable:
                cmd = ChangePropertyCommand(self.current_item, 'shadow_enable', old_enable, new_enable)
                self.document.push_command(cmd)

    def on_shadow_color_clicked(self):
        if self.current_item and not self._updating:
            old_color = getattr(self.current_item, 'shadow_color', QColor(0, 0, 0, 128))
            color = QColorDialog.getColor(old_color, None, "Выбрать цвет тени", QColorDialog.ShowAlphaChannel)
            if color.isValid() and color != old_color:
                cmd = ChangePropertyCommand(self.current_item, 'shadow_color', old_color, color)
                self.document.push_command(cmd)
                self.update_from_item()

    def on_shadow_params_changed(self):
        if self.current_item and not self._updating:
            old_blur = getattr(self.current_item, 'shadow_blur', 8.0)
            old_dx = getattr(self.current_item, 'shadow_dx', 4.0)
            old_dy = getattr(self.current_item, 'shadow_dy', 4.0)
            
            new_blur = self.shadow_blur_spin.value()
            new_dx = self.shadow_dx_spin.value()
            new_dy = self.shadow_dy_spin.value()
            
            has_changes = (old_blur != new_blur or old_dx != new_dx or old_dy != new_dy)
            if has_changes:
                self.document.undo_stack.beginMacro("Изменить параметры тени")
                try:
                    if old_blur != new_blur:
                        self.document.push_command(ChangePropertyCommand(self.current_item, 'shadow_blur', old_blur, new_blur))
                    if old_dx != new_dx:
                        self.document.push_command(ChangePropertyCommand(self.current_item, 'shadow_dx', old_dx, new_dx))
                    if old_dy != new_dy:
                        self.document.push_command(ChangePropertyCommand(self.current_item, 'shadow_dy', old_dy, new_dy))
                finally:
                    self.document.undo_stack.endMacro()
