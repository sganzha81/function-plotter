import numpy as np
import matplotlib.pyplot as plt

from numpy import sin, cos, sqrt

formula = input("Enter function of x: ")

x = np.linspace(-10, 10, 100)
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
