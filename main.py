import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor, implicit_application
)
from matplotlib import rcParams

rcParams['font.size'] = 8

canvas = None
toolbar = None

def replace_absolute_value(expr_str):
    import re
    def repl(match):
        inner_expr = match.group(1)
        return f'Abs({inner_expr})'
    expr_str = re.sub(r'\|([^|]+)\|', repl, expr_str)
    return expr_str

def plot_graph_2d():
    global canvas, toolbar
    result_label.config(text="")
    equation = entry_2d.get()
    try:
        if canvas:
            canvas.get_tk_widget().destroy()
            toolbar.destroy()
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
        ax.set_title(f"$y = {latex_eq}$", fontsize=12)
        ax.set_xlim([-10, 10])
        ax.set_ylim([np.nanmin(y_vals), np.nanmax(y_vals)])
        ax.set_xlabel('x axis')
        ax.set_ylabel('y axis')
        ax.grid(True)

        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        for label in ax.get_xticklabels():
            label.set_verticalalignment('top')
            label.set_fontsize(8)
        for label in ax.get_yticklabels():
            label.set_horizontalalignment('right')
            label.set_fontsize(8)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        def zoom(event):
            base_scale = 1.1
            ax = event.inaxes
            if ax is None:
                return

            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                scale_factor = 1

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            xdata = event.xdata
            ydata = event.ydata

            new_xlim = [xdata + (x - xdata) * scale_factor for x in xlim]
            new_ylim = [ydata + (y - ydata) * scale_factor for y in ylim]
            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)

            x_range = new_xlim[1] - new_xlim[0]
            y_range = new_ylim[1] - new_ylim[0]
            x_ticks = np.linspace(new_xlim[0], new_xlim[1], 10)
            y_ticks = np.linspace(new_ylim[0], new_ylim[1], 10)
            ax.set_xticks(x_ticks)
            ax.set_yticks(y_ticks)

            for label in ax.get_xticklabels():
                label.set_fontsize(8)
            for label in ax.get_yticklabels():
                label.set_fontsize(8)

            canvas.draw_idle()

        canvas.mpl_connect('scroll_event', zoom)

    except Exception as e:
        result_label.config(text=f"Error: {e}")

def plot_graph_3d():
    global canvas, toolbar
    result_label.config(text="")
    equation = entry_3d.get()
    try:
        if canvas:
            canvas.get_tk_widget().destroy()
            toolbar.destroy()
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

        x_range = [-10, 10]
        y_range = [-10, 10]
        x_vals = np.linspace(x_range[0], x_range[1], 200)
        y_vals = np.linspace(y_range[0], y_range[1], 200)
        X, Y = np.meshgrid(x_vals, y_vals)

        modules = {
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log,
            'sqrt': np.sqrt, 'Abs': np.abs, 'exp': np.exp, 'ln': np.log, 'e': np.e
        }
        z_func = sp.lambdify((x, y), expr, modules=[modules, "numpy"])
        Z = z_func(X, Y)

        fig = plt.figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111, projection='3d')

        surface = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)

        ax.set_xlim3d(x_range)
        ax.set_ylim3d(y_range)
        z_min = np.nanmin(Z)
        z_max = np.nanmax(Z)
        if np.isnan(z_min) or np.isnan(z_max):
            z_min = -10
            z_max = 10
        ax.set_zlim3d([z_min, z_max])

        axis_lines = []
        axis_lines.append(ax.plot([0, 0], y_range, [0, 0], color='black')[0])
        axis_lines.append(ax.plot(x_range, [0, 0], [0, 0], color='black')[0])
        axis_lines.append(ax.plot([0, 0], [0, 0], [z_min, z_max], color='black')[0])

        ax._axis3don = False

        def update_ticks():
            xticks = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 5)
            yticks = np.linspace(ax.get_ylim()[0], ax.get_ylim()[1], 5)
            zticks = np.linspace(ax.get_zlim()[0], ax.get_zlim()[1], 5)

            for txt in ax.texts:
                txt.remove()

            for xtick in xticks:
                ax.text(xtick, 0, 0, f'{xtick:.2f}', color='black', ha='center', va='center', fontsize=8)
            for ytick in yticks:
                ax.text(0, ytick, 0, f'{ytick:.2f}', color='black', ha='center', va='center', fontsize=8)
            for ztick in zticks:
                ax.text(0, 0, ztick, f'{ztick:.2f}', color='black', ha='center', va='center', fontsize=8)

        update_ticks()

        ax.set_title(f"$z = {latex_eq}$", fontsize=12, y=1.05)

        ax.view_init(elev=20., azim=30)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        def zoom(event):
            base_scale = 1.1
            if event.inaxes != ax:
                return

            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                scale_factor = 1

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            cur_zlim = ax.get_zlim()

            xdata = event.xdata if event.xdata else 0
            ydata = event.ydata if event.ydata else 0

            new_xlim = [xdata + (x - xdata) * scale_factor for x in cur_xlim]
            new_ylim = [ydata + (y - ydata) * scale_factor for y in cur_ylim]
            new_zlim = [z * scale_factor for z in cur_zlim]

            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)
            ax.set_zlim(new_zlim)

            x_vals = np.linspace(new_xlim[0], new_xlim[1], 200)
            y_vals = np.linspace(new_ylim[0], new_ylim[1], 200)
            X, Y = np.meshgrid(x_vals, y_vals)
            Z = z_func(X, Y)

            while ax.collections:
                ax.collections[0].remove()

            ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)

            for line in axis_lines:
                line.remove()
            axis_lines.clear()

            axis_lines.append(ax.plot([0, 0], new_ylim, [0, 0], color='black')[0])
            axis_lines.append(ax.plot(new_xlim, [0, 0], [0, 0], color='black')[0])
            axis_lines.append(ax.plot([0, 0], [0, 0], new_zlim, color='black')[0])

            update_ticks()

            canvas.draw_idle()

        canvas.mpl_connect('scroll_event', zoom)

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
