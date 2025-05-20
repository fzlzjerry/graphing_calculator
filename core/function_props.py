"""
函数属性计算模块 - 提供数学函数分析功能
"""

import sympy as sp
import numpy as np


class FunctionAnalyzer:
    """函数分析器类，用于计算函数的各种数学属性"""
    
    @staticmethod
    def compute_function_properties(expr):
        """计算函数的各种数学属性
        
        Args:
            expr: sympy表达式对象
            
        Returns:
            dict: 包含函数属性的字典
        """
        x = sp.symbols('x')
        properties = {}
        
        # 计算零点（x轴交点）
        try:
            x_intercepts = sp.solve(expr, x)
            properties['X-Intercepts'] = x_intercepts
        except Exception:
            properties['X-Intercepts'] = 'Unable to calculate x-intercepts.'
        
        # 计算y轴交点
        try:
            y_intercept = expr.subs(x, 0)
            properties['Y-Intercept'] = y_intercept
        except Exception:
            properties['Y-Intercept'] = 'Unable to calculate y-intercept.'
        
        # 计算函数末端行为
        try:
            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)
            properties['Function End Behavior'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
        except Exception:
            properties['Function End Behavior'] = 'Unable to calculate function end behavior.'
        
        # 计算一阶导数和临界点
        try:
            derivative = sp.diff(expr, x)
            properties['First Derivative'] = derivative
            critical_points = sp.solve(derivative, x)
            properties['Critical Points'] = critical_points
        except Exception:
            properties['First Derivative'] = 'Unable to calculate first derivative.'
            properties['Critical Points'] = 'Unable to calculate critical points.'
        
        # 计算定义域
        try:
            domain = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
            properties['Domain'] = domain
        except Exception:
            properties['Domain'] = 'Unable to calculate domain.'
        
        # 计算值域
        try:
            critical_points = sp.solve(sp.diff(expr, x), x)
            test_points = critical_points.copy()
            
            # 添加定义域的边界点进行测试
            try:
                test_points.append(domain.inf)
                test_points.append(domain.sup)
            except (AttributeError, TypeError):
                pass
            
            y_vals = []
            for point in test_points:
                if point is not None and (point.is_real or point.is_infinite):
                    try:
                        y_val = expr.subs(x, point).evalf()
                        if y_val.is_real:
                            y_vals.append(y_val)
                    except Exception:
                        continue
            
            # 确定值域的上下界
            if y_vals:
                y_min = min(y_vals)
                y_max = max(y_vals)
                
                # 检查函数在无穷处的极限
                limit_pos_inf = sp.limit(expr, x, sp.oo)
                limit_neg_inf = sp.limit(expr, x, -sp.oo)
                
                if limit_pos_inf == sp.oo or limit_neg_inf == sp.oo:
                    y_max = '∞'
                if limit_pos_inf == -sp.oo or limit_neg_inf == -sp.oo:
                    y_min = '-∞'
                
                properties['Range'] = f"[{y_min}, {y_max}]"
            else:
                properties['Range'] = 'Unable to calculate range.'
        except Exception:
            properties['Range'] = 'Unable to calculate range.'
        
        # 计算不连续点和渐近线
        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)
            if discontinuities:
                properties['Vertical Asymptotes'] = list(discontinuities)
                properties['Discontinuities'] = list(discontinuities)
            else:
                properties['Vertical Asymptotes'] = 'No vertical asymptotes.'
                properties['Discontinuities'] = 'No discontinuities.'
            
            # 检查水平渐近线
            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)
            
            if limit_pos_inf.is_finite and limit_neg_inf.is_finite:
                # Always use 'Horizontal Asymptotes' (plural) and a consistent dictionary structure
                properties['Horizontal Asymptotes'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
            else:
                properties['Horizontal Asymptotes'] = 'No horizontal asymptotes.'
        except Exception:
            properties['Asymptotes'] = 'Unable to calculate asymptotes.'
            properties['Discontinuities'] = 'Unable to calculate discontinuities.'
        
        # 计算二阶导数和极值
        try:
            second_derivative = sp.diff(expr, x, 2)
            properties['Second Derivative'] = second_derivative
            
            # 分析临界点的性质
            extrema = []
            for cp in critical_points:
                if cp.is_real:
                    f_cp = expr.subs(x, cp)
                    fpp_cp = second_derivative.subs(x, cp)
                    
                    if fpp_cp.is_real:
                        if fpp_cp > 0:
                            extrema.append((cp, f_cp, 'Local Minimum'))
                        elif fpp_cp < 0:
                            extrema.append((cp, f_cp, 'Local Maximum'))
                        else:
                            extrema.append((cp, f_cp, 'Inflection Point'))
            
            properties['Extrema'] = extrema
        except Exception:
            properties['Extrema'] = 'Unable to calculate extrema.'
        
        return properties
    
    @staticmethod
    def find_intersections(y_funcs_list, x_vals):
        """查找函数交点
        
        Args:
            y_funcs_list: 函数列表
            x_vals: x值数组
            
        Returns:
            list: 交点列表，每个元素为(x, y)坐标
        """
        from itertools import combinations
        
        intersections = []
        combinations_indices = list(combinations(range(len(y_funcs_list)), 2))
        
        # 计算所有函数的y值
        y_vals_list = []
        for y_func in y_funcs_list:
            y_vals = y_func(x_vals)
            y_vals_list.append(y_vals)
        
        # 对每对函数查找交点
        for i, j in combinations_indices:
            y_vals1 = y_vals_list[i]
            y_vals2 = y_vals_list[j]
            
            # 计算差值并处理无穷和NaN
            diff = y_vals1 - y_vals2
            diff = np.where(np.isnan(diff), np.inf, diff)
            diff = np.where(np.isinf(diff), np.inf, diff)
            
            # 查找符号变化的位置（表示交点）
            sign_diff = np.sign(diff)
            sign_changes = np.where(np.diff(sign_diff) != 0)[0]
            
            # 对每个符号变化位置进行线性插值以找到精确交点
            for idx in sign_changes:
                x1, x2 = x_vals[idx], x_vals[idx + 1]
                y1_diff, y2_diff = diff[idx], diff[idx + 1]
                
                if np.isfinite(y1_diff) and np.isfinite(y2_diff):
                    # 线性插值计算交点的x坐标
                    x_zero = x1 - y1_diff * (x2 - x1) / (y2_diff - y1_diff)
                    # 计算交点的y坐标
                    y_zero = y_funcs_list[i](x_zero)
                    intersections.append((x_zero, y_zero))
        
        # 移除重复的交点（考虑浮点误差）
        unique_intersections = list({(round(x, 5), round(y, 5)) for x, y in intersections})
        return unique_intersections
