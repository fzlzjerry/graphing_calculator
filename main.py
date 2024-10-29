import sys
import re
import requests
import semver
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTextBrowser, QMessageBox, QSizePolicy, QSplitter, QFileDialog
)
from PyQt6.QtCore import Qt, QEvent, QThread, pyqtSignal
from PyQt6.QtGui import QWheelEvent, QNativeGestureEvent
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor, implicit_application
)
from sympy.functions.special.bessel import jn, yn
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
import matplotlib
import matplotlib.pyplot as plt
from itertools import combinations
from scipy import special

matplotlib.use('QtAgg')

class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(str)
    up_to_date = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, owner, repo, current_version):
        super().__init__()
        self.owner = owner
        self.repo = repo
        self.current_version = current_version

    def run(self):
        try:
            url = f'https://api.github.com/repos/{self.owner}/{self.repo}/releases'
            response = requests.get(url)
            if response.status_code == 200:
                releases = response.json()
                if releases:
                    latest_release = releases[0]
                    latest_version = latest_release['tag_name']
                    cleaned_version = self.clean_version(latest_version)
                    cleaned_current_version = self.clean_version(self.current_version)
                    if semver.VersionInfo.parse(cleaned_version) > semver.VersionInfo.parse(cleaned_current_version):
                        self.update_available.emit(latest_version)
                    else:
                        self.up_to_date.emit()
                else:
                    self.error.emit('No releases found.')
            else:
                self.error.emit(f'Failed to fetch releases. Status code: {response.status_code}')
        except Exception as e:
            self.error.emit(str(e))

    @staticmethod
    def clean_version(version):
        version = version.lstrip('v')
        version = version.split('-')[0]
        return version

class GraphingCalculator(QMainWindow):
    GITHUB_OWNER = 'fzlzjerry'
    GITHUB_REPO = 'graphing_calculator'
    current_version = 'v1.0.2'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphing Calculator")
        self.resize(800, 1000)
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
        self.panning = False
        self.pan_start = None
        self.expr_list = []
        self.lines = []
        self.y_funcs_list = []
        self.x_vals = None

    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)
        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)
        top_layout = QHBoxLayout()
        self.label_2d = QLabel("Enter 2D equations (separated by spaces):")
        top_layout.addWidget(self.label_2d)
        self.entry_2d = QLineEdit()
        top_layout.addWidget(self.entry_2d)
        self.update_button = QPushButton("Check for Updates")
        self.update_button.setFixedSize(150, 30)
        self.update_button.clicked.connect(self.check_for_updates)
        top_layout.addWidget(self.update_button)
        upper_layout.addLayout(top_layout)
        self.plot_button_2d = QPushButton("Plot 2D Graphs")
        self.plot_button_2d.clicked.connect(self.plot_graphs_2d)
        upper_layout.addWidget(self.plot_button_2d)
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Graphs")
        self.save_button.clicked.connect(self.save_graphs)
        buttons_layout.addWidget(self.save_button)
        self.load_button = QPushButton("Load Graphs")
        self.load_button.clicked.connect(self.load_graphs)
        buttons_layout.addWidget(self.load_button)
        self.export_button = QPushButton("Export Graph")
        self.export_button.clicked.connect(self.export_graph)
        buttons_layout.addWidget(self.export_button)
        upper_layout.addLayout(buttons_layout)
        self.result_browser = QTextBrowser()
        upper_layout.addWidget(self.result_browser)
        splitter.addWidget(upper_widget)
        self.plot_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_widget)
        splitter.addWidget(self.plot_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)

    def check_for_updates(self):
        self.update_thread = UpdateCheckerThread(
            owner=self.GITHUB_OWNER,
            repo=self.GITHUB_REPO,
            current_version=self.current_version
        )
        self.update_thread.update_available.connect(self.on_update_available)
        self.update_thread.up_to_date.connect(self.on_up_to_date)
        self.update_thread.error.connect(self.on_update_error)
        self.update_thread.start()

    def on_update_available(self, latest_version):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Update Available")
        msg_box.setText(f"A new version ({latest_version}) is available.")
        msg_box.setInformativeText("Would you like to visit the GitHub releases page to download the latest version?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        ret = msg_box.exec()
        if ret == QMessageBox.StandardButton.Yes:
            import webbrowser
            url = f'https://github.com/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/releases'
            webbrowser.open(url)

    def on_up_to_date(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("No Updates")
        msg_box.setText("You are using the latest version.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def on_update_error(self, error_message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Update Check Failed")
        msg_box.setText("Could not check for updates.")
        msg_box.setInformativeText(error_message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def replace_absolute_value(self, expr_str):
        def repl(match):
            inner_expr = match.group(1)
            return f'Abs({inner_expr})'
        expr_str = re.sub(r'\|([^|]+)\|', repl, expr_str)
        return expr_str

    def replace_inverse_trig_functions(self, expr_str):
        def repl(match):
            func = match.group(1)
            arg = match.group(2)
            return f'a{func}({arg})'
        patterns = [
            r'(sin|cos|tan)\^-1\s*(\([^)]*\)|\w+)',
            r'(sin|cos|tan)⁻¹\s*(\([^)]*\)|\w+)'
        ]
        for pattern in patterns:
            expr_str = re.sub(pattern, repl, expr_str)
        return expr_str

    def plot_graphs_2d(self):
        self.result_browser.clear()
        equations_input = self.entry_2d.text()
        try:
            if self.canvas:
                self.canvas.mpl_disconnect(self.cid_press)
                self.canvas.mpl_disconnect(self.cid_motion)
                self.canvas.mpl_disconnect(self.cid_release)
                self.plot_layout.removeWidget(self.canvas)
                self.canvas.setParent(None)
            if self.toolbar:
                self.plot_layout.removeWidget(self.toolbar)
                self.toolbar.setParent(None)
            equations = equations_input.strip().split()
            if not equations:
                self.result_browser.setText("Please enter at least one equation.")
                return
            x = sp.symbols('x')
            transformations = standard_transformations + (
                implicit_multiplication_application, implicit_application, convert_xor)
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
            fig, self.ax = plt.subplots(figsize=(10, 8))
            colors = plt.cm.tab10.colors
            self.y_funcs_list = []
            self.expr_list = []
            self.lines = []
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
            result_text = ""
            for idx, equation in enumerate(equations):
                try:
                    equation = self.replace_absolute_value(equation)
                    equation = self.replace_inverse_trig_functions(equation)
                    expr = parse_expr(
                        equation, transformations=transformations, local_dict=local_dict)
                    symbols_in_expr = expr.free_symbols
                    if not symbols_in_expr.issubset({x}):
                        unsupported_vars = symbols_in_expr - {x}
                        var_names = ', '.join(str(var) for var in unsupported_vars)
                        self.result_browser.setText(
                            f"Error: Equation {idx + 1} contains unsupported variables: {var_names}")
                        return
                    self.expr_list.append(expr)
                    x_vals = np.linspace(-10, 10, 800)
                    y_func = sp.lambdify(x, expr, modules=[self.modules, "numpy"])
                    y_vals = y_func(x_vals)
                    self.y_funcs_list.append(y_func)
                    line, = self.ax.plot(
                        x_vals, y_vals, color=colors[idx % len(colors)],
                        label=f"${sp.latex(expr)}$")
                    self.lines.append(line)
                    properties = self.compute_function_properties(expr)
                    result_text += f"Equation {idx + 1}: {equation}\n"
                    for prop_name, prop_value in properties.items():
                        result_text += f"{prop_name}: {prop_value}\n"
                    result_text += "\n"
                except Exception as e:
                    self.result_browser.setText(f"Error processing equation {idx + 1}: {str(e)}")
                    return
            self.update_intersections()
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
                label.set_fontsize(10)
            for label in self.ax.get_yticklabels():
                label.set_fontsize(10)
            self.ax.legend(loc='upper left', fontsize=10)
            self.canvas = FigureCanvas(fig)
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.plot_layout.addWidget(self.toolbar)
            self.plot_layout.addWidget(self.canvas)
            self.canvas.installEventFilter(self)
            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
            self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
            self.canvas.draw()
            self.result_browser.setText(result_text)
        except Exception as e:
            self.result_browser.setText(f"An unexpected error occurred: {str(e)}")
            return

    def compute_function_properties(self, expr):
        x = sp.symbols('x')
        properties = {}
        try:
            x_intercepts = sp.solve(expr, x)
            properties['X-Intercepts'] = x_intercepts
        except Exception as e:
            properties['X-Intercepts'] = 'Unable to calculate x-intercepts.'
        try:
            y_intercept = expr.subs(x, 0)
            properties['Y-Intercept'] = y_intercept
        except Exception as e:
            properties['Y-Intercept'] = 'Unable to calculate y-intercept.'
        try:
            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)
            properties['Function End Behavior'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
        except Exception as e:
            properties['Function End Behavior'] = 'Unable to calculate function end behavior.'
        try:
            derivative = sp.diff(expr, x)
            properties['First Derivative'] = derivative
            critical_points = sp.solve(derivative, x)
            properties['Critical Points'] = critical_points
        except Exception as e:
            properties['First Derivative'] = 'Unable to calculate first derivative.'
        try:
            domain = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
            properties['Domain'] = domain
        except Exception as e:
            properties['Domain'] = 'Unable to calculate domain.'
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
            properties['Range'] = 'Unable to calculate range.'
        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)
            if discontinuities:
                properties['Vertical Asymptotes'] = list(discontinuities)
            else:
                properties['Vertical Asymptotes'] = 'No vertical asymptotes.'
            limit_pos_inf = sp.limit(expr, x, sp.oo)
            limit_neg_inf = sp.limit(expr, x, -sp.oo)
            if limit_pos_inf.is_finite and limit_neg_inf.is_finite:
                if limit_pos_inf == limit_neg_inf:
                    properties['Horizontal Asymptote'] = limit_pos_inf
                else:
                    properties['Horizontal Asymptotes'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
            else:
                properties['Horizontal Asymptotes'] = 'No horizontal asymptotes.'
        except Exception as e:
            properties['Asymptotes'] = 'Unable to calculate asymptotes.'
        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)
            if discontinuities:
                properties['Discontinuities'] = list(discontinuities)
            else:
                properties['Discontinuities'] = 'No discontinuities.'
        except Exception as e:
            properties['Discontinuities'] = 'Unable to calculate discontinuities.'
        try:
            second_derivative = sp.diff(expr, x, 2)
            properties['Second Derivative'] = second_derivative
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
        except Exception as e:
            properties['Extrema'] = 'Unable to calculate extrema.'
        return properties

    def update_intersections(self):
        if hasattr(self, 'intersection_points'):
            for point in self.intersection_points:
                point.remove()
        self.intersection_points = []
        intersections = self.find_intersections()
        if intersections:
            x_ints, y_ints = zip(*intersections)
            points = self.ax.plot(x_ints, y_ints, 'ko', label='Intersections')
            self.intersection_points.extend(points)

    def find_intersections(self):
        intersections = []
        combinations_indices = list(combinations(range(len(self.y_funcs_list)), 2))
        x_min, x_max = self.ax.get_xlim()
        x_vals = np.linspace(x_min, x_max, 800)
        y_vals_list = []
        for y_func in self.y_funcs_list:
            y_vals = y_func(x_vals)
            y_vals_list.append(y_vals)
        for i, j in combinations_indices:
            y_vals1 = y_vals_list[i]
            y_vals2 = y_vals_list[j]
            diff = y_vals1 - y_vals2
            diff = np.where(np.isnan(diff), np.inf, diff)
            diff = np.where(np.isinf(diff), np.inf, diff)
            sign_diff = np.sign(diff)
            sign_changes = np.where(np.diff(sign_diff) != 0)[0]
            for idx in sign_changes:
                x1, x2 = x_vals[idx], x_vals[idx + 1]
                y1_diff, y2_diff = diff[idx], diff[idx + 1]
                if np.isfinite(y1_diff) and np.isfinite(y2_diff):
                    x_zero = x1 - y1_diff * (x2 - x1) / (y2_diff - y1_diff)
                    y_zero = self.y_funcs_list[i](x_zero)
                    intersections.append((x_zero, y_zero))
        unique_intersections = list({(round(x, 5), round(y, 5)) for x, y in intersections})
        return unique_intersections

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 1:
            self.pressing = True
            self.selected_graph_index = None
            self.update_dot(event)
        elif event.button == 2:
            self.panning = True
            self.pan_start = (event.xdata, event.ydata)

    def on_motion(self, event):
        if event.inaxes != self.ax:
            return
        if self.panning and self.pan_start:
            x_start, y_start = self.pan_start
            x_curr, y_curr = event.xdata, event.ydata
            if x_curr is None or y_curr is None:
                return
            dx = x_start - x_curr
            dy = y_start - y_curr
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.set_xlim(xlim + dx)
            self.ax.set_ylim(ylim + dy)
            self.canvas.draw_idle()
            self.pan_start = (x_curr, y_curr)
            self.update_plot()
        elif self.pressing:
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
        elif event.button == 2:
            self.panning = False
            self.pan_start = None

    def update_dot(self, event):
        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return
        x_range = self.ax.get_xlim()
        x_scale = x_range[1] - x_range[0]
        y_range = self.ax.get_ylim()
        y_scale = y_range[1] - y_range[0]
        x_threshold = x_scale * 0.01
        intersection_threshold = x_scale * 0.025
        y_threshold = y_scale * 0.025
        x_int = round(x)
        delta_x = abs(x - x_int)
        if delta_x < x_threshold:
            x_snap = x_int
        else:
            x_snap = x
        snapped_to_intersection = False
        intersections = self.find_intersections()
        for x_ints, y_ints in intersections:
            if abs(x_snap - x_ints) < intersection_threshold and abs(y - y_ints) < y_threshold:
                x_snap = x_ints
                y = y_ints
                snapped_to_intersection = True
                break
        if self.selected_graph_index is None and not snapped_to_intersection:
            y_curves = []
            for y_func in self.y_funcs_list:
                y_curve = y_func(x_snap)
                if np.isfinite(y_curve):
                    y_curves.append(y_curve)
                else:
                    y_curves.append(np.nan)
            distances = [abs(y - y_curve) for y_curve in y_curves]
            valid_distances = [(dist, idx) for idx, dist in enumerate(distances) if not np.isnan(dist)]
            if not valid_distances:
                return
            min_distance, min_index = min(valid_distances, key=lambda t: t[0])
            y_curve = y_curves[min_index]
            if min_distance < y_threshold:
                self.selected_graph_index = min_index
            else:
                return
        if self.selected_graph_index is not None:
            y_func = self.y_funcs_list[self.selected_graph_index]
            y_curve = y_func(x_snap)
            if not np.isfinite(y_curve):
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
                x_snap,
                y_curve + (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.03,
                f"({x_display}, {y_display})\n{equation_label}",
                fontsize=10,
                color='black',
                ha='center',
                va='bottom'
            )
            self.canvas.draw_idle()

    def update_plot(self):
        for line in self.lines:
            line.remove()
        self.lines.clear()
        x_min, x_max = self.ax.get_xlim()
        x_vals = np.linspace(x_min, x_max, 800)
        colors = plt.cm.tab10.colors
        for idx, (expr, y_func) in enumerate(zip(self.expr_list, self.y_funcs_list)):
            y_vals = y_func(x_vals)
            line, = self.ax.plot(
                x_vals, y_vals, color=colors[idx % len(colors)],
                label=f"${sp.latex(expr)}$")
            self.lines.append(line)
        if hasattr(self.ax, 'legend_') and self.ax.legend_:
            self.ax.legend_.remove()
        self.ax.legend(loc='upper left', fontsize=10)
        self.update_intersections()
        self.ax.figure.canvas.draw_idle()

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
        angle_delta = event.angleDelta()
        delta_x = angle_delta.x()
        delta_y = angle_delta.y()
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if delta_y > 0:
                scale_factor = 0.9
            else:
                scale_factor = 1.1
            self.zoom(scale_factor, event)
            event.accept()
        else:
            self.pan_wheel(delta_x, delta_y, event)
            event.accept()

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
        self.update_plot()

    def pan_wheel(self, delta_x, delta_y, event):
        ax = self.canvas.figure.axes[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        dx = -delta_x * (xlim[1] - xlim[0]) / 1000
        dy = delta_y * (ylim[1] - ylim[0]) / 1000
        ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
        ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
        self.canvas.draw_idle()
        self.update_plot()

    def save_graphs(self):
        options = QFileDialog.Option(0)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Graphs", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                equations = self.entry_2d.text()
                with open(file_name, 'w') as f:
                    f.write(equations)
                QMessageBox.information(self, "Success", "Graphs saved successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while saving graphs: {str(e)}")

    def load_graphs(self):
        options = QFileDialog.Option(0)
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Graphs", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    equations = f.read()
                self.entry_2d.setText(equations)
                QMessageBox.information(self, "Success", "Graphs loaded successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred while loading graphs: {str(e)}")

    def export_graph(self):
        if self.canvas:
            options = QFileDialog.Option(0)
            file_name, _ = QFileDialog.getSaveFileName(self, "Export Graph", "", "PNG Files (*.png);;SVG Files (*.svg);;All Files (*)", options=options)
            if file_name:
                try:
                    self.canvas.figure.savefig(file_name)
                    QMessageBox.information(self, "Success", "Graph exported successfully.")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"An error occurred while exporting the graph: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No graph to export.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphingCalculator()
    window.show()
    sys.exit(app.exec())
