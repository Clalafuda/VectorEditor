#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def setup_linux_environment():
    """Настройка Linux-окружения"""
    if not sys.platform.startswith('linux'):
        return
    
    # Определение дисплейного сервера
    if os.environ.get('WAYLAND_DISPLAY'):
        os.environ['QT_QPA_PLATFORM'] = 'wayland'
    else:
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
    
    # Использование системной темы
    os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk3'

def main():
    # Настройка Linux
    setup_linux_environment()
    
    # Включение HiDPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Vector Editor")
    app.setApplicationDisplayName("Vector Editor")
    
    # Импортируем главное окно
    from vector_editor.gui.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()