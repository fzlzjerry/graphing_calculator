<div align="center">

# 📊 Advanced Graphing Calculator

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GNU%20AGPL%20v3-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/fzlzjerry/graphing_calculator/pulls)

**A powerful mathematical visualization tool crafted for educators and students. Transform complex mathematical expressions into interactive, dynamic graphs.**

[Getting Started](#-getting-started) • 
[Key Features](#-key-features) • 
[Examples](#-examples) • 
[Documentation](#-documentation) • 
[Contributing](#-contributing)

![Graphing Calculator Interface](https://ice.frostsky.com/2024/12/02/3ea54d757a78de373b554fc51a4bebc2.png)

</div>

---

## 🌟 Overview

**Advanced Graphing Calculator** is a sophisticated mathematical visualization tool that brings complex functions to life. Perfect for:

- 📚 **Students**: Exploring mathematical concepts
- 🎓 **Educators**: Demonstrating function behaviors
- 🔬 **Researchers**: Analyzing mathematical relationships
- 💡 **Enthusiasts**: Anyone interested in mathematical visualization

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Getting Started](#-getting-started)
   - [System Requirements](#system-requirements)
   - [Installation](#installation)
   - [Running the Application](#running-the-application)
3. [Usage Instructions](#-usage-instructions)
   - [Entering Expressions](#entering-expressions)
   - [Plotting Graphs](#plotting-graphs)
   - [Interactive Operations](#interactive-operations)
4. [Key Features](#-key-features)
   - [Function Plotting](#function-plotting)
   - [Mathematical Analysis](#mathematical-analysis)
   - [Interactive Controls](#interactive-controls)
   - [Data Management](#data-management)
   - [Supported Functions](#supported-functions)
5. [Examples](#-examples)
6. [Important Notes](#-important-notes)
7. [Frequently Asked Questions](#-frequently-asked-questions)
8. [Contributing](#-contributing)
9. [License](#-license)
10. [Contact Us](#-contact-us)

## 🚀 Getting Started

### System Requirements

- **Python 3.9+**
- **pip** package manager

### Installation

Install the required Python libraries using the following command:

```bash
pip install PyQt6 requests semver sympy numpy matplotlib scipy
```

### Running the Application

1. Save the `graphing_calculator.py` file to your local machine.
2. Open a terminal or command prompt and navigate to the directory containing the file.
3. Run the following command to start the application:

    ```bash
    python graphing_calculator.py
    ```

## Usage Instructions

### Entering Expressions

- In the "Enter 2D equations" input field, enter one or more 2D expressions.
- Input only expressions, not equations. For example, enter `sin(x) x^2 |x|` to plot `sin(x)`, `x²`, and `|x|`.
- Use spaces to separate multiple expressions. Spaces are used to distinguish different formulas.

### Plotting Graphs

- After entering the expressions, click the "Plot 2D Graphs" button.
- The application will plot the corresponding graphs and calculate various function properties.
- Results will be displayed in the text browser below the plot.

### Interactive Operations

- **Zooming**: Use the mouse wheel to zoom in and out of the graph. Hold the `Ctrl` key and scroll the mouse wheel for precise zooming.
- **Panning**: Press and hold the middle mouse button (scroll wheel) and drag to pan the graph.
- **View Intersections**: Click on the intersection points in the graph to display their coordinates and corresponding equations.

## ✨ Key Features

### Function Plotting

- **Multi-Function Plotting**: Visualize multiple functions simultaneously
- **Interactive Graphs**: Real-time zoom, pan, and point analysis
- **Smart Annotations**: Automatic labeling of key points and intersections

### Mathematical Analysis

| Feature | Description |
|---------|-------------|
| 🎯 Zero Points | Automatically finds x-intercepts |
| 📊 Derivatives | Calculates first and second derivatives |
| 🌟 Critical Points | Identifies extrema and inflection points |
| 🌐 Domain & Range | Determines function boundaries |
| 📉 Asymptotes | Locates horizontal and vertical asymptotes |
| ⚠️ Discontinuities | Identifies points of discontinuity |

### Interactive Controls

| Control | Action | Description |
|---------|--------|-------------|
| Mouse Wheel | Zoom | Scroll to zoom in/out |
| Ctrl + Wheel | Precise Zoom | Fine-grained zoom control |
| Middle Mouse | Pan | Click and drag to move view |
| Left Click | Point Analysis | Shows coordinates and function details |
| Grid Toggle | Show/Hide Grid | Toggle grid visibility |
| Dark Mode | Theme Switch | Changes interface theme |
| Custom Ranges | Set View Bounds | Enter custom x/y axis limits |

### Data Management

| Feature | Format | Description |
|---------|--------|-------------|
| Save Equations | Text file (.txt) | Save current function set |
| Load Equations | Text file (.txt) | Load saved function set |
| Export Graph | PNG/SVG | Export graph as image |
| Function Templates | Built-in | Quick access to common functions |

### Supported Functions

| Category | Functions | Examples |
|----------|-----------|-----------|
| Arithmetic | +, -, *, /, ^ | `x^2 + 2*x` |
| Trigonometric | sin, cos, tan, sec, csc, cot | `sin(x) * cos(x)` |
| Inverse Trig | asin, acos, atan | `asin(x/2)` |
| Hyperbolic | sinh, cosh, tanh | `sinh(x)` |
| Exponential | exp, ln, log | `exp(-x^2)` |
| Special | Abs, factorial, gamma | `|x|`, `gamma(x)` |
| Bessel | jn, yn | `jn(0,x)` |

## Examples

### Example 1: Plotting Simple Functions

**Input:**
```
sin(x) x^2
```

**Outcome:**
- Plots the sine function and the quadratic function on the same graph.
- Displays the intersection points, zeros, derivatives, and other properties for both functions.

### Example 2: Including Absolute Value Function

**Input:**
```
|x| x^3-3x
```

**Outcome:**
- Plots the absolute value function and the cubic function.
- Automatically handles absolute value notation and calculates relevant function properties.

## Important Notes

- **Avoid Using Dark Mode**: Do not use dark mode on Windows systems to ensure proper display of the interface and graphs.
- **Input Format**:
    - **Do Not Insert Spaces Within Expressions**: Spaces are used to separate different expressions. Do not include spaces within a single expression.
    - **Input Only Expressions**: Enter only the mathematical expression without an equals sign. For example, use `x^2` instead of `y = x^2`.
    - **Separate Multiple Expressions with Spaces**: To plot multiple functions, separate each expression with a space, such as `sin(x) cos(x)`.

## Frequently Asked Questions (FAQs)

### Q1: How do I input absolute value functions?

**A1**: Use the pipe symbol `|` to denote absolute values. For example, `|x|` will be automatically converted to `Abs(x)` for processing.

### Q2: What happens if I enter an invalid expression?

**A2**: The application will display an error message in the results browser, prompting you to check and correct your input expressions.

### Q3: How can I view the derivatives and other properties of a function?

**A3**: After plotting the graphs, the results browser will automatically list the first and second derivatives, domain, asymptotes, and other detailed properties for each function.

## Contributing

Contributions are welcome! If you have suggestions or want to contribute code, please submit an Issue or Pull Request on the [GitHub repository](https://github.com/fzlzjerry/graphing_calculator).

## License

This project is licensed under the GNU Affero General Public License v3.0 License. See the [LICENSE](LICENSE) file for details.

## Contact Us

If you have any questions or suggestions, please reach out to us:

- **Email**: james20081204@gmail.com
- **GitHub**: [fzlzjerry/graphing_calculator](https://github.com/fzlzjerry/graphing_calculator)
