import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor, implicit_application
)

canvas = None

def replace_absolute_value(expr_str):
    import re
    def repl(match):
        inner_expr = match.group(1)
        return f'Abs({inner_expr})'
    expr_str = re.sub(r'\|([^|]+)\|', repl, expr_str)
    return expr_str

def plot_graph_2d():
    global canvas
    result_label.config(text="")
    equation = entry_2d.get()
    try:
        if canvas:
            canvas.get_tk_widget().destroy()
        x = sp.symbols('x')
        equation = replace_absolute_value(equation)
        transformations = standard_transformations + (
            implicit_multiplication_application, implicit_application, convert_xor)
        local_dict = {
            'x': x, 'e': np.e, 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'log': sp.log, 'sqrt': sp.sqrt, 'Abs': sp.Abs, 'exp': sp.exp, 'ln': sp.log
        }
        expr = parse_expr(
            equation, transformations=transformations, local_dict=local_dict)
        latex_eq = sp.latex(expr)

        x_vals = np.linspace(-10, 10, 400)

        modules = {
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log,
            'sqrt': np.sqrt, 'Abs': np.abs, 'exp': np.exp, 'ln': np.log, 'e': np.e
        }
        y_func = sp.lambdify(x, expr, modules=[modules, "numpy"])
        y_vals = y_func(x_vals)

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(x_vals, y_vals)
        ax.set_title(f"$y = {latex_eq}$", fontsize=16)
        ax.set_xlim([-10, 10])
        ax.set_xlabel('x-axis')
        ax.set_ylabel('y-axis')
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    except Exception as e:
        result_label.config(text=f"Error: {e}")

def plot_graph_3d():
    global canvas
    result_label.config(text="")
    equation = entry_3d.get()
    try:
        if canvas:
            canvas.get_tk_widget().destroy()
        x, y = sp.symbols('x y')
        equation = replace_absolute_value(equation)
        transformations = standard_transformations + (
            implicit_multiplication_application, implicit_application, convert_xor)
        local_dict = {
            'x': x, 'y': y, 'e': np.e, 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'log': sp.log, 'sqrt': sp.sqrt, 'Abs': sp.Abs, 'exp': sp.exp, 'ln': sp.log
        }
        expr = parse_expr(
            equation, transformations=transformations, local_dict=local_dict)
        latex_eq = sp.latex(expr)

        x_vals = np.linspace(-5, 5, 100)
        y_vals = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x_vals, y_vals)

        modules = {
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log,
            'sqrt': np.sqrt, 'Abs': np.abs, 'exp': np.exp, 'ln': np.log, 'e': np.e
        }
        z_func = sp.lambdify((x, y), expr, modules=[modules, "numpy"])
        Z = z_func(X, Y)

        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_title(f"$z = {latex_eq}$", fontsize=16)
        ax.set_xlabel('x-axis')
        ax.set_ylabel('y-axis')
        ax.set_zlabel('z-axis')
        ax.view_init(elev=20., azim=30)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    except Exception as e:
        result_label.config(text=f"Error: {e}")

window = tk.Tk()
window.title("Graphing Calculator")

label_2d = tk.Label(window, text="Enter 2D equation (y = f(x)):")
label_2d.pack()
entry_2d = tk.Entry(window, width=30)
entry_2d.pack()

plot_button_2d = tk.Button(window, text="Plot 2D Graph", command=plot_graph_2d)
plot_button_2d.pack()

label_3d = tk.Label(window, text="Enter 3D equation (z = f(x, y)):")
label_3d.pack()
entry_3d = tk.Entry(window, width=30)
entry_3d.pack()

plot_button_3d = tk.Button(window, text="Plot 3D Graph", command=plot_graph_3d)
plot_button_3d.pack()

result_label = tk.Label(window, text="")
result_label.pack()

window.mainloop()
