# Function Plotter

A small Python learning project that plots a mathematical function.

The script runs in interactive mode:
- asks for a function formula in terms of `x`;
- asks for a range (`x min`, `x max`);
- asks for the number of points;
- draws the plot using `matplotlib`.

## Features

- Supports basic operations: `+`, `-`, `*`, `/`, `**`
- Supports `numpy` functions already imported in the script:
  - `sin(x)`
  - `cos(x)`
  - `sqrt(x)`
- Repeated formula input in a loop until `quit`
- Basic input validation (invalid formula, invalid range)

## Installation

If you use Bash (macOS/Linux or Git Bash on Windows), run:

```bash
git clone https://github.com/sganzha81/function-plotter.git
cd function-plotter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows Git Bash, if `python3` is not available, use `python` instead.

## Run

```bash
python3 main.py
```

When prompted:
1. Enter a formula, for example `x**2` or `sin(x) + x/2`
2. Enter `x min` and `x max`
3. Enter the number of points (for example, `200`)

To exit, type `quit`.

## Formula Examples

- `x**2`
- `sin(x)`
- `x**2 + 3*x - 1`
- `sqrt(x)` (works only on a valid domain/range)

## Limitations

- Formula input is evaluated with `eval`, so use only trusted local input.
- Some non-vectorized functions (for example `round(x)` or `int(x)`) do not work with the `x` array.