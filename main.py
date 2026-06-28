import matplotlib.pyplot as plt
import numpy as np

from plotter.evaluator import (
    evaluate_formula,
    prepare_y_values_for_plotting,
)

MAX_FUNCTIONS = 5


def get_formulas_from_user() -> list[str] | None:
    """Collect between one and MAX_FUNCTIONS formulas from the user."""
    formulas = []

    while len(formulas) < MAX_FUNCTIONS:
        function_number = len(formulas) + 1
        prompt = f"Enter function {function_number} of x (or type 'quit' to exit): "
        formula = input(prompt).strip()

        if function_number == 1 and formula.lower() == "quit":
            return None

        if not formula:
            print("Error: formula cannot be empty.")
            continue

        formulas.append(formula)

        if len(formulas) == MAX_FUNCTIONS:
            break

        while True:
            add_another = input("Add another function? (y/n): ").strip().lower()
            if add_another in {"y", "n"}:
                break

            print("Please enter 'y' or 'n'.")

        if add_another == "n":
            break

    return formulas


def get_plot_settings_from_user() -> tuple[float, float, int]:
    """Prompt until the user enters valid shared plot settings."""
    while True:
        try:
            x_min = float(input("Enter x min: "))
            x_max = float(input("Enter x max: "))
            num_points = int(input("Enter number of points: "))
        except ValueError:
            print("Error: x_min, x_max and points must be numbers.")
            continue

        if x_min >= x_max:
            print("Error: x min must be less than x max.")
            continue

        if num_points < 2:
            print("Error: points must be at least 2.")
            continue

        return x_min, x_max, num_points


def plot_graph(
    formulas: list[str],
    x_min: float,
    x_max: float,
    num_points: int,
) -> None:
    """Validate and plot all formulas on one graph."""
    x = np.linspace(x_min, x_max, num_points)
    plot_data = []

    for function_number, formula in enumerate(formulas, start=1):
        y = evaluate_formula(formula, x)
        prepared_y, error_message = prepare_y_values_for_plotting(
            y,
            expected_length=num_points,
        )
        if prepared_y is None:
            print(f"Error in Function {function_number}: {error_message}")
            return

        plot_data.append((formula, prepared_y))

    figure, axes = plt.subplots()
    for formula, y in plot_data:
        axes.plot(x, y, label=formula)

    axes.set_title("Function Plotter")
    axes.set_xlabel("x")
    axes.set_ylabel("y")
    axes.grid(True)
    axes.legend()

    while True:
        save_choice = input("Save plot to file? (y/n): ").strip().lower()
        if save_choice in {"y", "n"}:
            break

        print("Please enter 'y' or 'n'.")

    if save_choice == "y":
        filename = input("Enter filename (default: plot.png): ").strip()
        if not filename:
            filename = "plot.png"
        if not filename.endswith(".png"):
            filename += ".png"

        figure.savefig(filename)
        print(f"Plot saved as {filename}")

    plt.show()
    plt.close(figure)


def main() -> None:
    """Run the command-line function plotter."""
    while True:
        formulas = get_formulas_from_user()
        if formulas is None:
            break

        x_min, x_max, num_points = get_plot_settings_from_user()
        plot_graph(formulas, x_min, x_max, num_points)

    print("Goodbye!")


if __name__ == "__main__":
    main()
