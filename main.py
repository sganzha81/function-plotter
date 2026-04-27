import numpy as np
import matplotlib.pyplot as plt
from numpy import sin, cos, sqrt
from typing import Optional

def evaluate_formula(formula: str, x_val: float) -> Optional[float]:
    """
    Проверяет формулу на синтаксическую корректность и возвращает число.
    Если формула невалидна или возвращает не число — вернёт None.
    """
    try:
        # Временно подставляем x_val (обычно 0) и вычисляем
        x = x_val
        result = eval(formula)
        # Проверяем, что результат — число, а не функция или None
        if np.isscalar(result):
            return float(result)  # приводим к float, если это число
        else:
            return None
    except:
        return None

def plot_graph(formula: str, x_min: float, x_max: float, num_points: int) -> None:
    """Строит график функции, сохраняет его в файл по желанию пользователя."""
    # Создаём массив x
    x = np.linspace(x_min, x_max, num_points)
    # Вычисляем y
    try:
        y = eval(formula)
    except:
        print("Error: invalid formula")
        print("Examples: x**2, sin(x), x**2 + 3*x - 1")
        return

    # Проверка на нечисловые значения
    if np.any(np.isnan(y)):
        print("Invalid values in formula (e.g., sqrt of negative number)")
        return

    # Строим график
    plt.plot(x, y)
    plt.title(f"Graph of y = {formula}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)

    # Сохранение в файл
    save_choice: str = input("Save plot to file? (y/n): ").strip().lower()
    if save_choice == 'y':
        filename: str = input("Enter filename (default: plot.png): ").strip()
        if not filename:
            filename = "plot.png"
        if not filename.endswith('.png'):
            filename += '.png'
        plt.savefig(filename)
        print(f"Plot saved as {filename}")

    plt.show()

def main() -> None:
    """Основной цикл программы."""
    while True:
        formula: str = input("Enter function of x (or type 'quit' to exit): ")
        if formula == 'quit':
            break

        # Проверяем формулу (с x=0)
        if evaluate_formula(formula, 0.0) is None:
            print("Error: invalid formula (syntax or non-numeric result)")
            print("Examples: x**2, sin(x), x**2 + 3*x - 1")
            continue

        # Запрашиваем параметры графика
        x_min: float = float(input("Enter x min: "))
        x_max: float = float(input("Enter x max: "))
        if x_min >= x_max:
            print("Error: x min must be less than x max")
            continue

        num_points: int = int(input("Enter number of points: "))

        # Строим график
        plot_graph(formula, x_min, x_max, num_points)

    print("Goodbye!")

if __name__ == "__main__":
    main()