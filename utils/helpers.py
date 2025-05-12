"""
辅助函数模块 - 提供各种实用工具函数
"""

import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor, implicit_application
)


class ExpressionParser:
    """表达式解析器类，用于处理数学表达式"""
    
    @staticmethod
    def replace_absolute_value(expr_str):
        """替换绝对值表示法
        
        将 |x| 形式的绝对值替换为 Abs(x)
        
        Args:
            expr_str: 表达式字符串
            
        Returns:
            str: 替换后的表达式字符串
        """
        def repl(match):
            return f"Abs({match.group(1)})"
        
        # 使用正则表达式查找并替换绝对值表示法
        pattern = r'\|([^|]+)\|'
        return re.sub(pattern, repl, expr_str)
    
    @staticmethod
    def replace_inverse_trig_functions(expr_str):
        """替换反三角函数表示法
        
        将 arcsin, arccos, arctan 替换为 asin, acos, atan
        
        Args:
            expr_str: 表达式字符串
            
        Returns:
            str: 替换后的表达式字符串
        """
        def repl(match):
            func_name = match.group(1).lower()
            arg = match.group(2)
            mapping = {
                'arcsin': 'asin',
                'arccos': 'acos',
                'arctan': 'atan'
            }
            return f"{mapping.get(func_name, func_name)}({arg})"
        
        # 使用正则表达式查找并替换反三角函数
        pattern = r'(arcsin|arccos|arctan)\(([^)]+)\)'
        return re.sub(pattern, repl, expr_str)
    
    @staticmethod
    def parse_expression(expr_str, local_dict=None):
        """解析数学表达式
        
        Args:
            expr_str: 表达式字符串
            local_dict: 本地变量字典
            
        Returns:
            sympy.Expr: 解析后的表达式对象
        """
        # 预处理表达式
        expr_str = ExpressionParser.replace_absolute_value(expr_str)
        expr_str = ExpressionParser.replace_inverse_trig_functions(expr_str)
        
        # 设置默认的本地变量字典
        if local_dict is None:
            x = sp.symbols('x')
            local_dict = {
                'x': x, 'e': sp.E, 'pi': sp.pi,
                'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
                'log': sp.log, 'sqrt': sp.sqrt, 'Abs': sp.Abs,
                'exp': sp.exp, 'ln': sp.log,
                'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
                'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
                'sec': sp.sec, 'csc': sp.csc, 'cot': sp.cot,
                'factorial': sp.factorial, 'gamma': sp.gamma,
                'erf': sp.erf, 'erfc': sp.erfc
            }
        
        # 设置转换
        transformations = standard_transformations + (
            implicit_multiplication_application, 
            implicit_application, 
            convert_xor
        )
        
        # 解析表达式
        return parse_expr(expr_str, transformations=transformations, local_dict=local_dict)


class FileHandler:
    """文件处理器类，用于处理文件操作"""
    
    @staticmethod
    def save_equations(filename, equations):
        """保存方程式到文件
        
        Args:
            filename: 文件名
            equations: 方程式列表
            
        Returns:
            bool: 是否成功保存
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(equations))
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_equations(filename):
        """从文件加载方程式
        
        Args:
            filename: 文件名
            
        Returns:
            list: 方程式列表，如果失败则返回空列表
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []
