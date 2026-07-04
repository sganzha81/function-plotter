import os
import sys
import tkinter as tk

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from plotter.evaluator import evaluate_formula

MAX_FUNCTIONS = 5


def _resource_path(path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, path)


def classify_function(formula: str) -> str:
    normalized_formula = formula.lower().replace(" ", "")

    if "tan" in normalized_formula:
        return "tan_asymptote"
    reciprocal_formula = normalized_formula.replace("(", "").replace(")", "")
    if "1/x" in reciprocal_formula or "x**-1" in reciprocal_formula:
        return "reciprocal_asymptote"
    if "log" in normalized_formula or "sqrt" in normalized_formula:
        return "domain_limited"
    return "smooth"


def get_sampling_points(base_points: int, function_type: str) -> int:
    if function_type in {"tan_asymptote", "reciprocal_asymptote"}:
        return max(base_points * 3, 800)
    return base_points


def _insert_x_gap_separators(x_values, keep_mask):
    kept_indices = np.flatnonzero(keep_mask)
    if kept_indices.size == 0:
        return np.array([], dtype=float)

    gap_positions = np.flatnonzero(np.diff(kept_indices) > 1) + 1
    return np.insert(
        x_values[kept_indices],
        gap_positions,
        np.nan,
    )


def build_safe_x_grid(x_min, x_max, points, function_type):
    x_values = np.linspace(x_min, x_max, points)
    if function_type not in {"tan_asymptote", "reciprocal_asymptote"}:
        return x_values

    epsilon = abs(x_max - x_min) / points * 2
    keep_mask = np.ones(x_values.shape, dtype=bool)

    if function_type == "tan_asymptote":
        first_k = int(np.floor((x_min - np.pi / 2) / np.pi)) - 1
        last_k = int(np.ceil((x_max - np.pi / 2) / np.pi)) + 1
        for k in range(first_k, last_k + 1):
            asymptote = np.pi / 2 + k * np.pi
            keep_mask &= np.abs(x_values - asymptote) >= epsilon
    elif x_min <= 0 <= x_max:
        keep_mask &= np.abs(x_values) >= epsilon

    # NaN separators preserve gaps while keeping one x array and one plot artist.
    return _insert_x_gap_separators(x_values, keep_mask)


def preprocess_y_for_plotting(x, y, function_type):
    if y is None:
        return None

    try:
        processed_y = np.asarray(y, dtype=float).copy()
    except (TypeError, ValueError):
        return None

    processed_y[~np.isfinite(processed_y)] = np.nan
    return processed_y


def _prepare_function_values(
    formula,
    x,
    y,
    expected_length,
    function_type=None,
):
    if function_type is None:
        function_type = classify_function(formula)

    processed_y = preprocess_y_for_plotting(
        x,
        y,
        function_type,
    )
    if processed_y is None:
        return None, "Invalid formula."
    if processed_y.ndim != 1 or len(processed_y) != expected_length:
        return None, "Formula returned an unsupported result."
    if not np.isfinite(processed_y).any():
        return None, "Formula has no valid values in the selected x range."
    return processed_y, ""


class FunctionPlotterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.functions = []
        self.render_mode = "debounced"
        self._replot_job = None
        self.debounce_delay_ms = 300
        self._plot_ready = False

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
        self.x_min_entry.bind("<KeyRelease>", self._on_plot_input_changed)

        self.x_max_label = ctk.CTkLabel(self.input_frame, text="X max:")
        self.x_max_label.grid(row=3, column=0, padx=8, pady=8, sticky="w")

        self.x_max_entry = ctk.CTkEntry(self.input_frame)
        self.x_max_entry.insert(0, "10")
        self.x_max_entry.grid(row=3, column=1, padx=8, pady=8, sticky="ew")
        self.x_max_entry.bind("<KeyRelease>", self._on_plot_input_changed)

        self.points_label = ctk.CTkLabel(self.input_frame, text="Points:")
        self.points_label.grid(row=4, column=0, padx=8, pady=8, sticky="w")

        self.points_entry = ctk.CTkEntry(self.input_frame)
        self.points_entry.insert(0, "250")
        self.points_entry.grid(row=4, column=1, padx=8, pady=8, sticky="ew")
        self.points_entry.bind("<KeyRelease>", self._on_plot_input_changed)

        self.plot_button = ctk.CTkButton(
            self.input_frame,
            text="Replot",
            command=self.trigger_replot,
        )
        self.plot_button.grid(
            row=5, column=0, columnspan=2, padx=8, pady=12, sticky="ew"
        )

        self.instant_render_switch = ctk.CTkSwitch(
            self.input_frame,
            text="Instant render (no debounce)",
            command=self._on_render_mode_changed,
        )
        self.instant_render_switch.grid(
            row=6, column=0, columnspan=2, padx=8, pady=(0, 12), sticky="w"
        )

        self.input_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="Enter a formula and click Add Function.",
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
        self._plot_ready = True
        self.trigger_replot()

    def _create_formula_section(self):
        self.formula_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.formula_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.formula_frame.grid_columnconfigure(1, weight=1)

        self.formula_label = ctk.CTkLabel(
            self.formula_frame,
            text="Formula:",
        )
        self.formula_label.grid(row=0, column=0, padx=4, pady=8, sticky="w")

        self.formula_entry = ctk.CTkEntry(self.formula_frame)
        self.formula_entry.grid(
            row=0,
            column=1,
            columnspan=2,
            padx=4,
            pady=8,
            sticky="ew",
        )
        self.formula_entry.bind("<Return>", self.add_function)

        self.add_function_button = ctk.CTkButton(
            self.formula_frame,
            text="Add Function",
            command=self.add_function,
        )
        self.add_function_button.grid(
            row=1, column=0, padx=4, pady=(0, 8), sticky="ew"
        )
        self.update_function_button = ctk.CTkButton(
            self.formula_frame,
            text="Update Function",
            command=self.update_selected_function,
        )
        self.update_function_button.grid(
            row=1, column=1, padx=4, pady=(0, 8), sticky="ew"
        )
        self.remove_function_button = ctk.CTkButton(
            self.formula_frame,
            text="Remove Selected",
            command=self.remove_selected_function,
        )
        self.remove_function_button.grid(
            row=1, column=2, padx=4, pady=(0, 8), sticky="ew"
        )

        self.function_list_label = ctk.CTkLabel(
            self.formula_frame,
            text="Active functions:",
        )
        self.function_list_label.grid(
            row=2, column=0, columnspan=3, padx=4, sticky="w"
        )

        self.function_list = tk.Listbox(
            self.formula_frame,
            height=6,
            selectmode=tk.SINGLE,
            exportselection=False,
        )
        self.function_list.bind("<<ListboxSelect>>", self._on_function_selected)
        self.function_list.grid(
            row=3, column=0, columnspan=3, padx=4, pady=(4, 8), sticky="ew"
        )
        self.update_function_list()

    def add_function(self, _event=None):
        formula = self.formula_entry.get().strip()
        if not formula:
            self.status_label.configure(text="Error: enter a formula to add.")
            return

        if len(self.functions) >= MAX_FUNCTIONS:
            self.status_label.configure(
                text=f"Error: a maximum of {MAX_FUNCTIONS} functions is allowed."
            )
            return

        self.functions.append(formula)
        self.formula_entry.delete(0, "end")
        self.update_function_list()
        self.trigger_replot()

    def _on_function_selected(self, _event=None):
        selection = self.function_list.curselection()
        if not selection:
            return

        self.formula_entry.delete(0, "end")
        self.formula_entry.insert(0, self.functions[selection[0]])

    def update_selected_function(self):
        selection = self.function_list.curselection()
        if not selection:
            self.status_label.configure(
                text="Select a function from the list to update."
            )
            return

        formula = self.formula_entry.get().strip()
        if not formula:
            self.status_label.configure(text="Error: enter an updated formula.")
            return

        try:
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            points = int(self.points_entry.get())
        except ValueError:
            self.status_label.configure(
                text="Error: x_min, x_max and points must be numbers."
            )
            return

        if x_min >= x_max or points < 2:
            self.status_label.configure(
                text="Error: use a valid x range and at least 2 points."
            )
            return

        function_type = classify_function(formula)
        function_points = get_sampling_points(points, function_type)
        x_plot = build_safe_x_grid(
            x_min,
            x_max,
            function_points,
            function_type,
        )
        if x_plot.size == 0:
            self.status_label.configure(text="Error: no plottable x values.")
            return

        y = evaluate_formula(formula, x_plot)
        processed_y, error_message = _prepare_function_values(
            formula,
            x_plot,
            y,
            len(x_plot),
            function_type,
        )
        if processed_y is None:
            self.status_label.configure(text=f"Error: {error_message}")
            return

        selected_index = selection[0]
        self.functions[selected_index] = formula
        self.update_function_list()
        self.function_list.selection_set(selected_index)
        self.function_list.activate(selected_index)
        self.trigger_replot()

    def remove_selected_function(self):
        selection = self.function_list.curselection()
        if not selection:
            self.status_label.configure(
                text="Select a function from the list to remove."
            )
            return

        self.functions.pop(selection[0])
        self.update_function_list()
        self.trigger_replot()

    def update_function_list(self):
        self.function_list.delete(0, tk.END)
        for formula in self.functions:
            self.function_list.insert(tk.END, formula)

        self.add_function_button.configure(
            state="disabled" if len(self.functions) >= MAX_FUNCTIONS else "normal"
        )

    def _on_plot_input_changed(self, _event=None):
        self.trigger_replot()

    def _on_render_mode_changed(self):
        self.render_mode = (
            "instant" if self.instant_render_switch.get() else "debounced"
        )
        if self.render_mode == "instant":
            self._cancel_scheduled_replot()

    def trigger_replot(self):
        if not self._plot_ready:
            return

        if self.render_mode == "instant":
            self._cancel_scheduled_replot()
            self.replot()
        else:
            self.schedule_replot()

    def schedule_replot(self):
        self._cancel_scheduled_replot()
        self._replot_job = self.after(
            self.debounce_delay_ms,
            self._run_scheduled_replot,
        )

    def _cancel_scheduled_replot(self):
        if self._replot_job is not None:
            self.after_cancel(self._replot_job)
            self._replot_job = None

    def _run_scheduled_replot(self):
        self._replot_job = None
        self.replot()

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

    def replot(self):
        try:
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            points = int(self.points_entry.get())
        except ValueError:
            self.status_label.configure(
                text="Error: x_min, x_max and points must be numbers."
            )
            return

        if x_min >= x_max:
            self.status_label.configure(text="Error: x_min must be less than x_max.")
            return

        if points < 2:
            self.status_label.configure(text="Error: points must be at least 2.")
            return

        errors = []

        self.ax.clear()
        for formula_number, formula in enumerate(self.functions, start=1):
            function_type = classify_function(formula)
            function_points = get_sampling_points(points, function_type)
            x_plot = build_safe_x_grid(
                x_min,
                x_max,
                function_points,
                function_type,
            )
            if x_plot.size == 0:
                errors.append(
                    f"Function {formula_number}: no plottable x values."
                )
                continue

            y = evaluate_formula(formula, x_plot)
            processed_y, error_message = _prepare_function_values(
                formula,
                x_plot,
                y,
                len(x_plot),
                function_type,
            )
            if processed_y is None:
                errors.append(f"Function {formula_number}: {error_message}")
                continue

            self.ax.plot(x_plot, processed_y, label=formula)

        self.ax.set_title("Function Plotter")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True)
        if self.ax.lines:
            self.ax.legend()

        self.canvas.draw()

        if errors:
            self.status_label.configure(text="Error: " + " ".join(errors))
        elif self.functions:
            self.status_label.configure(text="Graph updated successfully.")
        else:
            self.status_label.configure(text="Add a function to start plotting.")

    def plot_graph(self):
        """Backward-compatible alias for the previous plot action."""
        self.trigger_replot()

    def on_closing(self):
        """Close the app and clean up matplotlib resources."""
        self._cancel_scheduled_replot()

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
