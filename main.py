import numpy as np
import matplotlib.pyplot as plt

from numpy import sin, cos, sqrt

formula = input("Enter function of x: ")
x_min = float(input("Enter x min: "))
x_max = float(input("Enter x max: "))
num_points = int(input("Enter number of points: "))

if x_min >= x_max:
    print("Error: x min must be less than x max")
    exit()

x = np.linspace(x_min, x_max, num_points)
try:
    y = eval(formula)
except:
    print("Ошибка: формула введена неправильно")
    print("Примеры правильных формул: x**2, sin(x), x**2 + 3*x - 1")
else:
    plt.plot(x, y)
    plt.title(f"Graph of y = {formula}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.show()
