import re
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QPainterPath

from ..items.layer_item import LayerItem
from ..items.group_item import GroupItem
from ..items.shape_items import RectangleItem, EllipseItem
from ..items.line_item import LineItem
from ..items.polyline_item import PolylineItem
from ..items.polygon_item import PolygonItem
from ..items.spline_item import SplineItem
from ..items.function_item import FunctionItem

def painter_path_to_svg_d(path):
    """Преобразует QPainterPath в строку команд SVG d="..." """
    d_parts = []
    i = 0
    n = path.elementCount()
    while i < n:
        el = path.elementAt(i)
        if el.type == QPainterPath.MoveToElement:
            d_parts.append(f"M {el.x:.2f} {el.y:.2f}")
            i += 1
        elif el.type == QPainterPath.LineToElement:
            d_parts.append(f"L {el.x:.2f} {el.y:.2f}")
            i += 1
        elif el.type == QPainterPath.CurveToElement:
            if i + 2 < n:
                el2 = path.elementAt(i+1)
                el3 = path.elementAt(i+2)
                d_parts.append(f"C {el.x:.2f} {el.y:.2f}, {el2.x:.2f} {el2.y:.2f}, {el3.x:.2f} {el3.y:.2f}")
                i += 3
            else:
                i += 1
        else:
            i += 1
    return " ".join(d_parts)

def parse_svg_d_to_path(d_str):
    """Упрощенный парсер SVG d струны обратно в QPainterPath"""
    path = QPainterPath()
    # Регулярное выражение для извлечения команд и чисел
    tokens = re.findall(r'([MLCmlc])|([-+]?\d*\.\d+|[-+]?\d+)', d_str)
    
    cmd = None
    coords = []
    
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t[0]:  # Команда
            cmd = t[0]
            coords = []
            i += 1
        else:  # Координата
            coords.append(float(t[1]))
            i += 1
            
        if cmd == 'M' and len(coords) >= 2:
            path.moveTo(coords[0], coords[1])
            coords = coords[2:]
        elif cmd == 'L' and len(coords) >= 2:
            path.lineTo(coords[0], coords[1])
            coords = coords[2:]
        elif cmd == 'C' and len(coords) >= 6:
            path.cubicTo(coords[0], coords[1], coords[2], coords[3], coords[4], coords[5])
            coords = coords[6:]
            
    return path

class SvgSerializer:
    @staticmethod
    def export_to_svg(document, filepath):
        """Экспорт текущего документа в файл формата SVG"""
        root = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:custom": "http://vector.editor/custom",
            "width": "800",
            "height": "600",
            "viewBox": "0 0 800 600"
        })
        
        defs = ET.SubElement(root, "defs")
        
        # Списки для связей градиентов/теней/обрезки
        grad_counter = 0
        shadow_counter = 0
        
        # Вспомогательный метод для сохранения кисти (заливки)
        def process_fill(item, elem):
            nonlocal grad_counter
            fill_type = getattr(item, 'fill_type', 'solid')
            if fill_type == 'solid':
                color = getattr(item, 'fill_color', QColor(255, 255, 255, 0))
                if color.alpha() == 0:
                    elem.set("fill", "none")
                else:
                    elem.set("fill", color.name())
                    if color.alpha() < 255:
                        elem.set("fill-opacity", f"{color.alpha() / 255.0:.2f}")
            elif fill_type in ('linear', 'radial'):
                grad_counter += 1
                grad_id = f"grad_{grad_counter}"
                
                # Читаем св-ва градиента
                stops_str = getattr(item, 'grad_stops', "0.0:#ffffff; 1.0:#000000")
                spread_mode = getattr(item, 'grad_spread', "pad")
                
                if fill_type == 'linear':
                    x1 = getattr(item, 'grad_x1', 0.0)
                    y1 = getattr(item, 'grad_y1', 0.0)
                    x2 = getattr(item, 'grad_x2', 1.0)
                    y2 = getattr(item, 'grad_y2', 0.0)
                    grad_elem = ET.SubElement(defs, "linearGradient", {
                        "id": grad_id,
                        "x1": f"{x1:.2f}", "y1": f"{y1:.2f}",
                        "x2": f"{x2:.2f}", "y2": f"{y2:.2f}",
                        "spreadMethod": "reflect" if spread_mode == "reflect" else ("repeat" if spread_mode == "repeat" else "pad")
                    })
                else:
                    cx = getattr(item, 'grad_cx', 0.5)
                    cy = getattr(item, 'grad_cy', 0.5)
                    r = getattr(item, 'grad_r', 0.5)
                    fx = getattr(item, 'grad_fx', cx)
                    fy = getattr(item, 'grad_fy', cy)
                    grad_elem = ET.SubElement(defs, "radialGradient", {
                        "id": grad_id,
                        "cx": f"{cx:.2f}", "cy": f"{cy:.2f}",
                        "r": f"{r:.2f}",
                        "fx": f"{fx:.2f}", "fy": f"{fy:.2f}",
                        "spreadMethod": "reflect" if spread_mode == "reflect" else ("repeat" if spread_mode == "repeat" else "pad")
                    })
                
                # Парсим stops
                for stop_item in stops_str.split(';'):
                    if not stop_item.strip():
                        continue
                    parts = stop_item.split(':')
                    if len(parts) == 2:
                        try:
                            offset = float(parts[0].strip()) * 100
                            col_val = parts[1].strip()
                            ET.SubElement(grad_elem, "stop", {
                                "offset": f"{offset:.1f}%",
                                "stop-color": col_val
                            })
                        except ValueError:
                            pass
                
                elem.set("fill", f"url(#{grad_id})")
                # Для совместимости запишем базовые цвета в custom
                elem.set("custom:grad_color_start", getattr(item, 'grad_color_start', QColor(255,255,255)).name())
                elem.set("custom:grad_color_end", getattr(item, 'grad_color_end', QColor(0,0,0)).name())
                elem.set("custom:grad_angle", f"{getattr(item, 'grad_angle', 0.0):.2f}")
                elem.set("custom:grad_radius", f"{getattr(item, 'grad_radius', 0.5):.2f}")
                elem.set("custom:grad_stops", stops_str)
                elem.set("custom:grad_spread", spread_mode)
                elem.set("custom:fill_type", fill_type)
        
        # Вспомогательный метод для сохранения тени
        def process_shadow(item, elem):
            nonlocal shadow_counter
            if getattr(item, 'shadow_enable', False):
                shadow_counter += 1
                filter_id = f"shadow_{shadow_counter}"
                blur = getattr(item, 'shadow_blur', 8.0)
                dx = getattr(item, 'shadow_dx', 4.0)
                dy = getattr(item, 'shadow_dy', 4.0)
                color = getattr(item, 'shadow_color', QColor(0, 0, 0, 128))
                
                filter_elem = ET.SubElement(defs, "filter", {
                    "id": filter_id,
                    "x": "-30%", "y": "-30%",
                    "width": "160%", "height": "160%"
                })
                
                opacity = color.alpha() / 255.0
                ET.SubElement(filter_elem, "feDropShadow", {
                    "dx": f"{dx:.2f}", "dy": f"{dy:.2f}",
                    "stdDeviation": f"{blur / 2.0:.2f}",
                    "flood-color": color.name(),
                    "flood-opacity": f"{opacity:.2f}"
                })
                
                elem.set("filter", f"url(#{filter_id})")
                
                # Доп. метаданные для точного восстановления альфа-канала тени в Qt
                elem.set("custom:shadow_enable", "True")
                elem.set("custom:shadow_blur", f"{blur:.2f}")
                elem.set("custom:shadow_dx", f"{dx:.2f}")
                elem.set("custom:shadow_dy", f"{dy:.2f}")
                elem.set("custom:shadow_color", f"{color.name()}:{color.alpha()}")

        # Вспомогательный метод для сохранения обрезки
        def process_clips(item, elem):
            clips = getattr(item, '_clip_paths', [])
            if clips:
                # Записываем custom ID для восстановления в редакторе
                clip_ids = [f"item_{id(c)}" for c in clips]
                elem.set("custom:clip_paths", ",".join(clip_ids))
                elem.set("custom:clip_mode", getattr(item, 'clip_mode', 'and'))
                
                # Пытаемся сформировать нативную отрисовку SVG clipPath
                # SVG стандартный клип накладывается через ID
                clip_path_id = f"clip_{id(item)}"
                clip_path_elem = ET.SubElement(defs, "clipPath", {"id": clip_path_id})
                
                for clip_item in clips:
                    sub_path = clip_item.shape()
                    mapped = item.mapFromItem(clip_item, sub_path)
                    d_str = painter_path_to_svg_d(mapped)
                    ET.SubElement(clip_path_elem, "path", {"d": d_str})
                
                elem.set("clip-path", f"url(#{clip_path_id})")

        # Вспомогательный метод для добавления общих графических параметров
        def apply_common_props(item, elem):
            elem.set("id", f"item_{id(item)}")
            elem.set("custom:name", getattr(item, 'name', 'Vector Item'))
            
            # Контур (stroke)
            stroke_col = getattr(item, 'stroke_color', QColor(0,0,0))
            elem.set("stroke", stroke_col.name())
            if stroke_col.alpha() < 255:
                elem.set("stroke-opacity", f"{stroke_col.alpha() / 255.0:.2f}")
            elem.set("stroke-width", f"{getattr(item, 'stroke_width', 1.0):.2f}")
            
            # Трансформации
            transform_parts = []
            pos = item.pos()
            if pos.x() != 0.0 or pos.y() != 0.0:
                transform_parts.append(f"translate({pos.x():.2f}, {pos.y():.2f})")
            rot = item.rotation()
            if rot != 0.0:
                transform_parts.append(f"rotate({rot:.2f})")
            scale = item.scale()
            if scale != 1.0:
                transform_parts.append(f"scale({scale:.2f})")
                
            if transform_parts:
                elem.set("transform", " ".join(transform_parts))
                
            process_fill(item, elem)
            process_shadow(item, elem)
            process_clips(item, elem)

        def serialize_item(item, parent_elem):
            if isinstance(item, RectangleItem):
                rect = item.rect
                elem = ET.SubElement(parent_elem, "rect", {
                    "x": f"{rect.x():.2f}",
                    "y": f"{rect.y():.2f}",
                    "width": f"{rect.width():.2f}",
                    "height": f"{rect.height():.2f}"
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, EllipseItem):
                rect = item.rect
                cx = rect.x() + rect.width() / 2.0
                cy = rect.y() + rect.height() / 2.0
                rx = rect.width() / 2.0
                ry = rect.height() / 2.0
                elem = ET.SubElement(parent_elem, "ellipse", {
                    "cx": f"{cx:.2f}",
                    "cy": f"{cy:.2f}",
                    "rx": f"{rx:.2f}",
                    "ry": f"{ry:.2f}"
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, LineItem):
                elem = ET.SubElement(parent_elem, "line", {
                    "x1": f"{item.start.x():.2f}", "y1": f"{item.start.y():.2f}",
                    "x2": f"{item.end.x():.2f}", "y2": f"{item.end.y():.2f}"
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, PolylineItem):
                pts_str = " ".join(f"{p.x():.2f},{p.y():.2f}" for p in item.points)
                elem = ET.SubElement(parent_elem, "polyline", {
                    "points": pts_str
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, PolygonItem):
                pts_str = " ".join(f"{p.x():.2f},{p.y():.2f}" for p in item.points)
                elem = ET.SubElement(parent_elem, "polygon", {
                    "points": pts_str
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, SplineItem):
                pts_str = " ".join(f"{p.x():.2f},{p.y():.2f}" for p in item.points)
                elem = ET.SubElement(parent_elem, "path", {
                    "d": painter_path_to_svg_d(item._cached_path),
                    "custom:type": "spline",
                    "custom:spline_points": pts_str,
                    "custom:spline_tension": f"{item.tension:.2f}",
                    "custom:spline_closed": str(item.closed)
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, FunctionItem):
                rect = item.rect
                elem = ET.SubElement(parent_elem, "path", {
                    "d": painter_path_to_svg_d(item.shape()),
                    "custom:type": "function",
                    "custom:func_expression": item.expression,
                    "custom:func_xmin": f"{item.x_min:.2f}",
                    "custom:func_xmax": f"{item.x_max:.2f}",
                    "custom:func_ymin": f"{item.y_min:.2f}",
                    "custom:func_ymax": f"{item.y_max:.2f}",
                    "custom:rect_x": f"{rect.x():.2f}",
                    "custom:rect_y": f"{rect.y():.2f}",
                    "custom:rect_width": f"{rect.width():.2f}",
                    "custom:rect_height": f"{rect.height():.2f}"
                })
                apply_common_props(item, elem)
                
            elif isinstance(item, GroupItem):
                g_elem = ET.SubElement(parent_elem, "g", {
                    "id": f"item_{id(item)}",
                    "custom:name": "Group"
                })
                apply_common_props(item, g_elem)
                for child in item.childItems():
                    serialize_item(child, g_elem)

        # Выгружаем по слоям, соблюдая Z-order
        for layer in document.layers:
            layer_elem = ET.SubElement(root, "g", {
                "id": f"layer_{id(layer)}",
                "custom:type": "layer",
                "custom:name": layer.name,
                "custom:visible": str(layer.visible),
                "custom:locked": str(layer.locked)
            })
            for item in layer.childItems():
                serialize_item(item, layer_elem)
                
        # Запись XML
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def import_from_svg(filepath, document):
        """Импорт векторных слоев и объектов из SVG файла"""
        document.clear()
        
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except Exception as e:
            print(f"Error parsing SVG: {e}")
            return False
            
        custom_ns = "{http://vector.editor/custom}"
        
        # Хранилище созданных объектов для восстановления clip-paths
        id_map = {}
        clip_data_todo = []
        
        def parse_common_props(elem, item):
            # Парсинг имени
            item.name = elem.get(f"{custom_ns}name", "Vector Item")
            
            # Восстанавливаем Z-Трансформации
            transform = elem.get("transform", "")
            if transform:
                translates = re.findall(r'translate\(([-+]?\d*\.\d+|[-+]?\d+),\s*([-+]?\d*\.\d+|[-+]?\d+)\)', transform)
                if translates:
                    item.setPos(float(translates[0][0]), float(translates[0][1]))
                rotates = re.findall(r'rotate\(([-+]?\d*\.\d+|[-+]?\d+)\)', transform)
                if rotates:
                    item.setRotation(float(rotates[0]))
                scales = re.findall(r'scale\(([-+]?\d*\.\d+|[-+]?\d+)\)', transform)
                if scales:
                    item.setScale(float(scales[0]))
                    
            # Восстанавливаем stroke
            stroke = elem.get("stroke", "#000000")
            stroke_opacity = elem.get("stroke-opacity", "1.0")
            stroke_width = elem.get("stroke-width", "1.0")
            
            sc = QColor(stroke)
            sc.setAlpha(int(float(stroke_opacity) * 255))
            item.stroke_color = sc
            item.stroke_width = float(stroke_width)
            
            # Восстанавливаем fill
            fill_type = elem.get(f"{custom_ns}fill_type", "solid")
            if fill_type == "solid":
                fill = elem.get("fill", "none")
                if fill == "none":
                    item.fill_color = QColor(255, 255, 255, 0)
                else:
                    fill_opacity = elem.get("fill-opacity", "1.0")
                    fc = QColor(fill)
                    fc.setAlpha(int(float(fill_opacity) * 255))
                    item.fill_color = fc
            elif fill_type in ("linear", "radial"):
                item.fill_type = fill_type
                item.grad_color_start = QColor(elem.get(f"{custom_ns}grad_color_start", "#ffffff"))
                item.grad_color_end = QColor(elem.get(f"{custom_ns}grad_color_end", "#000000"))
                item.grad_angle = float(elem.get(f"{custom_ns}grad_angle", "0.0"))
                item.grad_radius = float(elem.get(f"{custom_ns}grad_radius", "0.5"))
                item.grad_stops = elem.get(f"{custom_ns}grad_stops", "0.0:#ffffff; 1.0:#000000")
                item.grad_spread = elem.get(f"{custom_ns}grad_spread", "pad")
                
                # Координаты линейного или радиального градиентов
                if fill_type == "linear":
                    for name in ('grad_x1', 'grad_y1', 'grad_x2', 'grad_y2'):
                        val = elem.get(f"custom:{name}")
                        if val is not None:
                            setattr(item, name, float(val))
                else:
                    for name in ('grad_cx', 'grad_cy', 'grad_r', 'grad_fx', 'grad_fy'):
                        val = elem.get(f"custom:{name}")
                        if val is not None:
                            setattr(item, name, float(val))
            
            # Восстанавливаем тень
            shadow_enable = elem.get(f"{custom_ns}shadow_enable", "False")
            if shadow_enable == "True":
                item.shadow_enable = True
                item.shadow_blur = float(elem.get(f"{custom_ns}shadow_blur", "8.0"))
                item.shadow_dx = float(elem.get(f"{custom_ns}shadow_dx", "4.0"))
                item.shadow_dy = float(elem.get(f"{custom_ns}shadow_dy", "4.0"))
                
                sc_str = elem.get(f"{custom_ns}shadow_color", "#000000:128")
                parts = sc_str.split(':')
                if len(parts) == 2:
                    col = QColor(parts[0])
                    col.setAlpha(int(parts[1]))
                    item.shadow_color = col
                item.update_shadow_effect()
                
            # Запомним связи для clip-paths (будет восстановлено позже)
            clip_paths_str = elem.get(f"{custom_ns}clip_paths", "")
            if clip_paths_str:
                clip_mode = elem.get(f"{custom_ns}clip_mode", "and")
                clip_data_todo.append((item, clip_paths_str.split(','), clip_mode))
                
            # Запоминаем ID объекта в карте
            obj_id = elem.get("id")
            if obj_id:
                id_map[obj_id] = item

        def parse_element(elem):
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == "rect":
                x = float(elem.get("x", "0"))
                y = float(elem.get("y", "0"))
                w = float(elem.get("width", "100"))
                h = float(elem.get("height", "100"))
                item = RectangleItem(QRectF(x, y, w, h))
                parse_common_props(elem, item)
                return item
                
            elif tag == "ellipse":
                cx = float(elem.get("cx", "0"))
                cy = float(elem.get("cy", "0"))
                rx = float(elem.get("rx", "10"))
                ry = float(elem.get("ry", "10"))
                rect = QRectF(cx - rx, cy - ry, rx * 2.0, ry * 2.0)
                item = EllipseItem(rect)
                parse_common_props(elem, item)
                return item
                
            elif tag == "line":
                x1 = float(elem.get("x1", "0"))
                y1 = float(elem.get("y1", "0"))
                x2 = float(elem.get("x2", "0"))
                y2 = float(elem.get("y2", "0"))
                item = LineItem(QPointF(x1, y1), QPointF(x2, y2))
                parse_common_props(elem, item)
                return item
                
            elif tag == "polyline":
                pts_str = elem.get("points", "")
                pts = []
                for pair in pts_str.strip().split():
                    if ',' in pair:
                        coords = pair.split(',')
                        pts.append(QPointF(float(coords[0]), float(coords[1])))
                item = PolylineItem(pts)
                parse_common_props(elem, item)
                return item
                
            elif tag == "polygon":
                pts_str = elem.get("points", "")
                pts = []
                for pair in pts_str.strip().split():
                    if ',' in pair:
                        coords = pair.split(',')
                        pts.append(QPointF(float(coords[0]), float(coords[1])))
                item = PolygonItem(pts)
                parse_common_props(elem, item)
                return item
                
            elif tag == "path":
                custom_type = elem.get(f"{custom_ns}type", "")
                if custom_type == "spline":
                    pts_str = elem.get(f"{custom_ns}spline_points", "")
                    pts = []
                    for pair in pts_str.strip().split():
                        if ',' in pair:
                            coords = pair.split(',')
                            pts.append(QPointF(float(coords[0]), float(coords[1])))
                    tension = float(elem.get(f"{custom_ns}spline_tension", "0.5"))
                    closed = elem.get(f"{custom_ns}spline_closed", "False") == "True"
                    item = SplineItem(pts, tension, closed)
                    parse_common_props(elem, item)
                    return item
                    
                elif custom_type == "function":
                    expr = elem.get(f"{custom_ns}func_expression", "x^2 + y^2 = 25")
                    xmin = float(elem.get(f"{custom_ns}func_xmin", "-10.0"))
                    xmax = float(elem.get(f"{custom_ns}func_xmax", "10.0"))
                    ymin = float(elem.get(f"{custom_ns}func_ymin", "-10.0"))
                    ymax = float(elem.get(f"{custom_ns}func_ymax", "10.0"))
                    rx = float(elem.get(f"{custom_ns}rect_x", "-100"))
                    ry = float(elem.get(f"{custom_ns}rect_y", "-100"))
                    rw = float(elem.get(f"{custom_ns}rect_width", "200"))
                    rh = float(elem.get(f"{custom_ns}rect_height", "200"))
                    
                    item = FunctionItem(QRectF(rx, ry, rw, rh), expr)
                    item._x_min = xmin
                    item._x_max = xmax
                    item._y_min = ymin
                    item._y_max = ymax
                    item.recalculate()
                    parse_common_props(elem, item)
                    return item
                    
            elif tag == "g" and elem.get(f"{custom_ns}type") != "layer":
                item = GroupItem()
                parse_common_props(elem, item)
                for child_elem in elem:
                    child_item = parse_element(child_elem)
                    if child_item:
                        child_item.setParentItem(item)
                return item
                
            return None

        # Обрабатываем слои
        first_layer = True
        for elem in root:
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == "g" and elem.get(f"{custom_ns}type") == "layer":
                name = elem.get(f"{custom_ns}name", "Слой")
                visible = elem.get(f"{custom_ns}visible", "True") == "True"
                locked = elem.get(f"{custom_ns}locked", "False") == "True"
                
                # Добавляем слой в документ
                if first_layer:
                    layer = document.layers[0]
                    layer.name = name
                    first_layer = False
                else:
                    layer = document.add_layer(name, create_command=False)
                    
                layer.set_visible(visible)
                layer.set_locked(locked)
                
                # Восстанавливаем сущности слоя
                for child_elem in elem:
                    child_item = parse_element(child_elem)
                    if child_item:
                        layer.add_item(child_item)
                        document._add_item(child_item)
                        
        # Восстанавливаем связи clip-paths
        for target_item, clip_ids, clip_mode in clip_data_todo:
            clips = []
            for cid in clip_ids:
                if cid in id_map:
                    clips.append(id_map[cid])
            if clips:
                target_item.clip_mode = clip_mode
                target_item.set_clip_paths(clips)
                
        document.layers_changed.emit()
        document.items_changed.emit()
        return True