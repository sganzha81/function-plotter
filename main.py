import numpy as np
import matplotlib.pyplot as plt
from numpy import sin, cos, sqrt

while True:
    # Запрашиваем формулу у пользователя
    formula = input("Enter function of x (or type 'quit' to exit): ")
    if formula == 'quit':
        break

    # Проверяем формулу на синтаксическую ошибку, подставляя test_x = 0
    try:
        x = 0
        test_y = eval(formula)   
        # Убедимся, что результат - число (не функция и не None)
        if not np.isscalar(test_y):
            raise ValueError
    except:
        print("Error: invalid formula")
        print("Examples: x**2, sin(x), x**2 + 3*x - 1")
        continue    # не спрашиваем параметры, начинаем цикл заново
    
    # Если формула корректна, запрашиваем параметры графика
    x_min = float(input("Enter x min: "))
    x_max = float(input("Enter x max: "))
    
    if x_min >= x_max:
        print("Error: x min must be less than x max")
        continue

    num_points = int(input("Enter number of points: "))
    
    # Создаём массив x и вычисляем y
    x = np.linspace(x_min, x_max, num_points)
    # Вычисляем y для каждого x
    try:
        y = eval(formula)
    except:
        # На всякий случай (хотя формула уже прошла проверку)
        print("Error: formula cannot be evaluated for the entire x array")
        print("This can happen if you used non-vectorized functions (e.g., round(x), int(x))")
        print("Use only numpy-compatible operations: +, -, *, /, **, sin, cos, sqrt, etc.")
        continue
    
        # Проверяем, нет ли нечисловых значений (например, sqrt отрицательного)
        if np.any(np.isnan(y)):
            print("Invalid values in formula (e.g., sqrt of negative number)")
            continue
    
    # Рисуем график
    plt.plot(x, y)
    plt.title(f"Graph of y = {formula}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.show()

print("Goodbye!")
