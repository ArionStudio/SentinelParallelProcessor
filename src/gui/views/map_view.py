import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Callable

from tkintermapview import TkinterMapView
from tkintermapview.utility_functions import osm_to_decimal
from tkcalendar import DateEntry
# --- ### ZMIANA ###: Wracamy do pyproj, bo jest niezawodny ---
from pyproj import Geod

if TYPE_CHECKING:
    from src.gui.app import MainApplication


class Tooltip:
    # ... (klasa Tooltip bez zmian) ...
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
    # --- ### ZMIANA ###: Definiujemy margines bezpieczeństwa (10%) ---
    VALIDATION_SAFETY_MARGIN = 1.10

    def __init__(
        self, controller: "MainApplication", on_fetch_callback: Callable, on_preview_callback: Callable, **kwargs
    ):
        super().__init__(controller, padding=10, **kwargs)
        self.controller = controller
        self.on_fetch_callback = on_fetch_callback
        self.on_preview_callback = on_preview_callback
        self._setup_ui()

    def _setup_ui(self):
        # ... (reszta _setup_ui bez zmian) ...
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        instruction_label = ttk.Label(self, text="Pan and zoom the map, select a date range, then click an action button.", font=("TkDefaultFont", 10, "italic"))
        instruction_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.map_widget = TkinterMapView(self, corner_radius=0)
        self.map_widget.set_position(52.237, 21.017)
        self.map_widget.set_zoom(6)
        self.map_widget.grid(row=1, column=0, sticky="nsew")
        date_frame = ttk.LabelFrame(self, text="Date Range", padding=10)
        date_frame.grid(row=2, column=0, pady=10, sticky="ew")
        info_button = ttk.Button(date_frame, text="?", width=2, command=self._show_date_range_info)
        info_button.grid(row=0, column=4, padx=(20, 0), sticky="e")
        Tooltip(info_button, "Click to learn why a date range is used.")
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.start_date_entry = DateEntry(date_frame, date_pattern="yyyy-mm-dd", year=2025, month=5, day=1)
        self.start_date_entry.grid(row=0, column=1, padx=(0, 20))
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=(0, 5), sticky="w")
        self.end_date_entry = DateEntry(date_frame, date_pattern="yyyy-mm-dd", year=2025, month=6, day=11)
        self.end_date_entry.grid(row=0, column=3)
        explanation_label = ttk.Label(date_frame, text="The app will find the best quality (least cloudy) image within this period.", font=("TkDefaultFont", 9, "italic"), foreground="gray")
        explanation_label.grid(row=1, column=0, columnspan=5, pady=(10, 0), sticky="w")
        action_frame = ttk.Frame(self)
        action_frame.grid(row=3, column=0, pady=(0, 10))
        self.fetch_button = ttk.Button(action_frame, text="Fetch & Save Data", command=self._on_fetch_button_click)
        self.fetch_button.pack(side="left", padx=5)
        self.preview_button = ttk.Button(action_frame, text="Show Preview", command=self._on_preview_button_click)
        self.preview_button.pack(side="left", padx=5)
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    def _validate_resolution(self, top_left, bottom_right, image_size) -> tuple[bool, float]:
        """
        --- ### ZMIANA ###: Ulepszona i niezawodna walidacja z pyproj ---
        Calculates resolution at the center of the BBox and applies a safety margin.
        """
        nw_lat, nw_lon = top_left
        se_lat, se_lon = bottom_right
        width_px, _ = image_size

        if width_px == 0:
            return False, float('inf')

        # Oblicz środek szerokości geograficznej dla dokładniejszego pomiaru
        center_lat = (nw_lat + se_lat) / 2

        geod = Geod(ellps="WGS84")
        # Oblicz szerokość geograficzną na środku bounding boxa
        _, _, distance_meters = geod.inv(nw_lon, center_lat, se_lon, center_lat)

        calculated_mpp = distance_meters / width_px
        # Zastosuj margines bezpieczeństwa, aby być bardziej pesymistycznym niż API
        effective_mpp = calculated_mpp * self.VALIDATION_SAFETY_MARGIN

        print("-" * 20)
        print("[DEBUG] Walidacja rozdzielczości (metoda pyproj + margines)...")
        print(f"[DEBUG] Obliczona rozdzielczość: {calculated_mpp:.2f} m/piksel")
        print(f"[DEBUG] Rozdzielczość z marginesem bezpieczeństwa: {effective_mpp:.2f} m/piksel")

        is_valid = effective_mpp <= self.API_RESOLUTION_LIMIT_METERS
        return is_valid, effective_mpp

    # ... (reszta pliku, w tym _on_fetch_button_click, _get_precise_view_data, etc. bez zmian) ...
    def _validate_and_get_data(self):
        top_left, bottom_right, image_size = self._get_precise_view_data()
        is_valid, mpp = self._validate_resolution(top_left, bottom_right, image_size)
        if not is_valid:
            messagebox.showwarning("Zoom Level Too Low", f"The current map area is too large.\n\n" f"Estimated resolution: {mpp:.2f} m/pixel\n" f"API limit: {self.API_RESOLUTION_LIMIT_METERS:.2f} m/pixel\n\n" f"Please zoom in and try again.", parent=self)
            self.set_status("Validation failed: Map area too large.")
            return None
        start_date = self.start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date_entry.get_date().strftime("%Y-%m-%d")
        time_interval = (start_date, end_date)
        return top_left, bottom_right, image_size, time_interval
    def _on_fetch_button_click(self):
        data = self._validate_and_get_data()
        if data:
            top_left, bottom_right, image_size, time_interval = data
            self.on_fetch_callback(top_left, bottom_right, image_size, time_interval)
    def _on_preview_button_click(self):
        data = self._validate_and_get_data()
        if data:
            top_left, bottom_right, image_size, time_interval = data
            self.on_preview_callback(top_left, bottom_right, image_size, time_interval)
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
        return top_left, bottom_right, image_size
    def set_status(self, message: str):
        self.status_var.set(message)
    def set_button_state(self, is_enabled: bool):
        state = "!disabled" if is_enabled else "disabled"
        self.fetch_button.state([state])
        self.preview_button.state([state])
    def _show_date_range_info(self):
        title = "Why Select a Date Range?"
        message = ("Instead of a single day, you select a period. Here's why:\n\n"
                   "1.  **Avoids Clouds:** The application automatically finds the image with the least cloud cover within your selected range.\n\n"
                   "2.  **Ensures Data Availability:** Satellites don't scan every location daily. A range guarantees you'll find data if the satellite passed over during that time.\n\n"
                   "A wider range increases the chance of getting a perfect, cloud-free image.")
        messagebox.showinfo(title, message, parent=self)