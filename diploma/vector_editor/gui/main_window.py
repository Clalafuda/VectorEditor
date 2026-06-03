from PyQt5.QtWidgets import (QMainWindow, QToolBar, QAction, 
                             QStatusBar, QVBoxLayout, QWidget, QActionGroup)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence

from ..core.document import Document

from ..tools.tool_manager import ToolManager
from ..tools.selection_tool import SelectionTool
from ..tools.rectangle_tool import RectangleTool
from ..tools.ellipse_tool import EllipseTool
from ..tools.line_tool import LineTool
from ..tools.polyline_tool import PolylineTool  
from ..tools.polygon_tool import PolygonTool    
from ..tools.function_tool import FunctionTool
from ..tools.spline_tool import SplineTool

from .scene import Scene
from .scene_view import SceneView
from .properties_dock import PropertiesDock
from ..items.group_item import GroupItem
from ..gui.layers_dock import LayersDock
class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Создание документа
        self.document = Document()
        
        # Создание менеджера инструментов
        self.tool_manager = ToolManager(self.document)
        
        # Создание сцены и представления
        self.scene = Scene(self.document)
        self.view = SceneView(self.scene, self.tool_manager)
        self.scene.set_view(self.view)
        
        # Настройка интерфейса
        self.init_ui()
        self.create_tools()
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")

        self.properties_dock = PropertiesDock(self.document)
        self.document.undo_stack.indexChanged.connect(self.properties_dock.update_from_item)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Vector Editor")
        self.setGeometry(100, 100, 1024, 768)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        central_widget.setLayout(layout)
        
    def create_tools(self):
        """Создание инструментов"""
        # Регистрация инструментов
        self.tool_manager.register_tool('select', SelectionTool(self.document))
        self.tool_manager.register_tool('rectangle', RectangleTool(self.document))
        self.tool_manager.register_tool('ellipse', EllipseTool(self.document))
        self.tool_manager.register_tool('line', LineTool(self.document))
        self.tool_manager.register_tool('polyline', PolylineTool(self.document))
        self.tool_manager.register_tool('polygon', PolygonTool(self.document))
        self.tool_manager.register_tool('function', FunctionTool(self.document))
        self.tool_manager.register_tool('spline', SplineTool(self.document))
        # Установка инструмента по умолчанию
        self.tool_manager.set_active_tool('select')
        
    def create_actions(self):
        """Создание действий"""
        # Инструменты
        self.select_action = QAction("Выделение", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True)
        self.select_action.triggered.connect(lambda: self.tool_manager.set_active_tool('select'))
        
        self.rectangle_action = QAction("Прямоугольник", self)
        self.rectangle_action.setCheckable(True)
        self.rectangle_action.triggered.connect(lambda: self.tool_manager.set_active_tool('rectangle'))
        
        self.ellipse_action = QAction("Эллипс", self)
        self.ellipse_action.setCheckable(True)
        self.ellipse_action.triggered.connect(lambda: self.tool_manager.set_active_tool('ellipse'))
        
        self.line_action = QAction("Линия", self)
        self.line_action.setCheckable(True)
        self.line_action.triggered.connect(lambda: self.tool_manager.set_active_tool('line'))
        
        self.polyline_action = QAction("Ломаная", self)
        self.polyline_action.setCheckable(True)
        self.polyline_action.triggered.connect(lambda: self.tool_manager.set_active_tool('polyline'))
        
        self.polygon_action = QAction("Многоугольник", self)
        self.polygon_action.setCheckable(True)
        self.polygon_action.triggered.connect(lambda: self.tool_manager.set_active_tool('polygon'))
        
        self.function_action = QAction("Функция", self)
        self.function_action.setCheckable(True)
        self.function_action.triggered.connect(lambda: self.tool_manager.set_active_tool('function'))

        self.spline_action = QAction("Сплайн", self)
        self.spline_action.setCheckable(True)
        self.spline_action.triggered.connect(lambda: self.tool_manager.set_active_tool('spline'))

        # Группа действий для инструментов
        self.tool_group = QActionGroup(self)
        self.tool_group.addAction(self.select_action)
        self.tool_group.addAction(self.rectangle_action)
        self.tool_group.addAction(self.ellipse_action)
        self.tool_group.addAction(self.line_action)
        self.tool_group.addAction(self.polyline_action)
        self.tool_group.addAction(self.polygon_action)
        self.tool_group.addAction(self.function_action)
        self.tool_group.addAction(self.spline_action)
        
        # Файл
        self.new_action = QAction("Новый", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_document)

        self.import_svg_action = QAction("Импорт SVG...", self)
        self.import_svg_action.setShortcut("Ctrl+I")
        self.import_svg_action.triggered.connect(self.import_svg)

        self.export_svg_action = QAction("Экспорт SVG...", self)
        self.export_svg_action.setShortcut("Ctrl+E")
        self.export_svg_action.triggered.connect(self.export_svg)

        self.export_bitmap_action = QAction("Экспорт в растр (PNG/JPEG)...", self)
        self.export_bitmap_action.setShortcut("Ctrl+Shift+E")
        self.export_bitmap_action.triggered.connect(self.export_bitmap)
        
        self.quit_action = QAction("Выход", self)
        self.quit_action.setShortcut(QKeySequence.Quit)
        self.quit_action.triggered.connect(self.close)
        
        # Вид
        self.zoom_in_action = QAction("Увеличить", self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        
        self.zoom_out_action = QAction("Уменьшить", self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        
        self.zoom_fit_action = QAction("По размеру окна", self)
        self.zoom_fit_action.triggered.connect(self.zoom_fit)

        # Undo/Redo
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.document.undo)

        self.redo_action = QAction("Повторить", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.document.redo)

        # Обновление состояния кнопок
        self.document.undo_stack.canUndoChanged.connect(self.undo_action.setEnabled)
        self.document.undo_stack.canRedoChanged.connect(self.redo_action.setEnabled)
        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        
        #Группировка
        # В create_actions()
        self.group_action = QAction("Сгруппировать", self)
        self.group_action.setShortcut("Ctrl+G")
        self.group_action.triggered.connect(self.on_group)

        self.ungroup_action = QAction("Разгруппировать", self)
        self.ungroup_action.setShortcut("Ctrl+Shift+G")
        self.ungroup_action.triggered.connect(self.on_ungroup)

         # Панель слоёв
        self.layers_dock = LayersDock(self.document, self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layers_dock)
        self.document.layers_changed.connect(self.layers_dock._update_layers)
        self.document.active_layer_changed.connect(self.layers_dock._select_item_for_layer)
        self.document.selection_changed.connect(self.scene.update_selection) # Assuming Scene has update_selection method
        self.document.selection_changed.connect(self.layers_dock._select_item_in_tree) # Connect to update LayersDock selection
        
    def create_menus(self):
        """Создание меню"""
        # Меню "Файл"
        file_menu = self.menuBar().addMenu("&Файл")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.import_svg_action)
        file_menu.addAction(self.export_svg_action)
        file_menu.addAction(self.export_bitmap_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)
        
        # Меню "Инструменты"
        tools_menu = self.menuBar().addMenu("&Инструменты")
        tools_menu.addAction(self.select_action)
        tools_menu.addAction(self.rectangle_action)
        tools_menu.addAction(self.ellipse_action)
        tools_menu.addAction(self.line_action)
        tools_menu.addAction(self.polyline_action)
        tools_menu.addAction(self.polygon_action)
        tools_menu.addAction(self.function_action)
        tools_menu.addAction(self.spline_action)
        
        # Меню "Вид"
        view_menu = self.menuBar().addMenu("&Вид")
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.zoom_fit_action)

        # Меню "Правка"
        edit_menu = self.menuBar().addMenu("&Правка")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

        #Меню Объект
        obj_menu = self.menuBar().addMenu("&Объект")
        obj_menu.addAction(self.group_action)
        obj_menu.addAction(self.ungroup_action)
        
    def create_toolbars(self):
        """Создание панелей инструментов"""
        # Панель инструментов
        toolbar = self.addToolBar("Инструменты")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.addAction(self.select_action)
        toolbar.addAction(self.rectangle_action)
        toolbar.addAction(self.ellipse_action)
        toolbar.addAction(self.line_action)
        toolbar.addAction(self.polyline_action)
        toolbar.addAction(self.polygon_action)
        toolbar.addAction(self.function_action)
        toolbar.addAction(self.spline_action)

        # Панель правки
        edit_toolbar = self.addToolBar("Правка")
        edit_toolbar.addAction(self.undo_action)
        edit_toolbar.addAction(self.redo_action)
        
    def new_document(self):
        """Создание нового документа"""
        self.document.clear()
        self.scene.update_scene()
        self.statusBar().showMessage("Новый документ создан")

    def import_svg(self):
        """Импорт векторного SVG файла"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from ..core.svg_io import SvgSerializer
        filepath, _ = QFileDialog.getOpenFileName(self, "Импорт SVG", "", "SVG файлы (*.svg)")
        if filepath:
            success = SvgSerializer.import_from_svg(filepath, self.document)
            if success:
                self.scene.update_scene()
                self.properties_dock.update_from_item()
                self.statusBar().showMessage(f"Файл {filepath} импортирован")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось разобрать SVG файл")

    def export_svg(self):
        """Экспорт документа в векторный SVG файл"""
        from PyQt5.QtWidgets import QFileDialog
        from ..core.svg_io import SvgSerializer
        filepath, _ = QFileDialog.getSaveFileName(self, "Экспорт SVG", "", "SVG файлы (*.svg)")
        if filepath:
            if not filepath.endswith(".svg"):
                filepath += ".svg"
            SvgSerializer.export_to_svg(self.document, filepath)
            self.statusBar().showMessage(f"Документ сохранен в {filepath}")

    def export_bitmap(self):
        """Экспорт документа в растровые форматы PNG или JPEG"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from PyQt5.QtGui import QImage, QPainter
        from PyQt5.QtCore import QRectF
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Экспорт в растр", "", "PNG рисунок (*.png);;JPEG рисунок (*.jpg *.jpeg)"
        )
        if filepath:
            # Расширение по умолчанию
            if "png" in selected_filter.lower():
                if not filepath.lower().endswith(".png"):
                    filepath += ".png"
                fmt = "PNG"
            else:
                if not (filepath.lower().endswith(".jpg") or filepath.lower().endswith(".jpeg")):
                    filepath += ".jpg"
                fmt = "JPEG"

            # Ограничиваем область рендеринга границами сцены или объектов
            items_rect = self.scene.itemsBoundingRect()
            if items_rect.isEmpty():
                items_rect = QRectF(0, 0, 800, 600)
            else:
                items_rect = items_rect.adjusted(-10, -10, 10, 10) # отступы

            # Создаем QImage
            image = QImage(int(items_rect.width()), int(items_rect.height()), QImage.Format_ARGB32)
            if fmt == "JPEG":
                image.fill(Qt.white)
            else:
                image.fill(Qt.transparent)

            # Временно отключаем сетку во время экспорта
            was_grid_shown = getattr(self.scene, 'show_grid', True)
            self.scene.show_grid = False

            # Отрисовываем сцену на QImage
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Маппим область сцены на весь размер картинки
            self.scene.render(painter, QRectF(image.rect()), items_rect)
            painter.end()

            # Восстанавливаем видимость сетки
            self.scene.show_grid = was_grid_shown

            # Сохранение
            if image.save(filepath, fmt):
                self.statusBar().showMessage(f"Изображение экспортировано в {filepath}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить растровое изображение")
        
    def zoom_in(self):
        """Увеличение масштаба"""
        self.view.scale(1.2, 1.2)
        self.view.scale_factor *= 1.2
        
    def zoom_out(self):
        """Уменьшение масштаба"""
        self.view.scale(1/1.2, 1/1.2)
        self.view.scale_factor /= 1.2
        
    def zoom_fit(self):
        """Масштабировать по размеру окна"""
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.scale_factor = 1.0

    def on_group(self):
        """Сгруппировать выделенные объекты"""
        selected = self.document.selected_items
        if len(selected) >= 2:
            self.document.group_items(selected)

    def on_ungroup(self):
        """Разгруппировать выделенный объект"""
        selected = self.document.selected_items
        if len(selected) == 1 and isinstance(selected[0], GroupItem):
            self.document.ungroup_items(selected[0])    