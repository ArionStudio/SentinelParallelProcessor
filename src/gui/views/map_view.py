# src/gui/views/map_view.py

import tkinter as tk
from tkinter import ttk, messagebox
import io
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
# ZMIANA: Usunięto niepotrzebne importy matplotlib
from typing import TYPE_CHECKING, Tuple
from multiprocessing import cpu_count

from tkintermapview import TkinterMapView
from tkintermapview.utility_functions import osm_to_decimal
from tkcalendar import DateEntry
from pyproj import Geod

from src.gui.views.test_view import TestView
# ZMIANA: Dodano import nowego modułu wizualizacji
from src.gui.utils import visualizer

if TYPE_CHECKING:
    from src.gui.app import MainApplication
    from src.gui.controllers.map_controller import MapController

# Klasa Tooltip bez zmian
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip_window, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def hide_tip(self, event=None):
        if self.tip_window: self.tip_window.destroy()
        self.tip_window = None

class MapView(ttk.Frame):
    API_RESOLUTION_LIMIT_METERS = 1500.0
    VALIDATION_SAFETY_MARGIN = 1.10
    BACKGROUND_COLOR = "#333333" 

    def __init__(self, parent: "MainApplication", controller: "MapController", initial_position: tuple, initial_zoom: int, **kwargs):
        super().__init__(parent, padding=10, **kwargs)
        self.app = parent
        self.controller = controller
        self.controller.set_view(self)
        self.initial_position = initial_position
        self.initial_zoom = initial_zoom
        
        self.result_photo = None
        self.legend_photo = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_controls_frame = ttk.Frame(self)
        top_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        left_controls_frame = ttk.Frame(top_controls_frame)
        left_controls_frame.pack(side="left", fill="x", padx=(0, 10))

        date_frame = ttk.LabelFrame(left_controls_frame, text="Date Range", padding=10)
        date_frame.pack(side="left", fill="x")
        ttk.Label(date_frame, text="Start:").pack(side="left")
        self.start_date_entry = DateEntry(date_frame, date_pattern="yyyy-mm-dd", year=2025, month=5, day=1)
        self.start_date_entry.pack(side="left", padx=5)
        ttk.Label(date_frame, text="End:").pack(side="left")
        self.end_date_entry = DateEntry(date_frame, date_pattern="yyyy-mm-dd", year=2025, month=6, day=11)
        self.end_date_entry.pack(side="left", padx=5)

        processor_frame = ttk.LabelFrame(left_controls_frame, text="Processor", padding=10)
        processor_frame.pack(side="left", fill="x", padx=10)
        
        self.processor_var = tk.StringVar(value="GPU")
        gpu_radio = ttk.Radiobutton(processor_frame, text="GPU (Taichi)", variable=self.processor_var, value="GPU", command=self._on_processor_change)
        gpu_radio.pack(side="left")
        cpu_radio = ttk.Radiobutton(processor_frame, text="CPU (Parallel)", variable=self.processor_var, value="CPU", command=self._on_processor_change)
        cpu_radio.pack(side="left", padx=5)
        
        ttk.Label(processor_frame, text="Threads:").pack(side="left", padx=(10, 2))
        self.thread_count_var = tk.IntVar(value=cpu_count())
        self.thread_spinbox = ttk.Spinbox(processor_frame, from_=1, to=cpu_count(), textvariable=self.thread_count_var, width=5)
        self.thread_spinbox.pack(side="left")
        
        Tooltip(gpu_radio, "Fast calculations on the graphics card.")
        Tooltip(cpu_radio, "Parallel calculations on the CPU cores.\nUI may freeze for a moment during processing.")
        Tooltip(self.thread_spinbox, "Number of CPU threads to use for calculation.")

        right_buttons_frame = ttk.Frame(top_controls_frame)
        right_buttons_frame.pack(side="right")

        test_button = ttk.Button(right_buttons_frame, text="Performance Tests", command=lambda: self.app.view_controller.switch_to(TestView))
        test_button.pack(side="left", padx=(0, 20))

        self.fetch_button = ttk.Button(right_buttons_frame, text="Fetch Data for Current View", command=self.controller.handle_fetch_data)
        self.fetch_button.pack(side="left", padx=10)

        self.ndvi_button = ttk.Button(right_buttons_frame, text="Calculate NDVI", command=lambda: self.controller.handle_calculate_index("NDVI"), state="disabled")
        self.ndvi_button.pack(side="left", padx=5)
        self.ndmi_button = ttk.Button(right_buttons_frame, text="Calculate NDMI", command=lambda: self.controller.handle_calculate_index("NDMI"), state="disabled")
        self.ndmi_button.pack(side="left")

        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=1, column=0, sticky="nsew")

        map_frame = ttk.Frame(self.paned_window)
        map_frame.grid_rowconfigure(0, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)
        self.map_widget = TkinterMapView(map_frame, corner_radius=0)
        self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", max_zoom=22)
        self.map_widget.set_position(self.initial_position[0], self.initial_position[1])
        self.map_widget.set_zoom(self.initial_zoom)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        self.map_widget.bind("<B1-Motion>", self._on_map_interaction)
        self.map_widget.bind("<MouseWheel>", self._on_map_interaction)
        self.paned_window.add(map_frame, weight=1)

        result_frame = ttk.Frame(self.paned_window)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        self.result_image_label = ttk.Label(result_frame, background=self.BACKGROUND_COLOR)
        self.result_image_label.grid(row=0, column=0, sticky="nsew")
        self.legend_label = ttk.Label(result_frame)
        self.legend_label.grid(row=1, column=0, sticky="ew", pady=5)
        self.paned_window.add(result_frame, weight=1)
        self.paned_window.bind("<Configure>", self._initialize_paned_window_sash)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.status_var = tk.StringVar(value="Ready. Move map or click 'Fetch Data'.")
        ttk.Label(bottom_frame, textvariable=self.status_var).pack(side="left")
        self.timer_var = tk.StringVar(value="")
        ttk.Label(bottom_frame, textvariable=self.timer_var, font=("TkFixedFont", 10)).pack(side="right")
        
        self._on_processor_change()

    def _on_processor_change(self):
        if self.processor_var.get() == "CPU":
            self.thread_spinbox.config(state="normal")
        else:
            self.thread_spinbox.config(state="disabled")

    def get_selected_processor(self) -> str:
        return self.processor_var.get()

    def get_cpu_thread_count(self) -> int:
        try:
            count = int(self.thread_count_var.get())
            return max(1, count)
        except (tk.TclError, ValueError):
            return cpu_count()

    def _initialize_paned_window_sash(self, event=None):
        if self.paned_window.winfo_width() > 1:
            midpoint = self.paned_window.winfo_width() // 2
            self.paned_window.sashpos(0, midpoint)
            self.paned_window.unbind("<Configure>")

    def _on_map_interaction(self, event=None):
        self.set_fetch_button_state(True)
        self.set_status("Map moved. Click 'Fetch Data' to load new area.")

    # ZMIANA: Usunięto metodę _get_colormap_and_norm. Logika jest teraz w visualizer.py

    def get_view_parameters(self):
        top_left, bottom_right, image_size, zoom = self._get_precise_view_data()
        is_valid, mpp = self._validate_resolution(top_left, bottom_right, image_size)
        if not is_valid:
            messagebox.showwarning("Zoom Level Too Low", f"The current map area is too large.\n\n" f"Estimated resolution: {mpp:.2f} m/pixel\n" f"API limit: {self.API_RESOLUTION_LIMIT_METERS:.2f} m/pixel\n\n" f"Please zoom in and try again.", parent=self)
            self.set_status("Validation failed: Map area too large.")
            return None
        start_date = self.start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date_entry.get_date().strftime("%Y-%m-%d")
        time_interval = (start_date, end_date)
        return top_left, bottom_right, image_size, time_interval, zoom

    def _get_precise_view_data(self) -> tuple:
        self.map_widget.update_idletasks()
        upper_left_tile = self.map_widget.upper_left_tile_pos
        lower_right_tile = self.map_widget.lower_right_tile_pos
        zoom = self.map_widget.zoom
        nw_lat, nw_lon = osm_to_decimal(upper_left_tile[0], upper_left_tile[1], zoom)
        se_lat, se_lon = osm_to_decimal(lower_right_tile[0], lower_right_tile[1], zoom)
        top_left = (nw_lat, nw_lon)
        bottom_right = (se_lat, se_lon)
        image_size = (self.map_widget.winfo_width(), self.map_widget.winfo_height())
        return top_left, bottom_right, image_size, zoom

    def _validate_resolution(self, top_left, bottom_right, image_size) -> tuple[bool, float]:
        nw_lat, nw_lon = top_left
        se_lat, se_lon = bottom_right
        width_px, _ = image_size
        if width_px == 0: return False, float('inf')
        center_lat = (nw_lat + se_lat) / 2
        geod = Geod(ellps="WGS84")
        _, _, distance_meters = geod.inv(nw_lon, center_lat, se_lon, center_lat)
        calculated_mpp = distance_meters / width_px
        effective_mpp = calculated_mpp * self.VALIDATION_SAFETY_MARGIN
        is_valid = effective_mpp <= self.API_RESOLUTION_LIMIT_METERS
        return is_valid, effective_mpp

    def _resize_image_with_aspect_ratio(self, source_img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
        target_w, target_h = target_size
        source_w, source_h = source_img.size
        if source_w == 0 or source_h == 0: return Image.new('RGB', target_size, self.BACKGROUND_COLOR)
        source_ratio = source_w / source_h
        target_ratio = target_w / target_h
        if target_ratio > source_ratio:
            new_h = target_h
            new_w = int(new_h * source_ratio)
        else:
            new_w = target_w
            new_h = int(new_w / source_ratio)
        resized_img = source_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        final_img = Image.new("RGBA", target_size, self.BACKGROUND_COLOR)
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        final_img.paste(resized_img, (paste_x, paste_y))
        return final_img

    def _create_placeholder_image(self, width: int, height: int, text: str) -> Image.Image:
        img = Image.new('RGB', (width, height), color='gray')
        draw = ImageDraw.Draw(img)
        try: font = ImageFont.truetype("arial.ttf", size=16)
        except IOError: font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((width - text_width) / 2, (height - text_height) / 2)
        draw.text(position, text, font=font, fill='white', align="center")
        return img

    def display_result(self, index_type: str):
        if not self.winfo_exists():
            return
        self.update_idletasks()
        target_w = self.map_widget.winfo_width()
        target_h = self.map_widget.winfo_height()
        if np.all(self.controller.result_mask == 0):
            placeholder_img = self._create_placeholder_image(512, 512, "No valid data in the selected area.\n(e.g., due to clouds or location)")
            display_image = self._resize_image_with_aspect_ratio(placeholder_img, (target_w, target_h))
            self.set_status(f"Calculation complete: No valid data found for {index_type}.")
        else:
            # ZMIANA: Użycie funkcji z modułu visualizer
            heatmap = visualizer.create_heatmap_image(self.controller.index_result, self.controller.result_mask, index_type)
            display_image = self._resize_image_with_aspect_ratio(heatmap, (target_w, target_h))
            self.set_status(f"{index_type} visualization complete!")
        
        self.result_photo = ImageTk.PhotoImage(display_image)
        self.result_image_label.configure(image=self.result_photo)
        
        legend_width = self.result_image_label.winfo_width()
        if legend_width > 10:
            # ZMIANA: Użycie funkcji z modułu visualizer
            self.legend_photo = visualizer.create_legend_image(index_type, width=legend_width)
            self.legend_label.configure(image=self.legend_photo)

    # ZMIANA: Usunięto metody create_heatmap i create_legend. Logika jest teraz w visualizer.py

    def set_status(self, message: str):
        self.status_var.set(message)

    def set_fetch_button_state(self, is_enabled: bool):
        state = "normal" if is_enabled else "disabled"
        self.fetch_button.config(state=state)

    def set_calc_buttons_state(self, is_enabled: bool):
        state = "normal" if is_enabled else "disabled"
        self.ndvi_button.config(state=state)
        self.ndmi_button.config(state=state)

    def set_all_buttons_state(self, is_enabled: bool):
        self.set_fetch_button_state(is_enabled)
        self.set_calc_buttons_state(is_enabled)

    def update_timer_display(self, elapsed_seconds: float, is_final: bool = False):
        prefix = "Final Time: " if is_final else "Calculation Time: "
        if elapsed_seconds < 1:
            self.timer_var.set(f"{prefix}{elapsed_seconds * 1000:.0f} ms")
        else:
            self.timer_var.set(f"{prefix}{elapsed_seconds:.3f} s")