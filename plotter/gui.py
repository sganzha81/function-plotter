import os
import sys
import tkinter as tk

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from plotter.domain_engine import analyze_domain
from plotter.evaluator import evaluate_formula

MAX_FUNCTIONS = 5


def _resource_path(path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, path)


class FunctionPlotterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.functions = []
        self.domain_signals = []
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

        x = np.linspace(x_min, x_max, points)
        y = evaluate_formula(formula, x)
        if y is None:
            self.status_label.configure(text="Error: invalid formula.")
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

    def _plot_function_segments(self, x, y, formula, segment_breaks):
        x_segments = np.split(x, segment_breaks)
        y_segments = np.split(y, segment_breaks)
        color = None

        for segment_number, (x_segment, y_segment) in enumerate(
            zip(x_segments, y_segments)
        ):
            line, = self.ax.plot(
                x_segment,
                y_segment,
                color=color,
                label=formula if segment_number == 0 else None,
            )
            if color is None:
                color = line.get_color()

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
        x = np.linspace(x_min, x_max, points)
        self.domain_signals = []

        self.ax.clear()
        for formula_number, formula in enumerate(self.functions, start=1):
            y = evaluate_formula(formula, x)
            if y is None:
                errors.append(f"Function {formula_number}: invalid formula.")
                continue

            signals = analyze_domain(x, y, formula)
            self.domain_signals.append(signals)
            self._plot_function_segments(
                x,
                y,
                formula,
                signals["segment_breaks"],
            )

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
