"""
现代主题模块 - 提供更美观的UI主题设置
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt


class ModernTheme:
    """现代UI主题类，提供应用程序的视觉主题"""
    
    # 主题颜色 - 浅色模式
    LIGHT_COLORS = {
        'primary': '#1E88E5',       # 蓝色主色调
        'primary_light': '#64B5F6',  # 浅蓝色
        'primary_dark': '#0D47A1',   # 深蓝色
        'accent': '#FF4081',         # 粉色强调色
        'accent_light': '#FF80AB',   # 浅粉色
        'accent_dark': '#C51162',    # 深粉色
        'background': '#FFFFFF',     # 白色背景
        'card': '#F5F5F5',           # 卡片背景
        'text': '#212121',           # 主文本颜色
        'text_secondary': '#757575', # 次要文本颜色
        'divider': '#BDBDBD',        # 分隔线颜色
        'success': '#4CAF50',        # 成功色
        'warning': '#FFC107',        # 警告色
        'error': '#F44336',          # 错误色
        'info': '#2196F3',           # 信息色
    }
    
    # 主题颜色 - 深色模式
    DARK_COLORS = {
        'primary': '#42A5F5',       # 蓝色主色调
        'primary_light': '#90CAF9',  # 浅蓝色
        'primary_dark': '#1565C0',   # 深蓝色
        'accent': '#FF4081',         # 粉色强调色
        'accent_light': '#FF80AB',   # 浅粉色
        'accent_dark': '#C51162',    # 深粉色
        'background': '#121212',     # 深色背景
        'card': '#1E1E1E',           # 卡片背景
        'text': '#FFFFFF',           # 主文本颜色
        'text_secondary': '#B0B0B0', # 次要文本颜色
        'divider': '#424242',        # 分隔线颜色
        'success': '#66BB6A',        # 成功色
        'warning': '#FFCA28',        # 警告色
        'error': '#EF5350',          # 错误色
        'info': '#42A5F5',           # 信息色
    }
    
    # 字体设置
    FONTS = {
        'family': 'Arial',
        'size_small': 10,
        'size_normal': 12,
        'size_large': 14,
        'size_title': 16,
    }
    
    # 圆角半径
    BORDER_RADIUS = 8
    
    # 间距
    SPACING = {
        'tiny': 2,
        'small': 6,
        'medium': 12,
        'large': 18,
        'xlarge': 24,
    }
    
    @classmethod
    def get_stylesheet(cls, dark_mode=False):
        """获取应用程序样式表
        
        Args:
            dark_mode: 是否使用深色模式
            
        Returns:
            str: 样式表字符串
        """
        colors = cls.DARK_COLORS if dark_mode else cls.LIGHT_COLORS
        
        return f"""
            /* 全局样式 */
            QWidget {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                color: {colors['text']};
                background-color: {colors['background']};
            }}
            
            /* 主窗口样式 */
            QMainWindow {{
                background-color: {colors['background']};
            }}
            
            /* 标签样式 */
            QLabel {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                color: {colors['text']};
                padding: 1px 1px;
            }}
            
            QLabel[title="true"] {{
                font-size: {cls.FONTS['size_large']}px;
                font-weight: bold;
                color: {colors['primary']};
                padding: {cls.SPACING['small']}px {cls.SPACING['small']}px;
            }}
            
            /* 按钮样式 */
            QPushButton {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                font-weight: bold;
                color: white;
                background-color: {colors['primary']};
                border: none;
                border-radius: {cls.BORDER_RADIUS}px;
                padding: 2px 4px;
                min-height: 28px;
                margin: 0px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_light']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary_dark']};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['divider']};
                color: {colors['text_secondary']};
            }}
            
            QPushButton[accent="true"] {{
                background-color: {colors['accent']};
            }}
            
            QPushButton[accent="true"]:hover {{
                background-color: {colors['accent_light']};
            }}
            
            QPushButton[accent="true"]:pressed {{
                background-color: {colors['accent_dark']};
            }}
            
            QPushButton[flat="true"] {{
                background-color: transparent;
                color: {colors['primary']};
                border: none;
            }}
            
            QPushButton[flat="true"]:hover {{
                color: {colors['primary_light']};
                background-color: rgba(0, 0, 0, 0.05);
            }}
            
            QPushButton[flat="true"]:pressed {{
                color: {colors['primary_dark']};
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QPushButton[secondary="true"] {{
                background-color: transparent;
                color: {colors['primary']};
                border: 1px solid {colors['primary']};
            }}
            
            QPushButton[secondary="true"]:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            
            QPushButton[secondary="true"]:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            /* 输入框样式 */
            QLineEdit {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                padding: 2px 4px;
                border: 1px solid {colors['divider']};
                border-radius: {cls.BORDER_RADIUS}px;
                background-color: {colors['background']};
                color: {colors['text']};
                selection-background-color: {colors['primary_light']};
            }}
            
            QLineEdit:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            /* 文本浏览器样式 */
            QTextBrowser {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                padding: {cls.SPACING['small']}px;
                border: 1px solid {colors['divider']};
                border-radius: {cls.BORDER_RADIUS}px;
                background-color: {colors['card']};
                color: {colors['text']};
                selection-background-color: {colors['primary_light']};
            }}
            
            /* 组框样式 */
            QGroupBox {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                font-weight: bold;
                border: 1px solid {colors['divider']};
                border-radius: {cls.BORDER_RADIUS}px;
                margin-top: 2.5ex;
                padding: {cls.SPACING['medium']}px;
                background-color: {colors['card']};
                color: {colors['text']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {cls.SPACING['small']}px;
                top: -2.0ex;
                padding: 0 {cls.SPACING['small']}px;
                background-color: {colors['card']};
                color: {colors['text']};
            }}
            
            /* 复选框样式 */
            QCheckBox {{
                font-family: {cls.FONTS['family']};
                font-size: {cls.FONTS['size_normal']}px;
                color: {colors['text']};
                spacing: {cls.SPACING['small']}px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {colors['divider']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border: 1px solid {colors['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwLjIgMy44TDQuOCA5LjJMMS44IDYuMiIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
            }}
            
            /* 分割器样式 */
            QSplitter::handle {{
                background-color: {colors['divider']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            
            QSplitter::handle:vertical {{
                height: 1px;
            }}
            
            /* 状态栏样式 */
            QStatusBar {{
                background-color: {colors['card']};
                color: {colors['text_secondary']};
                border-top: 1px solid {colors['divider']};
                min-height: 24px;
                padding: 2px 4px;
            }}
            
            /* 工具栏样式 */
            QToolBar {{
                border: none;
                background-color: {colors['card']};
                spacing: {cls.SPACING['small']}px;
                padding: {cls.SPACING['tiny']}px;
            }}
            
            QToolButton {{
                border: none;
                background-color: transparent;
                padding: {cls.SPACING['tiny']}px;
                border-radius: {cls.BORDER_RADIUS // 2}px;
            }}
            
            QToolButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            
            QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            /* 滚动条样式 */
            QScrollBar:vertical {{
                border: none;
                background-color: {colors['card']};
                width: 10px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['divider']};
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['primary_light']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: {colors['card']};
                height: 10px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {colors['divider']};
                border-radius: 5px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {colors['primary_light']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
    
    @classmethod
    def get_toolbar_style(cls, dark_mode=False):
        """获取工具栏样式表
        
        Args:
            dark_mode: 是否使用深色模式
            
        Returns:
            str: 样式表字符串
        """
        colors = cls.DARK_COLORS if dark_mode else cls.LIGHT_COLORS
        
        return f"""
            QToolBar {{
                border: none;
                background-color: {colors['card']};
                spacing: {cls.SPACING['small']}px;
                padding: {cls.SPACING['tiny']}px;
            }}
            
            QToolButton {{
                border: none;
                background-color: transparent;
                padding: {cls.SPACING['tiny']}px;
                border-radius: {cls.BORDER_RADIUS // 2}px;
            }}
            
            QToolButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            
            QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
        """
    
    @classmethod
    def get_palette(cls, dark_mode=False):
        """获取应用程序调色板
        
        Args:
            dark_mode: 是否使用深色模式
            
        Returns:
            QPalette: 调色板对象
        """
        colors = cls.DARK_COLORS if dark_mode else cls.LIGHT_COLORS
        
        palette = QPalette()
        
        # 设置窗口背景色
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text']))
        
        # 设置按钮颜色
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('white'))
        
        # 设置高亮颜色
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))
        
        # 设置工具提示颜色
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['card']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['text']))
        
        # 设置文本颜色
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors['text_secondary']))
        
        # 设置基础颜色
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['card']))
        
        # 设置链接颜色
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors['primary_dark']))
        
        return palette
    
    @classmethod
    def get_default_font(cls):
        """获取默认字体
        
        Returns:
            QFont: 字体对象
        """
        font = QFont(cls.FONTS['family'], cls.FONTS['size_normal'])
        return font
