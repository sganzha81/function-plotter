import os
import sys
import tkinter as tk

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from plotter.evaluator import (
    evaluate_formula,
    prepare_y_values_for_plotting,
)

MAX_FUNCTIONS = 5


def _resource_path(path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, path)


class FunctionPlotterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Function Plotter")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self._set_window_icon()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._create_widgets()

    def _set_window_icon(self):
        icon_path = _resource_path("assets/app_icon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

    def _create_widgets(self):
        self.paned_window = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=8,
            sashrelief=tk.RAISED,
            borderwidth=0,
        )
        self.paned_window.pack(fill="both", expand=True)

        self.left_panel = ctk.CTkFrame(self.paned_window, width=360)
        self.right_panel = ctk.CTkFrame(self.paned_window)

        self.paned_window.add(
            self.left_panel,
            minsize=340,
            stretch="never",
        )
        self.paned_window.add(
            self.right_panel,
            minsize=450,
            stretch="always",
        )

        self.input_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=12, pady=(12, 0))

        self._create_formula_section()

        self.x_min_label = ctk.CTkLabel(self.input_frame, text="X min:")
        self.x_min_label.grid(row=2, column=0, padx=8, pady=8, sticky="w")

        self.x_min_entry = ctk.CTkEntry(self.input_frame)
        self.x_min_entry.insert(0, "-10")
        self.x_min_entry.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        self.x_max_label = ctk.CTkLabel(self.input_frame, text="X max:")
        self.x_max_label.grid(row=3, column=0, padx=8, pady=8, sticky="w")

        self.x_max_entry = ctk.CTkEntry(self.input_frame)
        self.x_max_entry.insert(0, "10")
        self.x_max_entry.grid(row=3, column=1, padx=8, pady=8, sticky="ew")

        self.points_label = ctk.CTkLabel(self.input_frame, text="Points:")
        self.points_label.grid(row=4, column=0, padx=8, pady=8, sticky="w")

        self.points_entry = ctk.CTkEntry(self.input_frame)
        self.points_entry.insert(0, "200")
        self.points_entry.grid(row=4, column=1, padx=8, pady=8, sticky="ew")

        self.plot_button = ctk.CTkButton(
            self.input_frame,
            text="Plot graph",
            command=self.plot_graph,
        )
        self.plot_button.grid(
            row=5, column=0, columnspan=2, padx=8, pady=12, sticky="ew"
        )

        self.input_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="Enter a formula and click Plot graph.",
            wraplength=320,
        )
        self.status_label.pack(fill="x", padx=20, pady=(0, 12))

        self.figure, self.ax = plt.subplots(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_panel)
        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            self.right_panel,
            pack_toolbar=False,
        )
        self.toolbar.update()
        self._create_toolbar()
        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12),
        )

    def _create_formula_section(self):
        self.formula_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.formula_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.formula_frame.grid_columnconfigure(1, weight=1)

        self.formula_rows = []
        self.add_function_button = ctk.CTkButton(
            self.input_frame,
            text="Add function",
            command=self._add_formula_row,
        )
        self.add_function_button.grid(
            row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="ew"
        )
        self._add_formula_row("x**2")

    def _add_formula_row(self, formula=""):
        if len(self.formula_rows) >= MAX_FUNCTIONS:
            return

        label = ctk.CTkLabel(self.formula_frame, text="")
        entry = ctk.CTkEntry(self.formula_frame)
        entry.insert(0, formula)
        remove_button = ctk.CTkButton(
            self.formula_frame,
            text="Remove",
            width=68,
        )

        formula_row = {
            "label": label,
            "entry": entry,
            "remove_button": remove_button,
        }
        remove_button.configure(
            command=lambda row=formula_row: self._remove_formula_row(row)
        )
        self.formula_rows.append(formula_row)
        self._refresh_formula_rows()

    def _remove_formula_row(self, formula_row):
        if len(self.formula_rows) == 1:
            return

        for widget in formula_row.values():
            widget.destroy()

        self.formula_rows.remove(formula_row)
        self._refresh_formula_rows()

    def _refresh_formula_rows(self):
        for row_number, formula_row in enumerate(self.formula_rows, start=1):
            formula_row["label"].configure(text=f"Formula {row_number}:")
            formula_row["label"].grid(
                row=row_number - 1, column=0, padx=4, pady=8, sticky="w"
            )
            formula_row["entry"].grid(
                row=row_number - 1, column=1, padx=4, pady=8, sticky="ew"
            )
            formula_row["remove_button"].grid(
                row=row_number - 1, column=2, padx=4, pady=8
            )

        self._update_formula_controls_state()

    def _update_formula_controls_state(self):
        remove_state = "disabled" if len(self.formula_rows) == 1 else "normal"
        for formula_row in self.formula_rows:
            formula_row["remove_button"].configure(state=remove_state)

        add_state = "disabled" if len(self.formula_rows) >= MAX_FUNCTIONS else "normal"
        self.add_function_button.configure(state=add_state)

    def _get_non_empty_formulas(self):
        formulas = []
        for row_number, formula_row in enumerate(self.formula_rows, start=1):
            formula = formula_row["entry"].get().strip()
            if formula:
                formulas.append((row_number, formula))

        return formulas

    def _create_toolbar(self):
        self.toolbar_frame = ctk.CTkFrame(self.right_panel)
        self.toolbar_frame.pack(fill="x", padx=12, pady=12)

        toolbar_buttons = (
            ("⌂ Home", self.toolbar.home),
            ("← Back", self.toolbar.back),
            ("→ Forward", self.toolbar.forward),
            ("✋ Pan", self.toolbar.pan),
            ("🔍 Zoom", self.toolbar.zoom),
            ("💾 Save", self.toolbar.save_figure),
        )

        for column, (text, command) in enumerate(toolbar_buttons):
            button = ctk.CTkButton(
                self.toolbar_frame,
                text=text,
                command=command,
                width=84,
            )
            button.grid(row=0, column=column, padx=4, pady=6, sticky="ew")
            self.toolbar_frame.grid_columnconfigure(column, weight=1)

    def plot_graph(self):
        formulas = self._get_non_empty_formulas()

        try:
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            points = int(self.points_entry.get())
        except ValueError:
            self.status_label.configure(
                text="Error: x_min, x_max and points must be numbers."
            )
            return

        if not formulas:
            self.status_label.configure(
                text="Error: enter at least one formula to plot."
            )
            return

        if x_min >= x_max:
            self.status_label.configure(text="Error: x_min must be less than x_max.")
            return

        if points < 2:
            self.status_label.configure(text="Error: points must be at least 2.")
            return

        x = np.linspace(x_min, x_max, points)
        plot_data = []

        for formula_number, formula in formulas:
            y = evaluate_formula(formula, x)
            prepared_y, error_message = prepare_y_values_for_plotting(
                y,
                expected_length=points,
            )
            if prepared_y is None:
                self.status_label.configure(
                    text=f"Error in Formula {formula_number}: {error_message}"
                )
                return

            plot_data.append((formula, prepared_y))

        self.ax.clear()
        for formula, y in plot_data:
            self.ax.plot(x, y, label=formula)

        self.ax.set_title("Function Plotter")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True)
        self.ax.legend()

        self.canvas.draw()

        self.status_label.configure(text="Graph plotted successfully.")

    def on_closing(self):
        """Close the app and clean up matplotlib resources."""
        if hasattr(self, "toolbar"):
            self.toolbar.destroy()

        if hasattr(self, "toolbar_frame"):
            self.toolbar_frame.destroy()

        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        if hasattr(self, "figure"):
            plt.close(self.figure)

        self.quit()
        self.destroy()


def run_app():
    app = FunctionPlotterApp()
    app.mainloop()
