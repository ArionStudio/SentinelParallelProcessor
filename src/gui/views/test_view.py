# src/gui/views/test_view.py

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, List
import io

from PIL import Image, ImageTk
import matplotlib.pyplot as plt

from src.gui.utils.system_info import get_system_specs

if TYPE_CHECKING:
    from src.gui.controllers.test_controller import TestController
    from src.gui.app import MainApplication

class TestView(ttk.Frame):
    def __init__(self, parent: "MainApplication", controller: "TestController", **kwargs):
        super().__init__(parent, padding=10, **kwargs)
        self.app = parent
        self.controller = controller
        self.controller.set_view(self)
        self.plot_photos = []
        self._setup_ui()

    def _setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.run_button = ttk.Button(top_frame, text="Run All Tests", command=self.controller.handle_run_tests)
        self.run_button.pack(side="left", padx=(0, 10))

        self.report_button = ttk.Button(top_frame, text="Generate Full Report from Last Results", command=self.controller.handle_generate_full_report)
        self.report_button.pack(side="left", padx=(0, 20))

        back_button = ttk.Button(top_frame, text="< Back to Map", command=lambda: self.app.view_controller.switch_to_map())
        back_button.pack(side="left")

        self.status_label = ttk.Label(top_frame, text="Ready to run tests.")
        self.status_label.pack(side="right", padx=10)

        self.progress_bar = ttk.Progressbar(top_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side="right", padx=10)

        canvas_frame = ttk.Frame(self)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, padding=10)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._display_system_specs()

    def _display_system_specs(self):
        specs_frame = ttk.LabelFrame(self.scrollable_frame, text="Test Platform Specification", padding=10)
        specs_frame.pack(fill="x", expand=True, pady=5, padx=5)
        specs_frame.grid_columnconfigure(1, weight=1)

        try:
            specs = get_system_specs()
            row = 0
            for key, value in specs.items():
                key_label = ttk.Label(specs_frame, text=f"{key}:", font=("Segoe UI", 9, "bold"))
                key_label.grid(row=row, column=0, sticky="nw", padx=5, pady=2)
                
                value_label = ttk.Label(specs_frame, text=value, wraplength=600, justify="left")
                value_label.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                row += 1
            
            note_text = "Note: Performance is also heavily influenced by factors not listed here, such as PCIe bus speed, VRAM speed, and system load."
            note_label = ttk.Label(specs_frame, text=note_text, font=("Segoe UI", 8, "italic"))
            note_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 2))

        except Exception as e:
            error_label = ttk.Label(specs_frame, text=f"Could not retrieve system specs: {e}", foreground="red")
            error_label.pack()

    def display_results(self, figures: List[plt.Figure], descriptions: List[str]):
        self.clear_results()
        self.plot_photos = []

        for i, fig in enumerate(figures):
            container = ttk.LabelFrame(self.scrollable_frame, text=fig.get_suptitle(), padding=10)
            container.pack(fill="x", expand=True, pady=10, padx=5)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=100)
            buf.seek(0)
            img = Image.open(buf)
            photo = ImageTk.PhotoImage(img)
            self.plot_photos.append(photo)

            plot_label = ttk.Label(container, image=photo)
            plot_label.pack()

            if i < len(descriptions):
                desc_label = ttk.Label(container, text=descriptions[i], wraplength=800, justify="left")
                desc_label.pack(pady=(10, 0))
            
            plt.close(fig)

    def update_progress(self, value: float, text: str):
        self.progress_bar['value'] = value
        self.status_label.config(text=text)
        self.app.update_idletasks()

    def clear_results(self):
        for widget in self.scrollable_frame.winfo_children()[1:]:
            widget.destroy()
        self.plot_photos = []

    def set_buttons_state(self, is_enabled: bool):
        state = "normal" if is_enabled else "disabled"
        self.run_button.config(state=state)
        self.report_button.config(state=state)