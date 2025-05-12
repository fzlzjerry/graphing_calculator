"""
UI样式定义模块 - 包含应用程序的所有样式定义
"""


class AppStyles:
    """应用程序样式类，包含所有UI样式定义"""
    
    # 颜色常量
    COLORS = {
        'primary': '#0A84FF',           # 更鲜艳的蓝色
        'primary_hover': '#0066CC',
        'primary_pressed': '#004C99',
        'secondary': '#F2F2F7',
        'secondary_hover': '#E5E5EA',
        'secondary_pressed': '#D1D1D6',
        'border': '#E5E5EA',
        'text': '#1C1C1E',
        'text_secondary': '#8E8E93',
        'background': '#FFFFFF',
        'error': '#FF453A',
        'success': '#32D74B',
        'card_background': '#F9F9FB',
    }
    
    # 暗色模式颜色
    DARK_COLORS = {
        'primary': '#0A84FF',
        'primary_hover': '#409CFF',
        'primary_pressed': '#70B8FF',
        'secondary': '#3A3A3C',
        'secondary_hover': '#48484A',
        'secondary_pressed': '#545456',
        'border': '#48484A',
        'text': '#FFFFFF',
        'text_secondary': '#8E8E93',
        'background': '#1C1C1E',
        'error': '#FF453A',
        'success': '#32D74B',
        'card_background': '#2C2C2E',
    }
    
    @classmethod
    def get_main_style(cls, dark_mode=False):
        """获取主窗口样式表
        
        Args:
            dark_mode: 是否使用暗色模式
            
        Returns:
            str: 样式表字符串
        """
        colors = cls.DARK_COLORS if dark_mode else cls.COLORS
        
        return f"""
            QMainWindow {{
                background-color: {colors['background']};
            }}
            QLabel {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 13px;
                color: {colors['text']};
                padding: 2px 0px;
            }}
            QPushButton {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: white;
                background-color: {colors['primary']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-height: 32px;
                margin: 0px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['primary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {colors['secondary']};
                color: {colors['text_secondary']};
            }}
            QPushButton[secondary="true"] {{
                background-color: {colors['secondary']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}
            QPushButton[secondary="true"]:hover {{
                background-color: {colors['secondary_hover']};
            }}
            QPushButton[secondary="true"]:pressed {{
                background-color: {colors['secondary_pressed']};
            }}
            QLineEdit {{
                font-family: Arial, sans-serif;
                font-size: 13px;
                padding: 8px 12px;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            QLineEdit:focus {{
                border: 1px solid {colors['primary']};
            }}
            QTextBrowser {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 13px;
                padding: 8px;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            QGroupBox {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                background-color: {colors['card_background']};
                color: {colors['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QCheckBox {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 13px;
                color: {colors['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {colors['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border: 1px solid {colors['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwLjIgMy44TDQuOCA5LjJMMS44IDYuMiIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
            }}
            QSplitter::handle {{
                background-color: {colors['border']};
            }}
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            QSplitter::handle:vertical {{
                height: 1px;
            }}
            QStatusBar {{
                background-color: {colors['background']};
                color: {colors['text_secondary']};
                border-top: 1px solid {colors['border']};
            }}
        """
    
    @classmethod
    def get_toolbar_style(cls, dark_mode=False):
        """获取工具栏样式表
        
        Args:
            dark_mode: 是否使用暗色模式
            
        Returns:
            str: 样式表字符串
        """
        colors = cls.DARK_COLORS if dark_mode else cls.COLORS
        
        return f"""
            QToolBar {{
                border: none;
                background-color: transparent;
                spacing: 8px;
            }}
            QToolButton {{
                border: none;
                background-color: transparent;
                padding: 4px;
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background-color: {colors['secondary']};
            }}
            QToolButton:pressed {{
                background-color: {colors['secondary_hover']};
            }}
        """
