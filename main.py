import sys  # Import system-specific parameters and functions
import re  # Import regular expressions module

from PyQt6.QtWidgets import (  # Import PyQt6 widgets for GUI components
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTextBrowser
)
from PyQt6.QtCore import Qt, QEvent  # Import core Qt functionality
from PyQt6.QtGui import QWheelEvent, QNativeGestureEvent  # Import GUI events
import numpy as np  # Import NumPy for numerical operations
import sympy as sp  # Import SymPy for symbolic mathematics
from sympy.parsing.sympy_parser import (  # Import SymPy parsing tools
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor, implicit_application
)
from matplotlib.backends.backend_qtagg import (  # Import Matplotlib backends for Qt
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
import matplotlib  # Import Matplotlib for plotting
import matplotlib.pyplot as plt  # Import Matplotlib's pyplot interface
from itertools import combinations  # Import combinations function

matplotlib.use('QtAgg')  # Use QtAgg backend for Matplotlib


class GraphingCalculator(QMainWindow):  # Define the main window class
    def __init__(self):
        super().__init__()  # Initialize the parent class
        self.setWindowTitle("Graphing Calculator")  # Set window title

        # Set the default window size (width x height in pixels)
        self.resize(600, 1400)

        self.initUI()  # Initialize the user interface
        self.canvas = None  # Placeholder for the Matplotlib canvas
        self.toolbar = None  # Placeholder for the Matplotlib toolbar
        self.pressing = False  # Flag to track if the mouse button is pressed
        self.dot = None  # Placeholder for the point annotation
        self.text_annotation = None  # Placeholder for the text annotation
        self.selected_graph_index = None  # Index of the selected graph
        self.cid_press = None  # Connection ID for mouse press event
        self.cid_motion = None  # Connection ID for mouse motion event
        self.cid_release = None  # Connection ID for mouse release event
        self.panning = False  # Flag to track panning state
        self.pan_start = None  # Starting point for panning

        self.expr_list = []  # List to store expressions
        self.lines = []  # List to store line objects
        self.y_funcs_list = []  # List to store y-functions
        self.x_vals = None  # Placeholder for x-values

    def initUI(self):
        widget = QWidget()  # Create a central widget
        self.setCentralWidget(widget)  # Set the central widget
        layout = QVBoxLayout(widget)  # Create a vertical box layout

        self.label_2d = QLabel("Enter 2D equations (separated by spaces):")  # Label for input
        layout.addWidget(self.label_2d)  # Add label to layout
        self.entry_2d = QLineEdit()  # Line edit for equation input
        layout.addWidget(self.entry_2d)  # Add line edit to layout

        self.plot_button_2d = QPushButton("Plot 2D Graphs")  # Button to plot graphs
        self.plot_button_2d.clicked.connect(self.plot_graphs_2d)  # Connect button to method
        layout.addWidget(self.plot_button_2d)  # Add button to layout

        self.result_browser = QTextBrowser()  # Text browser to display results
        layout.addWidget(self.result_browser)  # Add text browser to layout

    def replace_absolute_value(self, expr_str):
        # Replace absolute value notation with SymPy's Abs function
        def repl(match):
            inner_expr = match.group(1)
            return f'Abs({inner_expr})'

        expr_str = re.sub(r'\|([^|]+)\|', repl, expr_str)  # Substitute using regex
        return expr_str  # Return modified expression string

    def plot_graphs_2d(self):
        self.result_browser.clear()  # Clear the result display
        equations_input = self.entry_2d.text()  # Get input from user
        try:
            # If a canvas already exists, disconnect events and remove it
            if self.canvas:
                self.canvas.mpl_disconnect(self.cid_press)
                self.canvas.mpl_disconnect(self.cid_motion)
                self.canvas.mpl_disconnect(self.cid_release)
                self.canvas.setParent(None)
                self.toolbar.setParent(None)

            equations = equations_input.strip().split()  # Split input into equations
            if not equations:
                self.result_browser.setText("Please enter at least one equation.")  # Prompt user
                return  # Exit the method

            x = sp.symbols('x')  # Define symbolic variable x
            allowed_symbols = {'x'}  # Allowed symbols in equations
            transformations = standard_transformations + (  # Parsing transformations
                implicit_multiplication_application, implicit_application, convert_xor)
            local_dict = {  # Local dictionary for parsing expressions
                'x': x, 'e': np.e, 'pi': np.pi, 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
                'log': sp.log, 'sqrt': sp.sqrt, 'Abs': sp.Abs, 'exp': sp.exp, 'ln': sp.log
            }

            # Initialize figure and axes with increased size
            fig, self.ax = plt.subplots(figsize=(10, 8))  # Increased from (6, 5) to (10, 8)

            colors = plt.cm.tab10.colors  # Color map for plotting multiple graphs
            self.y_funcs_list = []  # List to store y-functions
            self.expr_list = []  # List to store expressions
            self.lines = []  # List to store line objects

            self.modules = {  # Modules for lambdify to handle functions
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log,
                'sqrt': np.sqrt, 'Abs': np.abs, 'exp': np.exp, 'ln': sp.log,
                'e': np.e, 'pi': np.pi
            }

            result_text = ""  # String to accumulate results

            for idx, equation in enumerate(equations):
                equation = self.replace_absolute_value(equation)  # Handle absolute values
                expr = parse_expr(  # Parse the equation into a SymPy expression
                    equation, transformations=transformations, local_dict=local_dict)

                symbols_in_expr = expr.free_symbols  # Symbols used in the expression
                if not symbols_in_expr.issubset({x}):  # Check for unsupported variables
                    unsupported_vars = symbols_in_expr - {x}
                    var_names = ', '.join(str(var) for var in unsupported_vars)
                    self.result_browser.setText(
                        f"Error: Equation {idx + 1} contains unsupported variables: {var_names}")
                    return  # Exit if unsupported variables are found

                self.expr_list.append(expr)  # Add expression to list

                # Initial plotting with a default range
                x_vals = np.linspace(-10, 10, 800)
                y_func = sp.lambdify(x, expr, modules=[self.modules, "numpy"])  # Convert to numerical function
                y_vals = y_func(x_vals)  # Calculate y-values
                self.y_funcs_list.append(y_func)  # Store the function

                line, = self.ax.plot( # Plot the graph
                    x_vals, y_vals, color=colors[idx % len(colors)],
                    label=f"${sp.latex(expr)}$")
                self.lines.append(line)  # Add line to list

                properties = self.compute_function_properties(expr)  # Compute properties
                result_text += f"Equation {idx + 1}: {equation}\n"  # Add equation info
                for prop_name, prop_value in properties.items():
                    result_text += f"{prop_name}: {prop_value}\n"  # Add properties
                result_text += "\n"  # Add a newline for spacing

            self.update_intersections()  # Find and plot intersections

            self.ax.grid(True)  # Enable grid

            # Adjust axes to cross at (0,0)
            self.ax.spines['left'].set_position('zero')
            self.ax.spines['bottom'].set_position('zero')
            self.ax.spines['right'].set_color('none')  # Hide right spine
            self.ax.spines['top'].set_color('none')  # Hide top spine
            self.ax.xaxis.set_ticks_position('bottom')  # Set x-axis ticks
            self.ax.yaxis.set_ticks_position('left')  # Set y-axis ticks

            self.ax.set_xlabel('')  # Clear x-axis label
            self.ax.set_ylabel('')  # Clear y-axis label

            # Set font size for tick labels
            for label in self.ax.get_xticklabels():
                label.set_fontsize(10)  # Increased from 8 to 10
            for label in self.ax.get_yticklabels():
                label.set_fontsize(10)  # Increased from 8 to 10

            self.ax.legend(loc='upper left', fontsize=10)  # Increased fontsize from 8 to 10

            self.canvas = FigureCanvas(fig)  # Create canvas widget
            self.toolbar = NavigationToolbar(self.canvas, self)  # Create toolbar
            layout = self.centralWidget().layout()  # Get current layout
            layout.addWidget(self.toolbar)  # Add toolbar to layout
            layout.addWidget(self.canvas)  # Add canvas to layout

            self.canvas.installEventFilter(self)  # Install event filter for canvas

            # Connect events to handlers
            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
            self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)

            self.canvas.draw()  # Draw the canvas

            self.result_browser.setText(result_text)  # Display results

        except Exception as e:
            # Handle exceptions and display the error message
            self.result_browser.setText(f"An error occurred while plotting graphs: {e}")

    def compute_function_properties(self, expr):
        x = sp.symbols('x')  # Define symbolic variable x
        properties = {}  # Dictionary to store properties

        try:
            x_intercepts = sp.solve(expr, x)  # Find x-intercepts
            properties['Zero Points (X-Intercepts)'] = x_intercepts
        except Exception as e:
            properties['Zero Points (X-Intercepts)'] = 'Unable to calculate x-intercepts.'

        try:
            y_intercept = expr.subs(x, 0)  # Find y-intercept
            properties['Y-Intercept'] = y_intercept
        except Exception as e:
            properties['Y-Intercept'] = 'Unable to calculate y-intercept.'

        try:
            limit_pos_inf = sp.limit(expr, x, sp.oo)  # Limit as x approaches infinity
            limit_neg_inf = sp.limit(expr, x, -sp.oo)  # Limit as x approaches negative infinity
            properties['Function End Behavior'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
        except Exception as e:
            properties['Function End Behavior'] = 'Unable to calculate function end behavior.'

        try:
            derivative = sp.diff(expr, x)  # Compute first derivative
            properties['First Derivative'] = derivative

            critical_points = sp.solve(derivative, x)  # Find critical points
            properties['Critical Points'] = critical_points
        except Exception as e:
            properties['First Derivative'] = 'Unable to calculate first derivative.'

        try:
            domain = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)  # Determine domain
            properties['Domain'] = domain
        except Exception as e:
            properties['Domain'] = 'Unable to calculate domain.'

        try:
            critical_points = sp.solve(sp.diff(expr, x), x)  # Recalculate critical points
            test_points = critical_points + [domain.inf, domain.sup]  # Points to test for range
            y_vals = []
            for point in test_points:
                if point.is_real or point.is_infinite:
                    y_val = expr.subs(x, point).evalf()
                    if y_val.is_real:
                        y_vals.append(y_val)

            y_min = min(y_vals)  # Minimum y-value
            y_max = max(y_vals)  # Maximum y-value

            limit_pos_inf = sp.limit(expr, x, sp.oo)  # Limits at infinity
            limit_neg_inf = sp.limit(expr, x, -sp.oo)

            if limit_pos_inf == sp.oo or limit_neg_inf == sp.oo:
                y_max = '∞'
            if limit_pos_inf == -sp.oo or limit_neg_inf == -sp.oo:
                y_min = '-∞'

            properties['Range'] = f"[{y_min}, {y_max}]"  # Set range
        except Exception as e:
            properties['Range'] = 'Unable to calculate range.'

        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)  # Find discontinuities
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
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)  # Recalculate discontinuities
            if discontinuities:
                properties['Discontinuities'] = list(discontinuities)
            else:
                properties['Discontinuities'] = 'No discontinuities.'
        except Exception as e:
            properties['Discontinuities'] = 'Unable to calculate discontinuities.'

        try:
            second_derivative = sp.diff(expr, x, 2)  # Compute second derivative
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
            properties['Extrema'] = extrema  # Add extrema to properties
        except Exception as e:
            properties['Extrema'] = 'Unable to calculate extrema.'

        return properties  # Return the computed properties

    def update_intersections(self):
        # Clear existing intersection points
        if hasattr(self, 'intersection_points'):
            for point in self.intersection_points:
                point.remove()
        self.intersection_points = []

        intersections = self.find_intersections()  # Find intersections

        if intersections:
            x_ints, y_ints = zip(*intersections)  # Unpack intersection points
            points = self.ax.plot(x_ints, y_ints, 'ko', label='Intersections')  # Plot intersections
            self.intersection_points.extend(points)

    def find_intersections(self):
        intersections = []  # List to store intersection points
        combinations_indices = list(combinations(range(len(self.y_funcs_list)), 2))
        x_min, x_max = self.ax.get_xlim()
        x_vals = np.linspace(x_min, x_max, 800)

        y_vals_list = []
        for y_func in self.y_funcs_list:
            y_vals = y_func(x_vals)
            y_vals_list.append(y_vals)

        for i, j in combinations_indices:  # Iterate over pairs of graphs
            y_vals1 = y_vals_list[i]
            y_vals2 = y_vals_list[j]
            diff = y_vals1 - y_vals2
            # Handle NaN and infinite values
            diff = np.where(np.isnan(diff), np.inf, diff)
            diff = np.where(np.isinf(diff), np.inf, diff)
            sign_diff = np.sign(diff)
            # Find indices where the sign of diff changes
            sign_changes = np.where(np.diff(sign_diff) != 0)[0]
            for idx in sign_changes:
                # Get x-values and corresponding y-values
                x1, x2 = x_vals[idx], x_vals[idx + 1]
                y1_diff, y2_diff = diff[idx], diff[idx + 1]
                if np.isfinite(y1_diff) and np.isfinite(y2_diff):
                    # Linear interpolation to estimate zero crossing
                    x_zero = x1 - y1_diff * (x2 - x1) / (y2_diff - y1_diff)
                    # Get y-value at x_zero
                    y_zero = self.y_funcs_list[i](x_zero)
                    intersections.append((x_zero, y_zero))
        # Remove duplicates
        unique_intersections = list({(round(x, 5), round(y, 5)) for x, y in intersections})
        return unique_intersections  # Return intersections

    def on_press(self, event):
        if event.inaxes != self.ax:
            return  # Ignore if not within axes
        if event.button == 1:
            self.pressing = True  # Set pressing flag
            self.selected_graph_index = None  # Reset selected graph
            self.update_dot(event)  # Update the dot annotation
        elif event.button == 2:
            # Middle mouse button pressed
            self.panning = True  # Set panning flag
            self.pan_start = (event.xdata, event.ydata)  # Record starting point

    def on_motion(self, event):
        if event.inaxes != self.ax:
            return  # Ignore if not within axes
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
            self.update_plot()  # Update the plot after panning
        elif self.pressing:
            self.update_dot(event)  # Update the dot annotation

    def on_release(self, event):
        if event.button == 1:
            self.pressing = False  # Reset pressing flag
            self.selected_graph_index = None  # Reset selected graph
            if self.dot:
                self.dot.remove()  # Remove dot annotation
                self.dot = None
            if self.text_annotation:
                self.text_annotation.remove()  # Remove text annotation
                self.text_annotation = None
            self.canvas.draw_idle()  # Redraw canvas
        elif event.button == 2:
            # Middle mouse button released
            self.panning = False
            self.pan_start = None

    def update_dot(self, event):
        x = event.xdata  # Get x-coordinate
        y = event.ydata  # Get y-coordinate

        if x is None or y is None:
            return  # Ignore if coordinates are invalid

        x_threshold = 0.2  # Threshold for snapping to integer

        x_int = round(x)
        delta_x = abs(x - x_int)

        if delta_x < x_threshold:
            x_snap = x_int  # Snap to integer value
        else:
            x_snap = x  # Use actual x-value

        # Check for proximity to intersections
        intersection_threshold = 0.5  # Threshold for snapping to intersections
        for x_ints, y_ints in self.find_intersections():
            if abs(x_snap - x_ints) < intersection_threshold and abs(y - y_ints) < intersection_threshold:
                x_snap = x_ints
                y = y_ints
                break

        if self.selected_graph_index is None:
            y_curves = []
            for y_func in self.y_funcs_list:
                y_curve = y_func(x_snap)
                if np.isfinite(y_curve):
                    y_curves.append(y_curve)
                else:
                    y_curves.append(np.nan)

            distances = [abs(y - y_curve) for y_curve in y_curves]  # Calculate distances
            valid_distances = [(dist, idx) for idx, dist in enumerate(distances) if not np.isnan(dist)]
            if not valid_distances:
                return
            min_distance, min_index = min(valid_distances, key=lambda t: t[0])
            y_curve = y_curves[min_index]

            y_threshold = 0.5  # Threshold for selecting graph

            if min_distance < y_threshold:
                self.selected_graph_index = min_index  # Select the closest graph
            else:
                return  # Ignore if no graph is close enough

        y_func = self.y_funcs_list[self.selected_graph_index]
        y_curve = y_func(x_snap)

        if not np.isfinite(y_curve):
            return  # Ignore if y is not finite

        if self.dot:
            self.dot.remove()  # Remove existing dot
        if self.text_annotation:
            self.text_annotation.remove()  # Remove existing annotation

        self.dot = self.ax.plot(x_snap, y_curve, 'ro')[0]  # Plot new dot

        x_display = round(x_snap, 2)  # Format x-value
        y_display = round(y_curve, 2)  # Format y-value
        equation_label = f"${sp.latex(self.expr_list[self.selected_graph_index])}$"  # Get equation label
        self.text_annotation = self.ax.text(  # Add text annotation
            x_snap, y_curve + (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.03,
            f"({x_display}, {y_display})\n{equation_label}",
            fontsize=10, color='black', ha='center', va='bottom'  # Increased fontsize from 9 to 10
        )

        self.canvas.draw_idle()  # Redraw canvas

    def update_plot(self):
        # Clear existing lines
        for line in self.lines:
            line.remove()
        self.lines.clear()

        # Get current x-limits
        x_min, x_max = self.ax.get_xlim()
        x_vals = np.linspace(x_min, x_max, 800)

        colors = plt.cm.tab10.colors  # Color map for plotting multiple graphs

        for idx, (expr, y_func) in enumerate(zip(self.expr_list, self.y_funcs_list)):
            y_vals = y_func(x_vals)  # Calculate y-values
            line, = self.ax.plot(  # Plot the graph
                x_vals, y_vals, color=colors[idx % len(colors)],
                label=f"${sp.latex(expr)}$")
            self.lines.append(line)  # Add line to list

        # Remove and redraw legend to avoid duplicates
        if hasattr(self.ax, 'legend_') and self.ax.legend_:
            self.ax.legend_.remove()
        self.ax.legend(loc='upper left', fontsize=10)  # Increased fontsize from 8 to 10

        self.update_intersections()  # Update intersections

        self.ax.figure.canvas.draw_idle()  # Redraw the canvas

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.NativeGesture:
            return self.nativeGestureEvent(event)  # Handle native gestures
        elif event.type() == QEvent.Type.Wheel:
            self.wheelEvent(event)  # Handle wheel events
            return event.isAccepted()
        return super(GraphingCalculator, self).eventFilter(source, event)  # Default handling

    def nativeGestureEvent(self, event):
        if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
            scale_factor = 1 / (1 + event.value())  # Calculate scale factor
            self.zoom(scale_factor, event)  # Perform zoom
            return True
        return False

    def wheelEvent(self, event):
        angle_delta = event.angleDelta()
        delta_x = angle_delta.x()
        delta_y = angle_delta.y()
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zooming
            if delta_y > 0:
                scale_factor = 0.9  # Zoom out
            else:
                scale_factor = 1.1  # Zoom in
            self.zoom(scale_factor, event)  # Perform zoom
            event.accept()
        else:
            # Panning
            self.pan_wheel(delta_x, delta_y, event)
            event.accept()

    def zoom(self, scale_factor, event):
        ax = self.canvas.figure.axes[0]  # Get current axes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        if hasattr(event, 'position'):
            xdata = event.position().x()
            ydata = event.position().y()
        else:
            xdata = event.x()
            ydata = event.y()
        xdata, ydata = ax.transData.inverted().transform([xdata, ydata])  # Convert to data coordinates

        # Calculate new limits
        new_xlim = [xdata + (x - xdata) * scale_factor for x in xlim]
        new_ylim = [ydata + (y - ydata) * scale_factor for y in ylim]
        ax.set_xlim(new_xlim)  # Set new x-axis limits
        ax.set_ylim(new_ylim)  # Set new y-axis limits

        self.canvas.draw_idle()  # Redraw canvas
        self.update_plot()  # Update the plot after zooming

    def pan_wheel(self, delta_x, delta_y, event):
        ax = self.canvas.figure.axes[0]  # Get current axes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        # Convert delta to movement in data coordinates
        dx = -delta_x * (xlim[1] - xlim[0]) / 1000  # Adjust scaling factor as needed
        dy = delta_y * (ylim[1] - ylim[0]) / 1000  # Adjust scaling factor as needed
        ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
        ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
        self.canvas.draw_idle()
        self.update_plot()  # Update the plot after panning


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create the application
    window = GraphingCalculator()  # Create the main window
    window.show()  # Show the window
    sys.exit(app.exec())  # Execute the application
