from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor

class VectorItem(QGraphicsItem):
    """Базовый класс для всех векторных объектов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Базовые свойства
        self.stroke_color = QColor(0, 0, 0)  # Черный
        self.fill_color = QColor(255, 255, 255, 0)  # Прозрачный
        self.stroke_width = 1.0
        
        # Свойства градиента
        self.fill_type = "solid"  # "solid", "linear", "radial"
        self.grad_color_start = QColor(255, 255, 255)
        self.grad_color_end = QColor(0, 0, 0)
        self.grad_angle = 0.0
        self.grad_radius = 0.5
        
        # Свойства тени уровня SVG (drop-shadow filter)
        self.shadow_enable = False
        self.shadow_blur = 8.0
        self.shadow_dx = 4.0
        self.shadow_dy = 4.0
        self.shadow_color = QColor(0, 0, 0, 128)
        
        # Расширенные свойства градиента уровня SVG
        self.grad_stops = "0.0:#ffffff; 1.0:#000000"  # Строка цветовых точек: "offset:color; ..."
        self.grad_spread = "pad"  # "pad", "reflect", "repeat"
        
        # Относительные координаты (ObjectBoundingMode)
        self.grad_x1 = 0.0
        self.grad_y1 = 0.0
        self.grad_x2 = 1.0
        self.grad_y2 = 0.0
        
        self.grad_cx = 0.5
        self.grad_cy = 0.5
        self.grad_r = 0.5
        self.grad_fx = 0.5
        self.grad_fy = 0.5
        
        # Флаги интерактивности
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Обрезка (ClipPath/Multiple ClipPaths)
        self._clip_paths = []
        self._clip_targets = []
        self.clip_mode = "and"  # "and" (пересечение/intersected), "or" (объединение/united)

        # Метаданные
        self.name = "Vector Item"

    def set_clip_paths(self, clip_list):
        # Очищаем старые связи
        for old_clip in list(getattr(self, '_clip_paths', [])):
            if old_clip not in clip_list:
                if hasattr(old_clip, '_clip_targets') and self in old_clip._clip_targets:
                    old_clip._clip_targets.remove(self)
        
        # Записываем новый список
        self._clip_paths = list(clip_list)
        
        # Настраиваем новые связи
        for new_clip in self._clip_paths:
            if not hasattr(new_clip, '_clip_targets'):
                new_clip._clip_targets = []
            if self not in new_clip._clip_targets:
                new_clip._clip_targets.append(self)
                
        self.update()

    def get_clip_paths(self):
        return getattr(self, '_clip_paths', [])

    clip_paths = property(get_clip_paths, set_clip_paths)

    def set_clip_path(self, clip_path):
        if clip_path:
            self.set_clip_paths([clip_path])
        else:
            self.set_clip_paths([])
            
    def get_clip_path(self):
        paths = getattr(self, '_clip_paths', [])
        return paths[0] if paths else None

    clip_path = property(get_clip_path, set_clip_path)

    def update_shadow_effect(self):
        """Обновляет эффект падающей тени объекта"""
        if getattr(self, 'shadow_enable', False):
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            effect = self.graphicsEffect()
            if not isinstance(effect, QGraphicsDropShadowEffect):
                effect = QGraphicsDropShadowEffect()
                self.setGraphicsEffect(effect)
            effect.setBlurRadius(getattr(self, 'shadow_blur', 8.0))
            effect.setOffset(getattr(self, 'shadow_dx', 4.0), getattr(self, 'shadow_dy', 4.0))
            effect.setColor(getattr(self, 'shadow_color', QColor(0, 0, 0, 128)))
        else:
            self.setGraphicsEffect(None)

    def boundingRect(self):
        """Должен быть переопределен в дочерних классах"""
        return QRectF()
    
    def paint(self, painter, option, widget=None):
        """Базовая отрисовка - настраивает перо и кисть"""
        # Применяем все clip-paths в зависимости от режима ("и" / "или")
        clip_paths = getattr(self, '_clip_paths', [])
        if clip_paths:
            clip_mode = getattr(self, 'clip_mode', 'and')
            if clip_mode == 'or':
                from PyQt5.QtGui import QPainterPath
                combined_path = QPainterPath()
                first = True
                for clip_item in clip_paths:
                    try:
                        mapped_path = self.mapFromItem(clip_item, clip_item.shape())
                        if first:
                            combined_path = mapped_path
                            first = False
                        else:
                            combined_path = combined_path.united(mapped_path)
                    except Exception as e:
                        print(f"Error applying clip path union: {e}")
                painter.setClipPath(combined_path, Qt.IntersectClip)
            else:
                # Режим "and" (Пересечение)
                for clip_item in clip_paths:
                    try:
                        # Маппим shape обтравочного контура в локальную систему координат данного объекта
                        mapped_path = self.mapFromItem(clip_item, clip_item.shape())
                        painter.setClipPath(mapped_path, Qt.IntersectClip)
                    except Exception as e:
                        print(f"Error applying clip path intersection: {e}")

        # Настройка пера (контур)
        pen = QPen(self.stroke_color, self.stroke_width)
        if (self.isSelected()):
            pen.setColor(QColor(0, 100, 255))  # Синий контур
            pen.setWidth(int(self.stroke_width + 2))  # Чуть толще
        

        pen.setCosmetic(True)  # Толщина не зависит от масштаба
        painter.setPen(pen)
        
            
        # Настройка кисти (заливка с поддержкой расширенных градиентов SVG)
        fill_type = getattr(self, 'fill_type', 'solid')
        if fill_type == 'solid':
            brush = QBrush(self.fill_color)
        elif fill_type in ('linear', 'radial'):
            from PyQt5.QtGui import QLinearGradient, QRadialGradient, QGradient
            from PyQt5.QtCore import QPointF
            
            # 1. Инициализация геометрии
            if fill_type == 'linear':
                # Если координаты дефолтные и задан угол, вычисляем его
                x1 = getattr(self, 'grad_x1', 0.0)
                y1 = getattr(self, 'grad_y1', 0.0)
                x2 = getattr(self, 'grad_x2', 1.0)
                y2 = getattr(self, 'grad_y2', 0.0)
                angle = getattr(self, 'grad_angle', 0.0)
                
                # Если координаты по умолчанию, но угол изменен, используем угол
                if x1 == 0.0 and y1 == 0.0 and x2 == 1.0 and y2 == 0.0 and angle != 0.0:
                    import math
                    theta = math.radians(angle)
                    dx = math.cos(theta) * 0.5
                    dy = math.sin(theta) * 0.5
                    grad = QLinearGradient(QPointF(0.5 - dx, 0.5 - dy), QPointF(0.5 + dx, 0.5 + dy))
                else:
                    grad = QLinearGradient(QPointF(x1, y1), QPointF(x2, y2))
            else: # radial
                cx = getattr(self, 'grad_cx', 0.5)
                cy = getattr(self, 'grad_cy', 0.5)
                r = getattr(self, 'grad_r', getattr(self, 'grad_radius', 0.5))
                fx = getattr(self, 'grad_fx', cx)
                fy = getattr(self, 'grad_fy', cy)
                grad = QRadialGradient(QPointF(cx, cy), r, QPointF(fx, fy))
                
            grad.setCoordinateMode(QGradient.ObjectBoundingMode)
            
            # 2. Настройка распространения (Spread)
            spread_str = getattr(self, 'grad_spread', 'pad')
            if spread_str == 'reflect':
                grad.setSpread(QGradient.ReflectSpread)
            elif spread_str == 'repeat':
                grad.setSpread(QGradient.RepeatSpread)
            else:
                grad.setSpread(QGradient.PadSpread)
                
            # 3. Парсинг цветовых точек Stops
            stops_str = getattr(self, 'grad_stops', '').strip()
            stops_set = False
            if stops_str:
                try:
                    for stop_item in stops_str.split(';'):
                        if not stop_item:
                            continue
                        parts = stop_item.split(':')
                        if len(parts) == 2:
                            offset = float(parts[0].strip())
                            color_val = parts[1].strip()
                            grad.setColorAt(max(0.0, min(1.0, offset)), QColor(color_val))
                    stops_set = True
                except Exception:
                    pass
                    
            if not stops_set:
                # Фолбэк на базовую двухцветную модель
                grad.setColorAt(0.0, getattr(self, 'grad_color_start', QColor(255, 255, 255)))
                grad.setColorAt(1.0, getattr(self, 'grad_color_end', QColor(0, 0, 0)))
                
            brush = QBrush(grad)
        else:
            brush = QBrush(self.fill_color)
            
        painter.setBrush(brush)
        
    def itemChange(self, change, value):
        """Обработка изменений объекта"""
        if change in (QGraphicsItem.ItemPositionHasChanged, QGraphicsItem.ItemTransformHasChanged, QGraphicsItem.ItemPositionChange):
            # Если мы являемся clip_path для других объектов, оповещаем их об изменении геометрии
            for target in getattr(self, '_clip_targets', []):
                target.update()
        return super().itemChange(change, value)
