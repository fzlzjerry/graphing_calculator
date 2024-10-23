# Graphing Calculator

This is a simple graphing calculator designed for pre-calculus students. It not only plots graphs but also provides first derivatives, domain, asymptotes, y-intercepts, and more. Additionally, it can display the solutions (intersections) between graphs.

## Features

- **Plot 2D Graphs**: Input multiple 2D expressions and plot them on the same coordinate system.
- **Function Properties Calculation**:
    - **Zero Points (X-Intercepts)**: Automatically calculates and displays the zeros of the function.
    - **Y-Intercept**: Calculates and displays the y-intercept of the function.
    - **End Behavior**: Analyzes the behavior of the function as \( x \) approaches positive and negative infinity.
    - **First Derivative**: Computes and displays the first derivative of the function.
    - **Critical Points**: Identifies and displays the critical points (local minima, maxima, and inflection points).
    - **Domain**: Determines and displays the domain of the function.
    - **Range**: Calculates and displays the range of the function.
    - **Asymptotes**: Automatically detects and displays horizontal and vertical asymptotes.
    - **Discontinuities**: Identifies and displays points of discontinuity.
    - **Second Derivative**: Computes and displays the second derivative for concavity analysis.
- **Intersection Calculation**: Automatically calculates and displays the intersection points between multiple functions.
- **Interactive Graphics**: Supports zooming and panning for detailed viewing of graph features.
- **Graph Annotations**: Click on points in the graph to display their coordinates and corresponding equations.

## Screenshot

![Graphing Calculator UI](https://ice.frostsky.com/2024/10/23/93aa0a1f85f2022dda0966ba84367775.png)

## Installation Guide

### Prerequisites

- **Python 3.7 or higher**
- **pip** package manager

### Required Libraries

Ensure the following Python libraries are installed:

- PyQt6
- NumPy
- SymPy
- Matplotlib

You can install all dependencies at once using the following command:

```bash
pip install PyQt6 numpy sympy matplotlib
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
|x| x^3 - 3x
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
