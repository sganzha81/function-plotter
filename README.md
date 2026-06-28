# Function Plotter

Function Plotter is an educational Python application for plotting functions of
one variable, `x`. It can be used through an interactive command-line interface
or a CustomTkinter graphical interface.

## Features

- CLI and GUI modes
- Plot from 1 to 5 functions on the same graph
- Shared x-axis range and number of points
- Legend showing plotted formulas
- Common math names: `sin`, `cos`, `tan`, `sqrt`, `log`, `exp`, `abs`, `pi`,
  and `e`
- Discontinuity handling for functions such as `1/x`, `tan(x)`, `sqrt(x)`,
  and `log(x)`
- GUI toolbar with Home, Back, Forward, Pan, Zoom, and Save controls
- Application window icon
- Unit tests for formula evaluation and y-value preparation

## Project Structure

- `main.py` — CLI entry point
- `gui.py` — GUI entry point
- `plotter/evaluator.py` — formula evaluation and y-value preparation
- `plotter/gui.py` — CustomTkinter GUI
- `assets/app_icon.png` — application icon
- `tests/test_evaluator.py` — evaluator unit tests

## Installation

Create a virtual environment and install the dependencies:

```bash
git clone https://github.com/sganzha81/function-plotter.git
cd function-plotter
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On some Linux systems, Tkinter may need to be installed separately:

```bash
sudo apt install python3-tk
```

## Usage

### CLI

```bash
python main.py
```

Follow the prompts to enter one or more formulas, the x-axis range, and the
number of points. The CLI can also save the resulting graph as a PNG file.

### GUI

```bash
python gui.py
```

Use the controls on the left to enter formulas and plot settings. The graph and
its navigation toolbar appear on the right.

## Formula Examples

- `x**2`
- `sin(x)`
- `cos(x)`
- `sin(40*x)`
- `1/x`
- `sqrt(x)`
- `log(x)`
- `exp(-x**2)`

## Important Syntax Notes

- Use `x` as the variable.
- Use Python-style exponentiation: `x**2`, not `x^2`.
- Formulas can use only the supported math names listed in the Features
  section.
- Formulas are evaluated in a restricted `eval` environment. This is an
  educational project, not a production-safe expression parser.

## Discontinuities

Invalid or infinite calculated values are converted to `NaN`, which tells
Matplotlib to leave gaps in the plotted line. Sharp outlier jumps are also
treated as gaps to avoid connecting branches across vertical asymptotes. This
allows functions such as `1/x`, `tan(x)`, `sqrt(x)`, and `log(x)` to be plotted
over the valid parts of the selected range.

## Running Tests

```bash
python -m unittest
```

## Development Notes

- Code is formatted with Black.
- The GUI uses CustomTkinter.
- Plotting and numerical calculations use Matplotlib and NumPy.
- Current feature work may be developed in separate branches.

## Roadmap

- Replace `eval` with a safer parser or SymPy
- Add formula color and line-style controls
- Export plot settings
- Save and load plot presets
- Improve the GUI layout and error display

## License

License not specified yet.
