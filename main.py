import sys  # Import system-specific parameters and functions
import re   # Import regular expressions module

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

    def initUI(self):
        widget = QWidget()  # Create a central widget
        self.setCentralWidget(widget)  # Set the central widget
        layout = QVBoxLayout(widget)  # Create a vertical box layout

        self.label_2d = QLabel("Enter 2D equations (separated by spaces):")  # Label for input
        layout.addWidget(self.label_2d)  # Add label to layout
        self.entry_2d = QLineEdit()  # Line edit for equation input
        layout.addWidget(self.entry_2d)  # Add line edit to layout

        self.plot_button_2d = QPushButton("Plot 2D Graph")  # Button to plot graphs
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

            self.x_vals = np.linspace(-10, 10, 800)  # Generate x-values for plotting
            modules = {  # Modules for lambdify to handle functions
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log,
                'sqrt': np.sqrt, 'Abs': np.abs, 'exp': np.exp, 'ln': np.log,
                'e': np.e, 'pi': np.pi
            }

            fig, self.ax = plt.subplots(figsize=(6, 5))  # Create a figure and axes

            colors = plt.cm.tab10.colors  # Color map for plotting multiple graphs
            self.y_vals_list = []  # List to store y-values of graphs
            self.expr_list = []  # List to store expressions
            self.lines = []  # List to store line objects

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
                        f"Error: Unsupported variables in equation {idx+1}: {var_names}")
                    return  # Exit if unsupported variables are found

                self.expr_list.append(expr)  # Add expression to list
                y_func = sp.lambdify(x, expr, modules=[modules, "numpy"])  # Convert to numerical function
                y_vals = y_func(self.x_vals)  # Calculate y-values
                self.y_vals_list.append(y_vals)  # Add y-values to list

                line, = self.ax.plot(  # Plot the graph
                    self.x_vals, y_vals, color=colors[idx % len(colors)],
                    label=f"${sp.latex(expr)}$")
                self.lines.append(line)  # Add line to list

                properties = self.compute_function_properties(expr)  # Compute properties
                result_text += f"Equation {idx+1}: {equation}\n"  # Add equation info
                for prop_name, prop_value in properties.items():
                    result_text += f"{prop_name}: {prop_value}\n"  # Add properties
                result_text += "\n"  # Add a newline for spacing

            intersections = self.find_intersections()  # Find intersections

            if intersections:
                x_ints, y_ints = zip(*intersections)  # Unpack intersection points
                self.ax.plot(x_ints, y_ints, 'ko', label='Intersections')  # Plot intersections

            self.ax.set_xlim([-10, 10])  # Set x-axis limits
            self.ax.set_ylim(  # Set y-axis limits based on data
                [np.nanmin([np.nanmin(y) for y in self.y_vals_list]),
                 np.nanmax([np.nanmax(y) for y in self.y_vals_list])])
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
                label.set_fontsize(8)
            for label in self.ax.get_yticklabels():
                label.set_fontsize(8)

            self.ax.legend(loc='upper left', fontsize=8)  # Add legend

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
            self.result_browser.setText(f"Error: {e}")  # Display error message

    def compute_function_properties(self, expr):
        x = sp.symbols('x')  # Define symbolic variable x
        properties = {}  # Dictionary to store properties

        try:
            x_intercepts = sp.solve(expr, x)  # Find x-intercepts
            properties['Zeroes (x-intercepts)'] = x_intercepts
        except Exception as e:
            properties['Zeroes (x-intercepts)'] = 'Cannot compute zeroes.'

        try:
            y_intercept = expr.subs(x, 0)  # Find y-intercept
            properties['Y-intercept'] = y_intercept
        except Exception as e:
            properties['Y-intercept'] = 'Cannot compute Y-intercept.'

        try:
            limit_pos_inf = sp.limit(expr, x, sp.oo)  # Limit as x approaches infinity
            limit_neg_inf = sp.limit(expr, x, -sp.oo)  # Limit as x approaches negative infinity
            properties['End behavior'] = {'x→∞': limit_pos_inf, 'x→-∞': limit_neg_inf}
        except Exception as e:
            properties['End behavior'] = 'Cannot compute end behavior.'

        try:
            derivative = sp.diff(expr, x)  # Compute first derivative
            properties['First derivative'] = derivative

            critical_points = sp.solve(derivative, x)  # Find critical points
            properties['Critical points'] = critical_points
        except Exception as e:
            properties['First derivative'] = 'Cannot compute derivative.'

        try:
            domain = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)  # Determine domain
            properties['Domain'] = domain
        except Exception as e:
            properties['Domain'] = 'Cannot compute domain.'

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
            properties['Range'] = 'Cannot compute range.'

        try:
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)  # Find discontinuities
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
            discontinuities = sp.calculus.util.discontinuities(expr, x, sp.S.Reals)  # Recalculate discontinuities
            if discontinuities:
                properties['Discontinuities'] = list(discontinuities)
            else:
                properties['Discontinuities'] = 'No discontinuities.'
        except Exception as e:
            properties['Discontinuities'] = 'Cannot compute discontinuities.'

        try:
            second_derivative = sp.diff(expr, x, 2)  # Compute second derivative
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
            properties['Local extrema'] = extrema  # Add extrema to properties
        except Exception as e:
            properties['Local extrema'] = 'Cannot compute local extrema.'

        return properties  # Return the computed properties

    def find_intersections(self):
        intersections = []  # List to store intersection points
        x = sp.symbols('x')  # Define symbolic variable x

        for i, j in combinations(range(len(self.expr_list)), 2):  # Iterate over pairs of graphs
            expr1 = self.expr_list[i]
            expr2 = self.expr_list[j]
            try:
                sol = sp.solve(expr1 - expr2, x)  # Solve for intersection points
                for s in sol:
                    if s.is_real and -10 <= s.evalf() <= 10:
                        y_val = expr1.subs(x, s).evalf()
                        if y_val.is_real:
                            intersections.append((float(s.evalf()), float(y_val)))
            except Exception as e:
                continue  # Skip if unable to find intersections

        unique_intersections = list(set(intersections))  # Remove duplicates
        return unique_intersections  # Return intersections

    def on_press(self, event):
        if event.inaxes != self.ax:
            return  # Ignore if not within axes
        if event.button == 1:
            self.pressing = True  # Set pressing flag
            self.selected_graph_index = None  # Reset selected graph
            self.update_dot(event)  # Update the dot annotation

    def on_motion(self, event):
        if not self.pressing:
            return  # Ignore if mouse not pressed
        if event.inaxes != self.ax:
            return  # Ignore if not within axes
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

        if self.selected_graph_index is None:
            y_curves = []
            for y_vals in self.y_vals_list:
                if self.x_vals[0] <= x_snap <= self.x_vals[-1]:
                    y_curve = np.interp(x_snap, self.x_vals, y_vals)  # Interpolate y-value
                else:
                    y_curve = np.nan
                y_curves.append(y_curve)

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

        y_vals = self.y_vals_list[self.selected_graph_index]
        if self.x_vals[0] <= x_snap <= self.x_vals[-1]:
            y_curve = np.interp(x_snap, self.x_vals, y_vals)  # Interpolate y-value
        else:
            return  # Ignore if x is out of bounds

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
            fontsize=9, color='black', ha='center', va='bottom'
        )

        self.canvas.draw_idle()  # Redraw canvas

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
        if event.angleDelta().y() != 0:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.angleDelta().y() > 0:
                    scale_factor = 0.9  # Zoom out
                else:
                    scale_factor = 1.1  # Zoom in
                self.zoom(scale_factor, event)  # Perform zoom
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create the application
    window = GraphingCalculator()  # Create the main window
    window.show()  # Show the window
    sys.exit(app.exec())  # Execute the application
