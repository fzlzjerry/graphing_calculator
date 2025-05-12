"""
交互处理模块 - 提供图表交互功能
"""

import numpy as np
import sympy as sp
from PyQt6.QtCore import Qt


class GraphInteractions:
    """图表交互处理类，用于处理用户与图表的交互"""
    
    def __init__(self, graph_manager):
        """初始化交互处理器
        
        Args:
            graph_manager: 图形管理器对象
        """
        self.graph_manager = graph_manager
        
        # 交互状态
        self.pressing = False
        self.panning = False
        self.pan_start = None
        self.selected_graph_index = None
        
        # 连接事件
        self._connect_events()
    
    def _connect_events(self):
        """连接事件处理器到图形管理器"""
        if self.graph_manager:
            # 覆盖图形管理器的事件处理方法
            self.graph_manager.on_press = self.on_press
            self.graph_manager.on_motion = self.on_motion
            self.graph_manager.on_release = self.on_release
    
    def on_press(self, event):
        """鼠标按下事件处理
        
        Args:
            event: 鼠标事件对象
        """
        if event.button == 1:  # 左键
            self.pressing = True
            self.selected_graph_index = None
            
            # 更新点位置
            self.update_dot(event)
        
        elif event.button == 2:  # 中键
            self.panning = True
            self.pan_start = (event.xdata, event.ydata)
    
    def on_motion(self, event):
        """鼠标移动事件处理
        
        Args:
            event: 鼠标事件对象
        """
        if not event.inaxes:
            return
        
        if self.pressing:
            # 更新点位置
            self.update_dot(event)
        
        elif self.panning and self.pan_start:
            # 处理平移
            if event.xdata and event.ydata:
                dx = self.pan_start[0] - event.xdata
                dy = self.pan_start[1] - event.ydata
                
                ax = self.graph_manager.ax
                
                # 获取当前视图范围
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                
                # 应用平移
                ax.set_xlim(x_min + dx, x_max + dx)
                ax.set_ylim(y_min + dy, y_max + dy)
                
                # 更新画布
                self.graph_manager.canvas.draw_idle()
                
                # 更新起始点
                self.pan_start = (event.xdata, event.ydata)
    
    def on_release(self, event):
        """鼠标释放事件处理
        
        Args:
            event: 鼠标事件对象
        """
        if event.button == 1:  # 左键
            self.pressing = False
        
        elif event.button == 2:  # 中键
            self.panning = False
            self.pan_start = None
    
    def update_dot(self, event):
        """更新交互点和标注
        
        Args:
            event: 鼠标事件对象
        """
        x = event.xdata
        y = event.ydata
        
        if x is None or y is None:
            return
        
        # 获取坐标轴范围
        ax = self.graph_manager.ax
        x_range = ax.get_xlim()
        x_scale = x_range[1] - x_range[0]
        y_range = ax.get_ylim()
        y_scale = y_range[1] - y_range[0]
        
        # 设置阈值
        x_threshold = x_scale * 0.01
        intersection_threshold = x_scale * 0.025
        y_threshold = y_scale * 0.025
        
        # 检查是否应该捕捉到整数x值
        x_int = round(x)
        delta_x = abs(x - x_int)
        if delta_x < x_threshold:
            x_snap = x_int
        else:
            x_snap = x
        
        # 检查是否应该捕捉到交点
        snapped_to_intersection = False
        for x_ints, y_ints in self.graph_manager.intersection_points:
            if abs(x_snap - x_ints) < intersection_threshold and abs(y - y_ints) < y_threshold:
                x_snap = x_ints
                y = y_ints
                snapped_to_intersection = True
                break
        
        # 如果没有选中图形且没有捕捉到交点，则选择最近的曲线
        if self.selected_graph_index is None and not snapped_to_intersection:
            y_curves = []
            for y_func in self.graph_manager.y_funcs_list:
                try:
                    y_curve = y_func(x_snap)
                    if np.isfinite(y_curve):
                        y_curves.append(y_curve)
                    else:
                        y_curves.append(np.nan)
                except Exception:
                    y_curves.append(np.nan)
            
            # 计算到每条曲线的距离
            distances = [abs(y - y_curve) for y_curve in y_curves]
            valid_distances = [(dist, idx) for idx, dist in enumerate(distances) if not np.isnan(dist)]
            
            if not valid_distances:
                return
            
            # 选择最近的曲线
            min_distance, min_index = min(valid_distances, key=lambda t: t[0])
            y_curve = y_curves[min_index]
            
            # 如果距离小于阈值，则选中该曲线
            if min_distance < y_threshold:
                self.selected_graph_index = min_index
            else:
                return
        
        # 如果已选中图形，则更新点和标注
        if self.selected_graph_index is not None:
            try:
                y_func = self.graph_manager.y_funcs_list[self.selected_graph_index]
                y_curve = y_func(x_snap)
                
                if not np.isfinite(y_curve):
                    return
                
                # 移除现有的点和标注
                if self.graph_manager.dot:
                    self.graph_manager.dot.remove()
                
                if self.graph_manager.text_annotation:
                    self.graph_manager.text_annotation.remove()
                
                # 绘制新的点
                self.graph_manager.dot = self.graph_manager.ax.plot(x_snap, y_curve, 'ro')[0]
                
                # 格式化坐标显示
                x_display = round(x_snap, 2)
                y_display = round(y_curve, 2)
                
                # 获取方程标签
                equation_label = f"${sp.latex(self.graph_manager.expr_list[self.selected_graph_index])}$"
                
                # 添加文本标注
                self.graph_manager.text_annotation = self.graph_manager.ax.text(
                    x_snap,
                    y_curve + (self.graph_manager.ax.get_ylim()[1] - self.graph_manager.ax.get_ylim()[0]) * 0.03,
                    f"({x_display}, {y_display})\n{equation_label}",
                    fontsize=10,
                    color='black' if not self.graph_manager.dark_mode else 'white',
                    ha='center',
                    va='bottom'
                )
                
                # 更新画布
                self.graph_manager.canvas.draw_idle()
            
            except (IndexError, ValueError, TypeError):
                pass
    
    def handle_wheel_event(self, event):
        """处理鼠标滚轮事件
        
        Args:
            event: 滚轮事件对象
            
        Returns:
            bool: 是否处理了事件
        """
        if not self.graph_manager.canvas:
            return False
        
        # 获取鼠标位置
        pos = event.position()
        mouse_x = pos.x()
        mouse_y = pos.y()
        
        # 转换为图表坐标
        ax = self.graph_manager.ax
        canvas = self.graph_manager.canvas
        
        # 检查鼠标是否在图表区域内
        try:
            # 创建一个带有x和y属性的对象
            coords = canvas.mouseEventCoords(event)
            class MouseEvent:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
            
            mouse_event = MouseEvent(coords[0], coords[1])
            if not ax.in_axes(mouse_event):
                return False
        except Exception:
            # 如果转换失败，默认允许事件处理
            pass
        
        # 获取当前视图范围
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # 计算缩放因子
        scale_factor = 1.2
        
        # 根据滚轮方向确定缩放方向
        if event.angleDelta().y() > 0:
            # 放大
            scale_factor = 1.0 / scale_factor
        
        # 应用缩放
        self.zoom(scale_factor, event)
        
        return True
    
    def zoom(self, scale_factor, event):
        """缩放图表
        
        Args:
            scale_factor: 缩放因子
            event: 事件对象
        """
        ax = self.graph_manager.ax
        canvas = self.graph_manager.canvas
        
        # 获取鼠标在图表中的位置
        try:
            coords = canvas.mouseEventCoords(event)
            x_data, y_data = coords
        except Exception:
            # 如果转换失败，使用图表中心作为默认位置
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            x_data = (x_min + x_max) / 2
            y_data = (y_min + y_max) / 2
        
        # 获取当前视图范围
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # 计算新的范围
        x_range = (x_max - x_min) * scale_factor
        y_range = (y_max - y_min) * scale_factor
        
        # 保持鼠标位置不变的缩放
        x_min_new = x_data - x_range * (x_data - x_min) / (x_max - x_min)
        x_max_new = x_data + x_range * (x_max - x_data) / (x_max - x_min)
        y_min_new = y_data - y_range * (y_data - y_min) / (y_max - y_min)
        y_max_new = y_data + y_range * (y_max - y_data) / (y_max - y_min)
        
        # 应用新的范围
        ax.set_xlim(x_min_new, x_max_new)
        ax.set_ylim(y_min_new, y_max_new)
        
        # 更新画布
        canvas.draw_idle()
    
    def pan_wheel(self, delta_x, delta_y, event):
        """使用滚轮平移图表
        
        Args:
            delta_x: x方向的平移量
            delta_y: y方向的平移量
            event: 事件对象
        """
        ax = self.graph_manager.ax
        
        # 获取当前视图范围
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # 应用平移
        ax.set_xlim(x_min + delta_x, x_max + delta_x)
        ax.set_ylim(y_min + delta_y, y_max + delta_y)
        
        # 更新画布
        self.graph_manager.canvas.draw_idle()
