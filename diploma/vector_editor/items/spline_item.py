from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QColor, QBrush
from .base_item import VectorItem

def interpolate_cardinal_spline(A, B, C, D, T, t):
    """Интерполяция кубического сплайна (эрмитова кардинального) с натяжением T"""
    t2 = t * t
    t3 = t2 * t
    
    # Базисные функции Эрмита
    h00 = 2.0 * t3 - 3.0 * t2 + 1.0
    h10 = t3 - 2.0 * t2 + t
    h01 = -2.0 * t3 + 3.0 * t2
    h11 = t3 - t2
    
    # Касательные в точках B и C
    m0_x = T * (C.x() - A.x())
    m0_y = T * (C.y() - A.y())
    
    m1_x = T * (D.x() - B.x())
    m1_y = T * (D.y() - B.y())
    
    # Вычисление интерполированной точки
    x = h00 * B.x() + h10 * m0_x + h01 * C.x() + h11 * m1_x
    y = h00 * B.y() + h10 * m0_y + h01 * C.y() + h11 * m1_y
    
    return QPointF(x, y)


class SplineItem(VectorItem):
    """Сплайн-объект (Кардинальный сплайн Катмулла-Рома с регулируемым натяжением)"""
    
    def __init__(self, points=None, tension=0.5, closed=False, parent=None):
        super().__init__(parent)
        self._points = points if points else []
        self._tension = float(tension)
        self._closed = bool(closed)
        self.name = "Spline"
        
        # Кэшированный путь
        self._cached_path = QPainterPath()
        self._recalculate_path()

    @property
    def points(self):
        return self._points
        
    @points.setter
    def points(self, value):
        self._points = value
        self._recalculate_path()
        self.update()
        
    @property
    def tension(self):
        return self._tension
        
    @tension.setter
    def tension(self, value):
        self._tension = float(value)
        self._recalculate_path()
        self.update()
        
    @property
    def closed(self):
        return self._closed
        
    @closed.setter
    def closed(self, value):
        self._closed = bool(value)
        self._recalculate_path()
        self.update()

    def add_point(self, point):
        self._points.append(point)
        self._recalculate_path()
        self.update()
        
    def set_points(self, points):
        self._points = points
        self._recalculate_path()
        self.update()

    def _recalculate_path(self):
        """Перерасчет интерполированного сплайна"""
        path = QPainterPath()
        if len(self._points) < 2:
            if len(self._points) == 1:
                path.addEllipse(self._points[0], 2, 2)
            self._cached_path = path
            return
            
        pts = self._points
        n = len(pts)
        T = self._tension
        
        first_pt = True
        
        # Определяем диапазон прохода
        # Если сплайн замкнут, мы проходим n интервалов, зацикливая точки по модулю.
        # В противном случае мы проходим n - 1 интервал.
        intervals = n if self._closed else n - 1
        
        for i in range(intervals):
            # Соседние 4 контрольные точки для сегмента между B (i) и C (i+1)
            if self._closed:
                p0 = pts[(i - 1) % n]
                p1 = pts[i % n]
                p2 = pts[(i + 1) % n]
                p3 = pts[(i + 2) % n]
            else:
                p0 = pts[max(0, i - 1)]
                p1 = pts[i]
                p2 = pts[i + 1]
                p3 = pts[min(n - 1, i + 2)]
                
            steps = 20
            start_step = 0 if first_pt else 1
            for step in range(start_step, steps + 1):
                t = step / steps
                interp_pt = interpolate_cardinal_spline(p0, p1, p2, p3, T, t)
                if first_pt and step == 0:
                    path.moveTo(interp_pt)
                    first_pt = False
                else:
                    path.lineTo(interp_pt)
                    
        if self._closed:
            path.closeSubpath()
            
        self._cached_path = path

    def boundingRect(self):
        if not self._points:
            return QRectF()
            
        # Возвращаем bounding box пути сплайна (включая контур)
        margin = self.stroke_width / 2 + 5
        return self._cached_path.boundingRect().adjusted(-margin, -margin, margin, margin)
        
    def paint(self, painter, option, widget=None):
        # Рисуем управляющий многоугольник и маркеры точек, если сплайн выделен
        if self.isSelected() and len(self._points) > 1:
            painter.save()
            poly_pen = QPen(QColor(120, 120, 120, 150), 1, Qt.DashLine)
            poly_pen.setCosmetic(True)
            painter.setPen(poly_pen)
            painter.setBrush(Qt.NoBrush)
            for i in range(len(self._points) - 1):
                painter.drawLine(self._points[i], self._points[i + 1])
            if self._closed and len(self._points) > 2:
                painter.drawLine(self._points[-1], self._points[0])
                
            # Рисуем маркеры узлов сплайна
            handle_pen = QPen(QColor(0, 100, 255), 1)
            handle_pen.setCosmetic(True)
            painter.setPen(handle_pen)
            painter.setBrush(QColor(200, 225, 255))
            for pt in self._points:
                painter.drawEllipse(pt, 3.5, 3.5)
            painter.restore()
            
        super().paint(painter, option, widget)
        # Отрисовываем сам закешированный путь сплайна
        painter.drawPath(self._cached_path)
        
    def shape(self):
        return self._cached_path