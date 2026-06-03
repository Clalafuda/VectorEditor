import math
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QColor
from .base_item import VectorItem

class SafeEvaluator:
    SAFE_NAMES = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'abs': abs,
        'pow': pow,
        'pi': math.pi,
        'e': math.e,
    }

    def __init__(self, expr_lhs, expr_rhs=None):
        self.expr_lhs = self.prepare_expr(expr_lhs)
        self.expr_rhs = self.prepare_expr(expr_rhs) if expr_rhs else None
        
        try:
            self.code_lhs = compile(self.expr_lhs, '<string>', 'eval')
        except Exception:
            self.code_lhs = None
            
        try:
            self.code_rhs = compile(self.expr_rhs, '<string>', 'eval') if self.expr_rhs else None
        except Exception:
            self.code_rhs = None

    def prepare_expr(self, s):
        cleaned = s.replace('^', '**')
        return cleaned

    def eval_at(self, x, y):
        if not self.code_lhs:
            return float('nan')
        
        context = {'x': x, 'y': y, '__builtins__': None}
        context.update(self.SAFE_NAMES)
        
        try:
            val_lhs = eval(self.code_lhs, context)
            if self.code_rhs:
                val_rhs = eval(self.code_rhs, context)
                return float(val_lhs - val_rhs)
            else:
                return float(val_lhs)
        except Exception:
            return float('nan')

class FunctionItem(VectorItem):
    """Объект неявной функции / математического графика"""
    
    def __init__(self, rect=QRectF(-100, -100, 200, 200), expression="x^2 + y^2 = 25", parent=None):
        super().__init__(parent)
        self._rect = rect
        self._expression = expression
        self.name = "Function"
        
        # Math limits defaults
        self._x_min = -10.0
        self._x_max = 10.0
        self._y_min = -10.0
        self._y_max = 10.0
        
        # Cache for rendered segments
        self._cached_lines = []
        
        # Perform initial calculation
        self.recalculate()

    @property
    def rect(self):
        return self._rect
        
    @rect.setter
    def rect(self, value):
        self._rect = value
        self.recalculate()
        self.update()
        
    @property
    def expression(self):
        return self._expression
        
    @expression.setter
    def expression(self, value):
        self._expression = value
        self.recalculate()
        self.update()
        
    @property
    def x_min(self):
        return self._x_min
        
    @x_min.setter
    def x_min(self, value):
        self._x_min = float(value)
        self.recalculate()
        self.update()
        
    @property
    def x_max(self):
        return self._x_max
        
    @x_max.setter
    def x_max(self, value):
        self._x_max = float(value)
        self.recalculate()
        self.update()
        
    @property
    def y_min(self):
        return self._y_min
        
    @y_min.setter
    def y_min(self, value):
        self._y_min = float(value)
        self.recalculate()
        self.update()
        
    @property
    def y_max(self):
        return self._y_max
        
    @y_max.setter
    def y_max(self, value):
        self._y_max = float(value)
        self.recalculate()
        self.update()

    def recalculate(self):
        """Вычисляет линии неявной функции методом Marching Squares"""
        self._cached_lines = []
        
        expr = self._expression.strip()
        if not expr:
            return
            
        if '=' in expr:
            parts = expr.split('=', 1)
            lhs, rhs = parts[0].strip(), parts[1].strip()
        else:
            lhs, rhs = expr, None
            
        evaluator = SafeEvaluator(lhs, rhs)
        
        # Grid parameters - 60x60 grid is highly responsive and smooth
        rows = 60
        cols = 60
        
        rect = self._rect
        x_min, x_max = self._x_min, self._x_max
        y_min, y_max = self._y_min, self._y_max
        
        # Evaluate values on a grid
        val_grid = []
        for r in range(rows + 1):
            row_vals = []
            y_val = y_max - (r / rows) * (y_max - y_min)
            for c in range(cols + 1):
                x_val = x_min + (c / cols) * (x_max - x_min)
                val = evaluator.eval_at(x_val, y_val)
                row_vals.append(val)
            val_grid.append(row_vals)
            
        # Marching squares algorithm
        for r in range(rows):
            py0 = rect.top() + (r / rows) * rect.height()
            py1 = rect.top() + ((r + 1) / rows) * rect.height()
            for c in range(cols):
                px0 = rect.left() + (c / cols) * rect.width()
                px1 = rect.left() + ((c + 1) / cols) * rect.width()
                
                # Grid corners
                v0 = val_grid[r][c]      # Top-Left (px0, py0)
                v1 = val_grid[r][c+1]    # Top-Right (px1, py0)
                v2 = val_grid[r+1][c+1]  # Bottom-Right (px1, py1)
                v3 = val_grid[r+1][c]    # Bottom-Left (px0, py1)
                
                if math.isnan(v0) or math.isnan(v1) or math.isnan(v2) or math.isnan(v3):
                    continue
                    
                # Determine bitmask
                index = 0
                if v0 >= 0: index |= 8
                if v1 >= 0: index |= 4
                if v2 >= 0: index |= 2
                if v3 >= 0: index |= 1
                
                if index == 0 or index == 15:
                    continue
                    
                # Interpolation helper
                def lerp_pt(p1, p2, val1, val2):
                    if abs(val2 - val1) < 1e-9:
                        return QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
                    t = -val1 / (val2 - val1)
                    t = max(0.0, min(1.0, t))
                    return p1 + t * (p2 - p1)
                    
                pts = {}
                # Edge 0 (Top)
                if (v0 >= 0) != (v1 >= 0):
                    pts[0] = lerp_pt(QPointF(px0, py0), QPointF(px1, py0), v0, v1)
                # Edge 1 (Right)
                if (v1 >= 0) != (v2 >= 0):
                    pts[1] = lerp_pt(QPointF(px1, py0), QPointF(px1, py1), v1, v2)
                # Edge 2 (Bottom)
                if (v3 >= 0) != (v2 >= 0):
                    pts[2] = lerp_pt(QPointF(px0, py1), QPointF(px1, py1), v3, v2)
                # Edge 3 (Left)
                if (v0 >= 0) != (v3 >= 0):
                    pts[3] = lerp_pt(QPointF(px0, py0), QPointF(px0, py1), v0, v3)
                    
                # Connections
                connections = []
                if index == 1 or index == 14:
                    connections = [(2, 3)]
                elif index == 2 or index == 13:
                    connections = [(1, 2)]
                elif index == 3 or index == 12:
                    connections = [(1, 3)]
                elif index == 4 or index == 11:
                    connections = [(0, 1)]
                elif index == 5:
                    connections = [(0, 3), (1, 2)]
                elif index == 10:
                    connections = [(0, 1), (2, 3)]
                elif index == 6 or index == 9:
                    connections = [(0, 2)]
                elif index == 7 or index == 8:
                    connections = [(0, 3)]
                    
                for e1, e2 in connections:
                    if e1 in pts and e2 in pts:
                        self._cached_lines.append((pts[e1], pts[e2]))

    def boundingRect(self):
        margin = self.stroke_width / 2 + 1
        return self._rect.adjusted(-margin, -margin, margin, margin)
        
    def paint(self, painter, option, widget=None):
        # Draw bounding rectangle with very light dash line if selected
        if self.isSelected():
            painter.save()
            dash_pen = QPen(QColor(150, 150, 150), 1, Qt.DashLine)
            dash_pen.setCosmetic(True)
            painter.setPen(dash_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self._rect)
            painter.restore()
            
        super().paint(painter, option, widget)
        
        # Redraw all marching-squares computed lines
        for p1, p2 in self._cached_lines:
            painter.drawLine(p1, p2)
            
    def shape(self):
        path = QPainterPath()
        path.addRect(self._rect)
        return path