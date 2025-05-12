"""
绘图计算器 - 主入口文件

一个功能强大的数学可视化工具，用于绘制和分析数学函数。
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import GraphingCalculatorWindow


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = GraphingCalculatorWindow()
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
