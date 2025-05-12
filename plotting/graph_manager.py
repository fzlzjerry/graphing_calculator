"""
图形管理模块 - 提供图形绘制和管理功能
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from PyQt6.QtWidgets import QSizePolicy
from ui.modern_theme import ModernTheme

from core.function_props import FunctionAnalyzer


class GraphManager:
    """图形管理器类，用于处理图形绘制和管理"""
    
    def __init__(self, plot_layout, statusbar, result_browser, dark_mode=False):
        """初始化图形管理器
        
        Args:
            plot_layout: 图形布局对象
            statusbar: 状态栏对象
            result_browser: 结果显示区对象
            dark_mode: 是否使用暗色模式
        """
        self.plot_layout = plot_layout
        self.statusbar = statusbar
        self.result_browser = result_browser
        self.dark_mode = dark_mode
        
        # 图形相关属性
        self.canvas = None
        self.toolbar = None
        self.ax = None
        self.fig = None
        self.lines = []
        self.expr_list = []
        self.y_funcs_list = []
        self.x_vals = None
        self.intersection_points = []
        
        # 交互相关属性
        self.pressing = False
        self.dot = None
        self.text_annotation = None
        self.selected_graph_index = None
        self.panning = False
        self.pan_start = None
        
        # 事件连接ID
        self.cid_press = None
        self.cid_motion = None
        self.cid_release = None
    
    def setup_new_figure(self, x_min=-10, x_max=10, y_min=-10, y_max=10, show_grid=True):
        """设置新的图形
        
        Args:
            x_min: x轴最小值
            x_max: x轴最大值
            y_min: y轴最小值
            y_max: y轴最大值
            show_grid: 是否显示网格
        """
        # 清除现有的画布和工具栏
        if self.canvas:
            self._disconnect_events()
            self._clear_plot_layout()
        
        # 创建新的图形和坐标轴
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        
        # 设置坐标轴范围
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        # 设置网格
        if show_grid:
            self.ax.grid(True, linestyle='--', alpha=0.2, color='#000000' if not self.dark_mode else '#FFFFFF', zorder=0)
        
        # 设置图形样式
        self._apply_figure_style()
        
        # 创建画布和工具栏
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, None)
        
        # 应用工具栏样式
        self.toolbar.setStyleSheet(ModernTheme.get_toolbar_style(self.dark_mode))
        
        # 设置画布的大小策略和最小高度
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumHeight(400)
        
        # 添加到布局
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
        
        # 连接事件
        self._connect_events()
        
        # 重绘画布
        self.canvas.draw()
        
        return self.fig, self.ax
    
    def plot_functions(self, equations, modules_dict, local_dict, transformations):
        """绘制函数图形
        
        Args:
            equations: 方程式列表
            modules_dict: 模块字典，用于lambdify
            local_dict: 本地字典，用于parse_expr
            transformations: 转换列表，用于parse_expr
            
        Returns:
            str: 结果文本
        """
        self.lines = []
        self.expr_list = []
        self.y_funcs_list = []
        result_text = ""
        
        # 获取当前坐标轴范围
        x_min, x_max = self.ax.get_xlim()
        
        # 创建x值数组
        self.x_vals = np.linspace(x_min, x_max, 800)
        
        # 获取颜色列表
        colors = plt.cm.tab10.colors
        
        x = sp.symbols('x')
        
        # 处理每个方程
        for idx, equation in enumerate(equations):
            try:
                # 解析表达式
                expr = sp.parse_expr(equation, transformations=transformations, local_dict=local_dict)
                
                # 检查表达式中的符号
                symbols_in_expr = expr.free_symbols
                if not symbols_in_expr.issubset({x}):
                    unsupported_vars = symbols_in_expr - {x}
                    var_names = ', '.join(str(var) for var in unsupported_vars)
                    return f"Error: Equation {idx + 1} contains unsupported variables: {var_names}"
                
                # 保存表达式
                self.expr_list.append(expr)
                
                # 创建函数并计算y值
                y_func = sp.lambdify(x, expr, modules=[modules_dict, "numpy"])
                y_vals = y_func(self.x_vals)
                self.y_funcs_list.append(y_func)
                
                # 绘制函数
                line, = self.ax.plot(
                    self.x_vals, y_vals, 
                    color=colors[idx % len(colors)],
                    label=f"${sp.latex(expr)}$"
                )
                self.lines.append(line)
                
                # 计算函数属性
                properties = FunctionAnalyzer.compute_function_properties(expr)
                
                # 添加到结果文本
                result_text += f"Equation {idx + 1}: {equation}\n"
                for prop_name, prop_value in properties.items():
                    result_text += f"{prop_name}: {prop_value}\n"
                result_text += "\n"
                
            except Exception as e:
                return f"Error processing equation {idx + 1}: {str(e)}"
        
        # 计算交点
        self.update_intersections()
        
        # 更新图例
        self._update_legend()
        
        # 重绘画布
        self.canvas.draw()
        
        # 更新状态栏
        self.statusbar.showMessage(f"Plotted {len(equations)} equation(s)")
        
        return result_text
    
    def update_intersections(self):
        """更新函数交点"""
        if len(self.y_funcs_list) >= 2 and self.x_vals is not None:
            self.intersection_points = FunctionAnalyzer.find_intersections(self.y_funcs_list, self.x_vals)
            
            # 在图上标记交点
            for x, y in self.intersection_points:
                self.ax.plot(x, y, 'ro', markersize=4)
    
    def reset_view(self, x_min=-10, x_max=10, y_min=-10, y_max=10):
        """重置视图到默认状态
        
        Args:
            x_min: x轴最小值
            x_max: x轴最大值
            y_min: y轴最小值
            y_max: y轴最大值
        """
        if self.ax:
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.canvas.draw()
    
    def clear_graphs(self):
        """清除所有图形并重置状态"""
        # 重置内部状态
        self.expr_list = []
        self.lines = []
        self.y_funcs_list = []
        self.intersection_points = []
        
        # 设置新的图形
        self.setup_new_figure()
    
    def update_theme(self, dark_mode):
        """更新主题
        
        Args:
            dark_mode: 是否使用暗色模式
        """
        self.dark_mode = dark_mode
        
        if self.ax and self.canvas:
            # 应用新的样式
            self._apply_figure_style()
            self.canvas.draw()
    
    def _apply_figure_style(self):
        """应用图形样式"""
        # 设置图表样式
        plt.style.use('default')
        
        if self.dark_mode:
            # 暗色模式
            self.fig.patch.set_facecolor('#1C1C1E')
            self.ax.set_facecolor('#2C2C2E')
            
            # 设置坐标轴
            for spine in ['left', 'bottom', 'right', 'top']:
                self.ax.spines[spine].set_linewidth(0.5)
                self.ax.spines[spine].set_color('#48484A')
            
            # 美化刻度
            self.ax.tick_params(axis='both', color='#48484A', width=0.5)
            
            # 设置字体
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontsize(10)
                label.set_fontfamily('Arial')
                label.set_color('#8E8E93')
        else:
            # 亮色模式
            self.fig.patch.set_facecolor('#FFFFFF')
            self.ax.set_facecolor('#FAFAFA')
            
            # 设置坐标轴
            for spine in ['left', 'bottom', 'right', 'top']:
                self.ax.spines[spine].set_linewidth(0.5)
                self.ax.spines[spine].set_color('#D1D1D6')
            
            # 美化刻度
            self.ax.tick_params(axis='both', color='#D1D1D6', width=0.5)
            
            # 设置字体
            for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
                label.set_fontsize(10)
                label.set_fontfamily('Arial')
                label.set_color('#6C6C70')
    
    def _update_legend(self):
        """更新图例"""
        if self.ax:
            self.ax.legend(
                loc='upper left',
                fontsize=10,
                frameon=True,
                fancybox=True,
                shadow=True,
                framealpha=0.95,
                edgecolor='#D1D1D6' if not self.dark_mode else '#48484A',
                borderpad=1,
                labelspacing=0.5
            )
    
    def _connect_events(self):
        """连接事件处理器"""
        if self.canvas:
            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
            self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
    
    def _disconnect_events(self):
        """断开事件处理器连接"""
        if self.canvas:
            if self.cid_press:
                self.canvas.mpl_disconnect(self.cid_press)
            if self.cid_motion:
                self.canvas.mpl_disconnect(self.cid_motion)
            if self.cid_release:
                self.canvas.mpl_disconnect(self.cid_release)
    
    def _clear_plot_layout(self):
        """清除绘图布局中的所有部件"""
        if self.plot_layout:
            for i in reversed(range(self.plot_layout.count())):
                widget = self.plot_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
    
    # 以下是事件处理方法，将在interactions.py中实现
    def on_press(self, event):
        pass
    
    def on_motion(self, event):
        pass
    
    def on_release(self, event):
        pass
