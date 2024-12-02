<div align="center">

# 📊 Advanced Graphing Calculator

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GNU%20AGPL%20v3-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/fzlzjerry/graphing_calculator/pulls)

A powerful mathematical visualization tool crafted for educators and students.
Transform complex mathematical expressions into interactive, dynamic graphs.

[Getting Started](#-getting-started) • 
[Key Features](#-key-features) • 
[Examples](#examples) • 
[Documentation](#-comprehensive-feature-guide) • 
[Contributing](#contribution)

![Graphing Calculator Interface](https://ice.frostsky.com/2024/12/02/3ea54d757a78de373b554fc51a4bebc2.png)

</div>

## 🌟 Overview

Advanced Graphing Calculator is a sophisticated mathematical visualization tool that brings complex functions to life. Perfect for:

- ��� **Students** exploring mathematical concepts
- 🎓 **Educators** demonstrating function behaviors
- 🔬 **Researchers** analyzing mathematical relationships
- 💡 **Anyone** interested in mathematical visualization

## ✨ Key Features

### 📈 Visualization Tools
- **Multi-Function Plotting**: Visualize multiple functions simultaneously
- **Interactive Graphs**: Real-time zoom, pan, and point analysis
- **Smart Annotations**: Automatic labeling of key points and intersections

### 🧮 Mathematical Analysis
| Feature | Description |
|---------|-------------|
| 🎯 Zero Points | Automatically finds x-intercepts |
| 📊 Derivatives | Calculates first and second derivatives |
| 🌟 Critical Points | Identifies extrema and inflection points |
| 🌐 Domain & Range | Determines function boundaries |
| 📉 Asymptotes | Locates horizontal and vertical asymptotes |
| ⚠️ Discontinuities | Identifies points of discontinuity |

## 📚 Comprehensive Feature Guide

### 🎨 Basic Features
| Feature | Description |
|---------|-------------|
| 📈 Function Plotting | Plot multiple mathematical functions on the same coordinate system |
| 🎯 Interactive Points | Click anywhere on the graph to see exact coordinates and function values |
| 🔄 Real-time Updates | Graphs update automatically when modifying expressions |
| 💾 Save/Load | Save your function sets and load them later |
| 📸 Export | Export graphs as PNG or SVG files |

### 🧮 Mathematical Analysis
| Analysis Type | Description |
|--------------|-------------|
| 🎯 Zero Points | Automatically calculates x-intercepts (f(x) = 0) |
| 📊 Y-Intercept | Determines the point where function crosses y-axis |
| 📈 Derivatives | Computes first and second derivatives with critical points |
| 🌐 Domain/Range | Analyzes complete function boundaries |
| 📉 Asymptotes | Identifies horizontal, vertical, and oblique asymptotes |
| ⚠️ Discontinuities | Locates points of discontinuity |
| 💫 Critical Points | Finds local maxima, minima, and inflection points |
| ➗ End Behavior | Analyzes function behavior as x approaches ±∞ |

### 🛠️ Interactive Tools
| Tool | Description |
|------|-------------|
| 🔍 Zoom | Mouse wheel or pinch gesture for precise zooming |
| 🤚 Pan | Middle-mouse drag or two-finger slide |
| 📏 Grid | Toggle grid display for precise measurements |
| 🎨 Dark Mode | Switch between light and dark themes |
| 📊 Custom Ranges | Set custom x and y axis ranges |

### 📐 Supported Functions
| Category | Functions |
|----------|-----------|
| Basic | +, -, *, /, ^, √ |
| Trigonometric | sin, cos, tan, sec, csc, cot |
| Inverse Trig | asin, acos, atan |
| Hyperbolic | sinh, cosh, tanh, asinh, acosh, atanh |
| Exponential | exp, ln, log |
| Special | Abs (absolute value), factorial, gamma |
| Bessel | jn (Bessel function of first kind), yn (Bessel function of second kind) |

### 🧪 Advanced Features
| Feature | Description |
|---------|-------------|
| 🔄 Auto-scaling | Automatically adjusts view to show important features |
| 🎯 Intersection Detection | Automatically finds and marks intersection points |
| 📝 Smart Labels | Intelligent placement of labels to avoid overlap |
| 🔍 Point Analysis | Click any point to see detailed function information |
| 📊 Multiple Functions | Compare multiple functions on the same graph |

### ⚙️ Technical Capabilities
| Capability | Description |
|------------|-------------|
| 🚀 Performance | Optimized for smooth rendering of complex functions |
| 💻 Cross-platform | Works on Windows, macOS, and Linux |
| 🎨 High DPI | Support for high-resolution displays |
| 🔄 Real-time Updates | Instant updates when modifying parameters |

### 🎓 Educational Tools
| Tool | Description |
|------|-------------|
| 📚 Function Templates | Pre-built templates for common functions |
| 🔍 Step-by-step Analysis | Detailed breakdown of function properties |
| 📊 Visual Aids | Color-coded graphs and clear annotations |
| 💡 Error Feedback | Clear error messages with suggestions for correction |

## 🚀 Getting Started

### System Requirements
- Python 3.9+
- pip package manager

### Installation

Ensure the following Python libraries are installed:

- PyQt6
- NumPy
- SymPy
- Matplotlib
- scipy

You can install all dependencies at once using the following command:

```bash
pip install PyQt6 requests semver sympy numpy matplotlib
```

### Running the Application

1. Save the `graphing_calculator.py` file to your local machine.
2. Open a terminal or command prompt and navigate to the directory containing the file.
3. Run the following command to start the application:

    ```bash
    python graphing_calculator.py
    ```

## Usage Instructions

1. **Enter Expressions**:
    - In the "Enter 2D equations" input field, enter one or more 2D expressions.
    - Input only expressions, not equations. For example, enter `sin(x) x^2 |x|` to plot `sin(x)`, `x²`, and `|x|`.
    - Use spaces to separate multiple expressions. Spaces are used to distinguish different formulas.

2. **Plot Graphs**:
    - After entering the expressions, click the "Plot 2D Graphs" button.
    - The application will plot the corresponding graphs and calculate various function properties.
    - Results will be displayed in the text browser below the plot.

3. **Interactive Operations**:
    - **Zooming**: Use the mouse wheel to zoom in and out of the graph. Hold the `Ctrl` key and scroll the mouse wheel for precise zooming.
    - **Panning**: Press and hold the middle mouse button (scroll wheel) and drag to pan the graph.
    - **View Intersections**: Click on the intersection points in the graph to display their coordinates and corresponding equations.

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

## Contribution

Contributions are welcome! If you have suggestions or want to contribute code, please submit an Issue or Pull Request on the [GitHub repository](https://github.com/fzlzjerry/graphing_calculator).

## License

This project is licensed under the GNU Affero General Public License v3.0 License. See the [LICENSE](LICENSE) file for details.

## Contact Us

If you have any questions or suggestions, please reach out to us:

- **Email**: james20081204@gmail.com
- **GitHub**: [https://github.com/fzlzjerry/graphing_calculator](https://github.com/fzlzjerry/graphing_calculator)
