import numpy as np
import matplotlib.pyplot as plt


formula = input("Enter function of x: ")

x = np.linspace(-10, 10, 100)
y = eval(formula)

plt.plot(x, y)
plt.title(f"Graph of y = {formula}")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)

plt.show()