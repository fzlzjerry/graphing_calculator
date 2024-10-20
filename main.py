import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton
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
        self.pressing = False  # Flag to track mouse press state
        self.dot = None  # To store the dot artist
        self.text_annotation = None  # To store the text annotation
        self.selected_graph_index = None  # Index of the graph currently being tracked
        self.cid_press = None  # Event connection IDs
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

        self.plot_button_2d = QPushButton("Plot 2D Graphs")
        self.plot_button_2d.clicked.connect(self.plot_graphs_2d)
        layout.addWidget(self.plot_button_2d)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    def replace_absolute_value(self, expr_str):
        def repl(match):
            inner_expr = match.group(1)
            return f'Abs({inner_expr})'
        expr_str = re.sub(r'\|([^|]+)\|', repl, expr_str)
        return expr_str

    def plot_graphs_2d(self):
        self.result_label.setText("")
        equations_input = self.entry_2d.text()
        try:
            # Disconnect previous events
            if self.canvas:
                self.canvas.mpl_disconnect(self.cid_press)
                self.canvas.mpl_disconnect(self.cid_motion)
                self.canvas.mpl_disconnect(self.cid_release)
                self.canvas.setParent(None)
                self.toolbar.setParent(None)

            # Split the input into separate equations
            equations = equations_input.strip().split()
            if not equations:
                self.result_label.setText("Please enter at least one equation.")
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

            colors = plt.cm.tab10.colors  # Get a list of colors
            self.y_vals_list = []  # To store y-values for each equation
            self.expr_list = []  # To store expressions
            self.lines = []  # To store line objects

            for idx, equation in enumerate(equations):
                equation = self.replace_absolute_value(equation)
                expr = parse_expr(
                    equation, transformations=transformations, local_dict=local_dict)

                # Check for unsupported variables
                symbols_in_expr = expr.free_symbols
                if not symbols_in_expr.issubset({x}):
                    unsupported_vars = symbols_in_expr - {x}
                    var_names = ', '.join(str(var) for var in unsupported_vars)
                    self.result_label.setText(
                        f"Error: Unsupported variable(s) in equation {idx+1}: {var_names}")
                    return

                self.expr_list.append(expr)
                y_func = sp.lambdify(x, expr, modules=[modules, "numpy"])
                y_vals = y_func(self.x_vals)
                self.y_vals_list.append(y_vals)

                # Plot each graph with a different color and label
                line, = self.ax.plot(
                    self.x_vals, y_vals, color=colors[idx % len(colors)],
                    label=f"${sp.latex(expr)}$")
                self.lines.append(line)

            # Find intersection points
            intersections = self.find_intersections()

            # Plot intersection points
            if intersections:
                x_ints, y_ints = zip(*intersections)
                self.ax.plot(x_ints, y_ints, 'ko', label='Intersections')

            # Set up the plot
            self.ax.set_xlim([-10, 10])
            self.ax.set_ylim(
                [np.nanmin([np.nanmin(y) for y in self.y_vals_list]),
                 np.nanmax([np.nanmax(y) for y in self.y_vals_list])])
            self.ax.grid(True)

            # Adjust axes to cross at zero
            self.ax.spines['left'].set_position('zero')
            self.ax.spines['bottom'].set_position('zero')
            self.ax.spines['right'].set_color('none')
            self.ax.spines['top'].set_color('none')
            self.ax.xaxis.set_ticks_position('bottom')
            self.ax.yaxis.set_ticks_position('left')

            # Remove edge labels
            self.ax.set_xlabel('')
            self.ax.set_ylabel('')

            for label in self.ax.get_xticklabels():
                label.set_fontsize(8)
            for label in self.ax.get_yticklabels():
                label.set_fontsize(8)

            # Add legend
            self.ax.legend(loc='upper left', fontsize=8)

            self.canvas = FigureCanvas(fig)
            self.toolbar = NavigationToolbar(self.canvas, self)
            layout = self.centralWidget().layout()
            layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)

            # Install event filter
            self.canvas.installEventFilter(self)

            # Connect mouse events
            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
            self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)

            self.canvas.draw()

        except Exception as e:
            self.result_label.setText(f"Error: {e}")

    def find_intersections(self):
        intersections = []
        x = sp.symbols('x')

        # Generate combinations of equations
        for i, j in combinations(range(len(self.expr_list)), 2):
            expr1 = self.expr_list[i]
            expr2 = self.expr_list[j]
            # Solve expr1 - expr2 = 0
            try:
                sol = sp.solve(expr1 - expr2, x)
                for s in sol:
                    # Only consider real solutions within the plotting range
                    if s.is_real and -10 <= s.evalf() <= 10:
                        y_val = expr1.subs(x, s).evalf()
                        if y_val.is_real:
                            intersections.append((float(s.evalf()), float(y_val)))
            except Exception as e:
                continue  # Skip if unable to solve

        # Remove duplicate points (if any)
        unique_intersections = list(set(intersections))
        return unique_intersections

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 1:  # Left mouse button
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
        if event.button == 1:  # Left mouse button
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

        # Snapping threshold for x-coordinate
        x_threshold = 0.2  # Adjust this value to change x snapping sensitivity

        # Calculate distance to the nearest integer x-value
        x_int = round(x)
        delta_x = abs(x - x_int)

        if delta_x < x_threshold:
            x_snap = x_int
        else:
            x_snap = x

        # If no graph is selected yet, select the closest one
        if self.selected_graph_index is None:
            # Get y-values of all curves at x_snap
            y_curves = []
            for y_vals in self.y_vals_list:
                if self.x_vals[0] <= x_snap <= self.x_vals[-1]:
                    y_curve = np.interp(x_snap, self.x_vals, y_vals)
                else:
                    y_curve = np.nan
                y_curves.append(y_curve)

            # Calculate distances from the mouse position to each curve at (x_snap, y_curve)
            distances = [abs(y - y_curve) for y_curve in y_curves]
            # Exclude NaN values
            valid_distances = [(dist, idx) for idx, dist in enumerate(distances) if not np.isnan(dist)]
            if not valid_distances:
                return  # No valid distances
            min_distance, min_index = min(valid_distances, key=lambda t: t[0])
            y_curve = y_curves[min_index]

            # Snapping threshold for vertical distance
            y_threshold = 0.5  # Adjust this value to change y snapping sensitivity

            if min_distance < y_threshold:
                self.selected_graph_index = min_index
            else:
                return  # Do not create dot if not close enough

        # Now, update the dot along the selected graph
        y_vals = self.y_vals_list[self.selected_graph_index]
        if self.x_vals[0] <= x_snap <= self.x_vals[-1]:
            y_curve = np.interp(x_snap, self.x_vals, y_vals)
        else:
            return  # x_snap is out of range

        # Remove previous dot and annotation if they exist
        if self.dot:
            self.dot.remove()
        if self.text_annotation:
            self.text_annotation.remove()

        # Plot new dot
        self.dot = self.ax.plot(x_snap, y_curve, 'ro')[0]

        # Display coordinates above the dot, including which equation
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
            return self.wheelEvent(event)
        return super(GraphingCalculator, self).eventFilter(source, event)

    def nativeGestureEvent(self, event):
        if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
            scale_factor = 1 / (1 + event.value())
            self.zoom(scale_factor, event)
            return True
        return False

    def wheelEvent(self, event):
        if event.angleDelta().y() != 0:
            # Mouse wheel event
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # Zoom when Ctrl key is pressed
                if event.angleDelta().y() > 0:
                    scale_factor = 0.9
                else:
                    scale_factor = 1.1
                self.zoom(scale_factor, event)
                return True
        return False

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
