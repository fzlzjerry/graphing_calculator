import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTextBrowser
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QWheelEvent, QNativeGestureEvent
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor, implicit_application
)
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
import matplotlib
import matplotlib.pyplot as plt
from itertools import combinations

matplotlib.use('QtAgg')

class GraphingCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphing Calculator")
        self.initUI()
        self.canvas = None
        self.toolbar = None
        self.pressing = False
        self.dot = None
        self.text_annotation = None
        self.selected_graph_index = None
        self.cid_press = None
        self.cid_motion = None
        self.cid_release = None

    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        self.label_2d = QLabel("Enter 2D equations (separated by spaces):")
        layout.addWidget(self.label_2d)
        self.entry_2d = QLineEdit()
        layout.addWidget(self.entry_2d)

        self.plot_button_2d = QPushButton("Plot 2D Graph")
        self.plot_button_2d.clicked.connect(self.plot_graphs_2d)
        layout.addWidget(self.plot_button_2d)

        self.result_browser = QTextBrowser()
        layout.addWidget(self.result_browser)

    def replace_absolute_value(self, expr_str):
        def repl(match):
            inner_expr = match.group(1)
            return f'Abs({inner_expr})'
        expr_str = re.sub(r'\|([^|]+)\|', repl, expr_str)
        return expr_str

    def plot_graphs_2d(self):
        self.result_browser.clear()
        equations_input = self.entry_2d.text()
        try:
            if self.canvas:
                self.canvas.mpl_disconnect(self.cid_press)
                self.canvas.mpl_disconnect(self.cid_motion)
                self.canvas.mpl_disconnect(self.cid_release)
                self.canvas.setParent(None)
                self.toolbar.setParent(None)

            equations = equations_input.strip().split()
            if not equations:
                self.result_browser.setText("Please enter at least one equation.")
                return

            x = sp.symbols('x')
            allowed_symbols = {'x'}
            transformations = standard_transformations + (
                implicit_multiplication_application, implicit_application, convert_xor)
            local_dict = {
                'x': x, 'e': np.e, 'pi': np.pi, 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'log': sp.log, 'sqrt': sp.sqrt, 'Abs': sp.Abs, 'exp': sp.exp, 'ln': sp.log
            }

            self.x_vals = np.linspace(-10, 10, 800)
            modules = {
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log,
                'sqrt': np.sqrt, 'Abs': np.abs, 'exp': np.exp, 'ln': np.log,
                'e': np.e, 'pi': np.pi
            }

            fig, self.ax = plt.subplots(figsize=(6, 5))

            colors = plt.cm.tab10.colors
            self.y_vals_list = []
            self.expr_list = []
            self.lines = []

            result_text = ""

            for idx, equation in enumerate(equations):
                equation = self.replace_absolute_value(equation)
                expr = parse_expr(
                    equation, transformations=transformations, local_dict=local_dict)

                symbols_in_expr = expr.free_symbols
                if not symbols_in_expr.issubset({x}):
                    unsupported_vars = symbols_in_expr - {x}
                    var_names = ', '.join(str(var) for var in unsupported_vars)
                    self.result_browser.setText(
                        f"Error: Unsupported variables in equation {idx+1}: {var_names}")
                    return

                self.expr_list.append(expr)
                y_func = sp.lambdify(x, expr, modules=[modules, "numpy"])
                y_vals = y_func(self.x_vals)
                self.y_vals_list.append(y_vals)

                line, = self.ax.plot(
                    self.x_vals, y_vals, color=colors[idx % len(colors)],
                    label=f"${sp.latex(expr)}$")
                self.lines.append(line)

                properties = self.compute_function_properties(expr)
                result_text += f"Equation {idx+1}: {equation}\n"
                for prop_name, prop_value in properties.items():
                    result_text += f"{prop_name}: {prop_value}\n"
                result_text += "\n"

            intersections = self.find_intersections()

            if intersections:
                x_ints, y_ints = zip(*intersections)
                self.ax.plot(x_ints, y_ints, 'ko', label='Intersections')

            self.ax.set_xlim([-10, 10])
            self.ax.set_ylim(
                [np.nanmin([np.nanmin(y) for y in self.y_vals_list]),
                 np.nanmax([np.nanmax(y) for y in self.y_vals_list])])
            self.ax.grid(True)

            self.ax.spines['left'].set_position('zero')
            self.ax.spines['bottom'].set_position('zero')
            self.ax.spines['right'].set_color('none')
            self.ax.spines['top'].set_color('none')
            self.ax.xaxis.set_ticks_position('bottom')
            self.ax.yaxis.set_ticks_position('left')

            self.ax.set_xlabel('')
            self.ax.set_ylabel('')

            for label in self.ax.get_xticklabels():
                label.set_fontsize(8)
            for label in self.ax.get_yticklabels():
                label.set_fontsize(8)

            self.ax.legend(loc='upper left', fontsize=8)

            self.canvas = FigureCanvas(fig)
            self.toolbar = NavigationToolbar(self.canvas, self)
            layout = self.centralWidget().layout()
            layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)

            self.canvas.installEventFilter(self)

            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
            self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)

            self.canvas.draw()

            self.result_browser.setText(result_text)

        except Exception as e:
            self.result_browser.setText(f"Error: {e}")

    def compute_function_properties(self, expr):
        x = sp.symbols('x')
        properties = {}

        try:
            x_intercepts = sp.solve(expr, x)
            properties['Zeroes (x-intercepts)'] = x_intercepts
        except Exception as e:
            properties['Zeroes (x-intercepts)'] = 'Cannot compute zeroes.'

        try:
            y_intercept = expr.subs(x, 0)
            properties['Y-intercept'] = y_intercept
        except Exception as e:
            properties['Y-intercept'] = 'Cannot compute Y-intercept.'

        try:
            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)
            properties['End behavior'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
        except Exception as e:
            properties['End behavior'] = 'Cannot compute end behavior.'

        try:
            derivative = sp.diff(expr, x)
            properties['First derivative'] = derivative

            critical_points = sp.solve(derivative, x)
            properties['Critical points'] = critical_points
        except Exception as e:
            properties['First derivative'] = 'Cannot compute derivative.'

        try:
            domain = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
            properties['Domain'] = domain
        except Exception as e:
            properties['Domain'] = 'Cannot compute domain.'

        try:
            critical_points = sp.solve(sp.diff(expr, x), x)
            test_points = critical_points + [domain.inf, domain.sup]
            y_vals = []
            for point in test_points:
                if point.is_real or point.is_infinite:
                    y_val = expr.subs(x, point).evalf()
                    if y_val.is_real:
                        y_vals.append(y_val)

            y_min = min(y_vals)
            y_max = max(y_vals)

            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)

            if limit_pos_inf == sp.oo or limit_neg_inf == sp.oo:
                y_max = '∞'
            if limit_pos_inf == -sp.oo or limit_neg_inf == -sp.oo:
                y_min = '-∞'

            properties['Range'] = f"[{y_min}, {y_max}]"
        except Exception as e:
            properties['Range'] = 'Cannot compute range.'

        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)
            if discontinuities:
                properties['Vertical asymptotes'] = list(discontinuities)
            else:
                properties['Vertical asymptotes'] = 'No vertical asymptotes.'
            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)

            if limit_pos_inf.is_finite and limit_neg_inf.is_finite:
                if limit_pos_inf == limit_neg_inf:
                    properties['Horizontal asymptote'] = limit_pos_inf
                else:
                    properties['Horizontal asymptote'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
            else:
                properties['Horizontal asymptote'] = 'No horizontal asymptote.'
        except Exception as e:
            properties['Asymptotes'] = 'Cannot compute asymptotes.'

        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)
            if discontinuities:
                properties['Discontinuities'] = list(discontinuities)
            else:
                properties['Discontinuities'] = 'No discontinuities.'
        except Exception as e:
            properties['Discontinuities'] = 'Cannot compute discontinuities.'

        try:
            second_derivative = sp.diff(expr, x, 2)
            properties['Second derivative'] = second_derivative

            extrema = []
            for cp in critical_points:
                if cp.is_real:
                    f_cp = expr.subs(x, cp)
                    fpp_cp = second_derivative.subs(x, cp)
                    if fpp_cp.is_real:
                        if fpp_cp > 0:
                            extrema.append((cp, f_cp, 'Local minimum'))
                        elif fpp_cp < 0:
                            extrema.append((cp, f_cp, 'Local maximum'))
                        else:
                            extrema.append((cp, f_cp, 'Inflection point'))
            properties['Local extrema'] = extrema
        except Exception as e:
            properties['Local extrema'] = 'Cannot compute local extrema.'

        return properties

    def find_intersections(self):
        intersections = []
        x = sp.symbols('x')

        for i, j in combinations(range(len(self.expr_list)), 2):
            expr1 = self.expr_list[i]
            expr2 = self.expr_list[j]
            try:
                sol = sp.solve(expr1 - expr2, x)
                for s in sol:
                    if s.is_real and -10 <= s.evalf() <= 10:
                        y_val = expr1.subs(x, s).evalf()
                        if y_val.is_real:
                            intersections.append((float(s.evalf()), float(y_val)))
            except Exception as e:
                continue

        unique_intersections = list(set(intersections))
        return unique_intersections

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 1:
            self.pressing = True
            self.selected_graph_index = None
            self.update_dot(event)

    def on_motion(self, event):
        if not self.pressing:
            return
        if event.inaxes != self.ax:
            return
        self.update_dot(event)

    def on_release(self, event):
        if event.button == 1:
            self.pressing = False
            self.selected_graph_index = None
            if self.dot:
                self.dot.remove()
                self.dot = None
            if self.text_annotation:
                self.text_annotation.remove()
                self.text_annotation = None
            self.canvas.draw_idle()

    def update_dot(self, event):
        x = event.xdata
        y = event.ydata

        if x is None or y is None:
            return

        x_threshold = 0.2

        x_int = round(x)
        delta_x = abs(x - x_int)

        if delta_x < x_threshold:
            x_snap = x_int
        else:
            x_snap = x

        if self.selected_graph_index is None:
            y_curves = []
            for y_vals in self.y_vals_list:
                if self.x_vals[0] <= x_snap <= self.x_vals[-1]:
                    y_curve = np.interp(x_snap, self.x_vals, y_vals)
                else:
                    y_curve = np.nan
                y_curves.append(y_curve)

            distances = [abs(y - y_curve) for y_curve in y_curves]
            valid_distances = [(dist, idx) for idx, dist in enumerate(distances) if not np.isnan(dist)]
            if not valid_distances:
                return
            min_distance, min_index = min(valid_distances, key=lambda t: t[0])
            y_curve = y_curves[min_index]

            y_threshold = 0.5

            if min_distance < y_threshold:
                self.selected_graph_index = min_index
            else:
                return

        y_vals = self.y_vals_list[self.selected_graph_index]
        if self.x_vals[0] <= x_snap <= self.x_vals[-1]:
            y_curve = np.interp(x_snap, self.x_vals, y_vals)
        else:
            return

        if self.dot:
            self.dot.remove()
        if self.text_annotation:
            self.text_annotation.remove()

        self.dot = self.ax.plot(x_snap, y_curve, 'ro')[0]

        x_display = round(x_snap, 2)
        y_display = round(y_curve, 2)
        equation_label = f"${sp.latex(self.expr_list[self.selected_graph_index])}$"
        self.text_annotation = self.ax.text(
            x_snap, y_curve + (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.03,
            f"({x_display}, {y_display})\n{equation_label}",
            fontsize=9, color='black', ha='center', va='bottom'
        )

        self.canvas.draw_idle()

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.NativeGesture:
            return self.nativeGestureEvent(event)
        elif event.type() == QEvent.Type.Wheel:
            self.wheelEvent(event)
            return event.isAccepted()
        return super(GraphingCalculator, self).eventFilter(source, event)

    def nativeGestureEvent(self, event):
        if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
            scale_factor = 1 / (1 + event.value())
            self.zoom(scale_factor, event)
            return True
        return False

    def wheelEvent(self, event):
        if event.angleDelta().y() != 0:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.angleDelta().y() > 0:
                    scale_factor = 0.9
                else:
                    scale_factor = 1.1
                self.zoom(scale_factor, event)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def zoom(self, scale_factor, event):
        ax = self.canvas.figure.axes[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        if hasattr(event, 'position'):
            xdata = event.position().x()
            ydata = event.position().y()
        else:
            xdata = event.x()
            ydata = event.y()
        xdata, ydata = ax.transData.inverted().transform([xdata, ydata])

        new_xlim = [xdata + (x - xdata) * scale_factor for x in xlim]
        new_ylim = [ydata + (y - ydata) * scale_factor for y in ylim]
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)

        self.canvas.draw_idle()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphingCalculator()
    window.show()
    sys.exit(app.exec())
