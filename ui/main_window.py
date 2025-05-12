"""
主窗口UI组件模块 - 实现主窗口界面
"""

import sys
import numpy as np
import sympy as sp
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTextBrowser, QMessageBox, 
    QSizePolicy, QSplitter, QFileDialog, QStatusBar, QGroupBox, 
    QFormLayout, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QWheelEvent, QNativeGestureEvent
from sympy.functions.special.bessel import jn, yn
from scipy import special

from ui.modern_theme import ModernTheme
from plotting.graph_manager import GraphManager
from plotting.interactions import GraphInteractions
from utils.helpers import ExpressionParser, FileHandler


class GraphingCalculatorWindow(QMainWindow):
    """绘图计算器主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("Graphing Calculator")
        self.resize(800, 1000)
        
        # 初始化UI组件
        self.init_ui()
        
        # 初始化图形管理器
        self.graph_manager = GraphManager(
            self.plot_layout,
            self.statusBar(),
            self.result_browser,
            self.dark_mode_checkbox.isChecked()
        )
        
        # 应用样式
        self.apply_styles()
        
        # 初始化交互处理器
        self.interactions = GraphInteractions(self.graph_manager)
        
        # 设置初始图形
        self.graph_manager.setup_new_figure(
            show_grid=self.grid_checkbox.isChecked()
        )
        
        # 定义模块字典，用于lambdify
        self.modules = {
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
            'log': np.log, 'sqrt': np.sqrt, 'Abs': np.abs,
            'exp': np.exp, 'ln': np.log, 'e': np.e, 'pi': np.pi,
            'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
            'asinh': np.arcsinh, 'acosh': np.arccosh, 'atanh': np.arctanh,
            'sec': lambda x: 1 / np.cos(x),
            'csc': lambda x: 1 / np.sin(x),
            'cot': lambda x: 1 / np.tan(x),
            'factorial': special.factorial, 'gamma': special.gamma,
            'erf': special.erf, 'erfc': special.erfc,
            'jn': special.jn, 'yn': special.yn
        }
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter)
        
        # 创建上半部分部件
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        splitter.addWidget(top_widget)
        
        # 创建下半部分部件
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)
        splitter.addWidget(bottom_widget)
        
        # 设置分割器初始大小
        splitter.setSizes([700, 300])
        
        # 创建输入区域
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        top_layout.addWidget(input_group)
        
        # 创建2D方程输入
        input_2d_layout = QHBoxLayout()
        input_layout.addLayout(input_2d_layout)
        
        input_2d_label = QLabel("输入2D方程式:")
        input_2d_layout.addWidget(input_2d_label)
        
        self.entry_2d = QLineEdit()
        self.entry_2d.setPlaceholderText("输入方程式，用空格分隔多个方程式，例如: sin(x) x^2 |x|")
        input_2d_layout.addWidget(self.entry_2d)
        
        self.plot_button = QPushButton("绘制2D图形")
        self.plot_button.clicked.connect(self.plot_graphs_2d)
        input_2d_layout.addWidget(self.plot_button)
        
        # 创建模板按钮区域
        templates_layout = QHBoxLayout()
        input_layout.addLayout(templates_layout)
        
        templates_label = QLabel("常用函数:")
        templates_layout.addWidget(templates_label)
        
        # 添加模板按钮
        templates = [
            ("sin(x)", "sin(x)"),
            ("cos(x)", "cos(x)"),
            ("tan(x)", "tan(x)"),
            ("x²", "x^2"),
            ("√x", "sqrt(x)"),
            ("e^x", "exp(x)"),
            ("ln(x)", "ln(x)"),
            ("|x|", "|x|"),
            ("1/x", "1/x")
        ]
        
        for label, template in templates:
            button = QPushButton(label)
            button.setProperty("secondary", True)
            button.clicked.connect(lambda checked, t=template: self.insert_template(t))
            templates_layout.addWidget(button)
        
        # 创建设置区域
        settings_group = QGroupBox("设置")
        settings_layout = QGridLayout(settings_group)
        top_layout.addWidget(settings_group)
        
        # 坐标范围设置
        range_label = QLabel("坐标范围:")
        settings_layout.addWidget(range_label, 0, 0)
        
        x_min_label = QLabel("X最小值:")
        settings_layout.addWidget(x_min_label, 0, 1)
        self.x_min = QLineEdit("-10")
        settings_layout.addWidget(self.x_min, 0, 2)
        
        x_max_label = QLabel("X最大值:")
        settings_layout.addWidget(x_max_label, 0, 3)
        self.x_max = QLineEdit("10")
        settings_layout.addWidget(self.x_max, 0, 4)
        
        y_min_label = QLabel("Y最小值:")
        settings_layout.addWidget(y_min_label, 1, 1)
        self.y_min = QLineEdit("-10")
        settings_layout.addWidget(self.y_min, 1, 2)
        
        y_max_label = QLabel("Y最大值:")
        settings_layout.addWidget(y_max_label, 1, 3)
        self.y_max = QLineEdit("10")
        settings_layout.addWidget(self.y_max, 1, 4)
        
        apply_range_button = QPushButton("应用范围")
        apply_range_button.clicked.connect(self.update_graph_settings)
        settings_layout.addWidget(apply_range_button, 1, 5)
        
        # 网格和主题设置
        self.grid_checkbox = QCheckBox("显示网格")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.update_graph_settings)
        settings_layout.addWidget(self.grid_checkbox, 2, 1, 1, 2)
        
        self.dark_mode_checkbox = QCheckBox("暗色模式")
        self.dark_mode_checkbox.setChecked(False)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        settings_layout.addWidget(self.dark_mode_checkbox, 2, 3, 1, 2)
        
        # 创建操作按钮区域
        actions_layout = QHBoxLayout()
        settings_layout.addLayout(actions_layout, 3, 0, 1, 6)
        
        # 添加操作按钮
        save_button = QPushButton("保存方程式")
        save_button.clicked.connect(self.save_graphs)
        actions_layout.addWidget(save_button)
        
        load_button = QPushButton("加载方程式")
        load_button.clicked.connect(self.load_graphs)
        actions_layout.addWidget(load_button)
        
        export_button = QPushButton("导出图像")
        export_button.clicked.connect(self.export_graph)
        actions_layout.addWidget(export_button)
        
        reset_view_button = QPushButton("重置视图")
        reset_view_button.clicked.connect(self.reset_view)
        actions_layout.addWidget(reset_view_button)
        
        clear_button = QPushButton("清除图形")
        clear_button.clicked.connect(self.clear_graphs)
        actions_layout.addWidget(clear_button)
        
        # 创建绘图区域
        plot_group = QGroupBox("图形")
        self.plot_layout = QVBoxLayout(plot_group)
        top_layout.addWidget(plot_group, 1)  # 使用拉伸因子1
        
        # 创建结果区域
        result_group = QGroupBox("结果")
        result_layout = QVBoxLayout(result_group)
        bottom_layout.addWidget(result_group)
        
        self.result_browser = QTextBrowser()
        result_layout.addWidget(self.result_browser)
        
        # 创建状态栏
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("就绪")
        
        # 应用样式
        self.apply_styles()
        
        # 安装事件过滤器
        self.installEventFilter(self)
    
    def apply_styles(self):
        """应用样式表"""
        # 获取样式表和调色板
        dark_mode = self.dark_mode_checkbox.isChecked()
        style_sheet = ModernTheme.get_stylesheet(dark_mode)
        palette = ModernTheme.get_palette(dark_mode)
        font = ModernTheme.get_default_font()
        
        # 应用样式表和调色板
        self.setStyleSheet(style_sheet)
        self.setPalette(palette)
        self.setFont(font)
    
    def toggle_dark_mode(self, state):
        """切换暗色模式
        
        Args:
            state: 复选框状态
        """
        # 应用新样式
        self.apply_styles()
        
        # 更新图形主题
        if self.graph_manager:
            self.graph_manager.update_theme(state)
    
    def update_graph_settings(self):
        """更新图形设置"""
        try:
            # 获取坐标范围
            x_min = float(self.x_min.text())
            x_max = float(self.x_max.text())
            y_min = float(self.y_min.text())
            y_max = float(self.y_max.text())
            
            # 检查范围有效性
            if x_min >= x_max or y_min >= y_max:
                QMessageBox.warning(self, "无效范围", "最小值必须小于最大值")
                return
            
            # 更新图形
            if self.graph_manager:
                # 设置坐标轴范围
                self.graph_manager.ax.set_xlim(x_min, x_max)
                self.graph_manager.ax.set_ylim(y_min, y_max)
                
                # 设置网格
                self.graph_manager.ax.grid(self.grid_checkbox.isChecked(), 
                                          linestyle='--', 
                                          alpha=0.2, 
                                          color='#000000' if not self.dark_mode_checkbox.isChecked() else '#FFFFFF', 
                                          zorder=0)
                
                # 更新画布
                self.graph_manager.canvas.draw()
        
        except ValueError:
            QMessageBox.warning(self, "无效输入", "请输入有效的数值")
    
    def insert_template(self, template):
        """插入函数模板
        
        Args:
            template: 模板字符串
        """
        current_text = self.entry_2d.text()
        if current_text and not current_text.endswith(' '):
            self.entry_2d.setText(current_text + ' ' + template)
        else:
            self.entry_2d.setText(current_text + template)
    
    def plot_graphs_2d(self):
        """绘制2D图形"""
        # 获取方程式输入
        equations_input = self.entry_2d.text().strip()
        
        if not equations_input:
            self.result_browser.setText("请输入至少一个方程式。")
            return
        
        # 分割多个方程式
        equations = equations_input.split()
        
        # 创建符号变量和转换
        x = sp.symbols('x')
        transformations = sp.parsing.sympy_parser.standard_transformations + (
            sp.parsing.sympy_parser.implicit_multiplication_application, 
            sp.parsing.sympy_parser.implicit_application, 
            sp.parsing.sympy_parser.convert_xor
        )
        
        # 创建本地字典
        local_dict = {
            'x': x, 'e': np.e, 'pi': np.pi,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            'log': sp.log, 'sqrt': sp.sqrt, 'Abs': sp.Abs,
            'exp': sp.exp, 'ln': sp.log,
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
            'sec': sp.sec, 'csc': sp.csc, 'cot': sp.cot,
            'factorial': sp.factorial, 'gamma': sp.gamma,
            'erf': sp.erf, 'erfc': sp.erfc,
            'jn': jn, 'yn': yn
        }
        
        # 处理方程式
        processed_equations = []
        for equation in equations:
            # 预处理方程式
            equation = ExpressionParser.replace_absolute_value(equation)
            equation = ExpressionParser.replace_inverse_trig_functions(equation)
            processed_equations.append(equation)
        
        # 绘制图形
        result_text = self.graph_manager.plot_functions(
            processed_equations, 
            self.modules, 
            local_dict, 
            transformations
        )
        
        # 显示结果
        self.result_browser.setText(result_text)
    
    def save_graphs(self):
        """保存方程式到文件"""
        if not self.entry_2d.text().strip():
            QMessageBox.warning(self, "无方程式", "没有方程式可保存")
            return
        
        # 获取保存文件名
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存方程式", "", "文本文件 (*.txt)"
        )
        
        if filename:
            # 保存方程式
            equations = self.entry_2d.text().strip().split()
            if FileHandler.save_equations(filename, equations):
                self.statusBar().showMessage(f"方程式已保存到 {filename}")
            else:
                QMessageBox.warning(self, "保存失败", "无法保存方程式")
    
    def load_graphs(self):
        """从文件加载方程式"""
        # 获取加载文件名
        filename, _ = QFileDialog.getOpenFileName(
            self, "加载方程式", "", "文本文件 (*.txt)"
        )
        
        if filename:
            # 加载方程式
            equations = FileHandler.load_equations(filename)
            if equations:
                self.entry_2d.setText(' '.join(equations))
                self.statusBar().showMessage(f"已从 {filename} 加载方程式")
                
                # 自动绘制图形
                self.plot_graphs_2d()
            else:
                QMessageBox.warning(self, "加载失败", "无法加载方程式或文件为空")
    
    def export_graph(self):
        """导出图形为图像文件"""
        if not self.graph_manager or not self.graph_manager.fig:
            QMessageBox.warning(self, "无图形", "没有图形可导出")
            return
        
        # 获取保存文件名
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出图形", "", "PNG图像 (*.png);;SVG图像 (*.svg)"
        )
        
        if filename:
            try:
                # 保存图形
                self.graph_manager.fig.savefig(filename, dpi=300, bbox_inches='tight')
                self.statusBar().showMessage(f"图形已导出到 {filename}")
            except Exception as e:
                QMessageBox.warning(self, "导出失败", f"无法导出图形: {str(e)}")
    
    def reset_view(self):
        """重置图表视图到默认状态"""
        if self.graph_manager:
            # 重置坐标范围输入框
            self.x_min.setText("-10")
            self.x_max.setText("10")
            self.y_min.setText("-10")
            self.y_max.setText("10")
            
            # 重置图形视图
            self.graph_manager.reset_view()
            
            self.statusBar().showMessage("视图已重置")
    
    def clear_graphs(self):
        """清除所有图表并重置UI状态"""
        if self.graph_manager:
            # 清除输入
            self.entry_2d.clear()
            self.result_browser.clear()
            
            # 清除图形
            self.graph_manager.clear_graphs()
            
            self.statusBar().showMessage("所有图形已清除")
    
    def eventFilter(self, source, event):
        """事件过滤器，用于处理特殊事件
        
        Args:
            source: 事件源对象
            event: 事件对象
            
        Returns:
            bool: 是否处理了事件
        """
        # 处理滚轮事件
        if event.type() == QEvent.Type.Wheel and source is self:
            if self.interactions:
                if self.interactions.handle_wheel_event(event):
                    return True
        
        # 处理原生手势事件
        elif event.type() == QEvent.Type.NativeGesture:
            if isinstance(event, QNativeGestureEvent):
                if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                    if self.interactions:
                        scale_factor = 1.0 - event.value()
                        self.interactions.zoom(scale_factor, event)
                        return True
        
        return super().eventFilter(source, event)
    
    def wheelEvent(self, event):
        """滚轮事件处理
        
        Args:
            event: 滚轮事件对象
        """
        # 检查是否按下Ctrl键
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # 精确缩放
            delta = event.angleDelta().y() / 120.0
            scale_factor = 0.9 if delta < 0 else 1.1
            
            if self.interactions:
                self.interactions.zoom(scale_factor, event)
        elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # 水平平移
            delta_x = event.angleDelta().y() / 120.0 * 0.1
            
            if self.interactions:
                self.interactions.pan_wheel(delta_x, 0, event)
        else:
            # 垂直平移
            delta_y = event.angleDelta().y() / 120.0 * 0.1
            
            if self.interactions:
                self.interactions.pan_wheel(0, delta_y, event)
        
        # 阻止事件传播
        event.accept()
