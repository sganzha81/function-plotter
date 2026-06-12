import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from plotter.evaluator import (
    evaluate_formula,
    validate_formula_at_points,
    validate_y_values,
)


class FunctionPlotterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Function Plotter")
        self.geometry("900x650")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._create_widgets()

    def _create_widgets(self):
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=16, pady=16)

        self.formula_label = ctk.CTkLabel(self.input_frame, text="Formula:")
        self.formula_label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

        self.formula_entry = ctk.CTkEntry(self.input_frame, width=300)
        self.formula_entry.insert(0, "x**2")
        self.formula_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self.x_min_label = ctk.CTkLabel(self.input_frame, text="X min:")
        self.x_min_label.grid(row=1, column=0, padx=8, pady=8, sticky="w")

        self.x_min_entry = ctk.CTkEntry(self.input_frame)
        self.x_min_entry.insert(0, "-10")
        self.x_min_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        self.x_max_label = ctk.CTkLabel(self.input_frame, text="X max:")
        self.x_max_label.grid(row=2, column=0, padx=8, pady=8, sticky="w")

        self.x_max_entry = ctk.CTkEntry(self.input_frame)
        self.x_max_entry.insert(0, "10")
        self.x_max_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        self.points_label = ctk.CTkLabel(self.input_frame, text="Points:")
        self.points_label.grid(row=3, column=0, padx=8, pady=8, sticky="w")

        self.points_entry = ctk.CTkEntry(self.input_frame)
        self.points_entry.insert(0, "200")
        self.points_entry.grid(row=3, column=1, padx=8, pady=8, sticky="ew")

        self.plot_button = ctk.CTkButton(
            self.input_frame,
            text="Plot graph",
            command=self.plot_graph,
        )
        self.plot_button.grid(
            row=4, column=0, columnspan=2, padx=8, pady=12, sticky="ew"
        )

        self.input_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(
            self, text="Enter a formula and click Plot graph."
        )
        self.status_label.pack(fill="x", padx=16, pady=(0, 8))

        self.figure, self.ax = plt.subplots(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=16)

    def plot_graph(self):
        formula = self.formula_entry.get().strip()

        try:
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            points = int(self.points_entry.get())
        except ValueError:
            self.status_label.configure(
                text="Error: x_min, x_max and points must be numbers."
            )
            return

        if not formula:
            self.status_label.configure(text="Error: formula cannot be empty.")
            return

        if x_min >= x_max:
            self.status_label.configure(text="Error: x_min must be less than x_max.")
            return

        if points < 2:
            self.status_label.configure(text="Error: points must be at least 2.")
            return

        validation_points = []

        if x_min < 0 < x_max:
            validation_points.append(0.0)

        if validation_points:
            is_valid, error_message = validate_formula_at_points(
                formula, validation_points
            )

            if not is_valid:
                self.status_label.configure(text=f"Error: {error_message}")
                return

        x = np.linspace(x_min, x_max, points)
        y = evaluate_formula(formula, x)
        is_valid, error_message = validate_y_values(y, expected_length=points)

        if not is_valid:
            self.status_label.configure(text=f"Error: {error_message}")
            return

        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_title(f"y = {formula}")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True)

        self.canvas.draw()

        self.status_label.configure(text="Graph plotted successfully.")

    def on_closing(self):
        """Close the app and clean up matplotlib resources."""
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        if hasattr(self, "figure"):
            plt.close(self.figure)

        self.quit()
        self.destroy()


def run_app():
    app = FunctionPlotterApp()
    app.mainloop()
