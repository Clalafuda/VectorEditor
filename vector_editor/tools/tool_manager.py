class ToolManager:
    """Менеджер инструментов"""
    
    def __init__(self, document):
        self.document = document
        self.tools = {}
        self.active_tool = None
        
    def register_tool(self, name, tool):
        """Регистрация инструмента"""
        self.tools[name] = tool
        
    def set_active_tool(self, name):
        """Установка активного инструмента"""
        if self.active_tool:
            self.active_tool.deactivate()
            
        self.active_tool = self.tools.get(name)
        if self.active_tool:
            self.active_tool.activate()
            
    def mouse_pressed(self, pos, modifiers):
        """Обработка нажатия мыши"""
        if self.active_tool:
            self.active_tool.mouse_pressed(pos, modifiers)
            
    def mouse_moved(self, pos, modifiers):
        """Обработка движения мыши"""
        if self.active_tool:
            self.active_tool.mouse_moved(pos, modifiers)
            
    def mouse_released(self, pos, modifiers):
        """Обработка отпускания мыши"""
        if self.active_tool:
            self.active_tool.mouse_released(pos, modifiers)
            
    def key_pressed(self, event):
        """Обработка нажатия клавиш"""
        if self.active_tool:
            self.active_tool.key_pressed(event)
