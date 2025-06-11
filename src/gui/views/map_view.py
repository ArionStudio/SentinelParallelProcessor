import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Callable

from tkintermapview import TkinterMapView
from tkintermapview.utility_functions import osm_to_decimal
from tkcalendar import DateEntry

if TYPE_CHECKING:
    from src.gui.app import MainApplication


# --- ### ZMIANA ###: Dodajemy klasę pomocniczą do tworzenia tooltipów ---
class Tooltip:
    """
    Creates a tooltip for a given widget.
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Display the tooltip window."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tip_window,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        """Destroy the tooltip window."""
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


# --- Koniec zmiany ---


class MapView(ttk.Frame):
    """
    A "thin" view that displays a map and date selectors. It informs the
    user about the date range selection and delegates actions to a controller.
    """

    def __init__(
        self, controller: "MainApplication", on_fetch_callback: Callable, **kwargs
    ):
        super().__init__(controller, padding=10, **kwargs)
        self.controller = controller
        self.on_fetch_callback = on_fetch_callback
        self._setup_ui()

    def _setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        instruction_label = ttk.Label(
            self,
            text="Pan and zoom the map, select a date range, then click 'Fetch & Save Data'.",
            font=("TkDefaultFont", 10, "italic"),
        )
        instruction_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.map_widget = TkinterMapView(self, corner_radius=0)
        self.map_widget.set_position(52.237, 21.017)
        self.map_widget.set_zoom(6)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        date_frame = ttk.LabelFrame(self, text="Date Range", padding=10)
        date_frame.grid(row=2, column=0, pady=10, sticky="ew")

        info_button = ttk.Button(
            date_frame,
            text="?",
            width=2,
            command=self._show_date_range_info,
            # --- ### ZMIANA ###: Usunięto nieprawidłowy argument 'tooltip' ---
        )
        info_button.grid(row=0, column=4, padx=(20, 0), sticky="e")
        # --- ### ZMIANA ###: Tworzymy tooltip przy użyciu naszej nowej klasy ---
        Tooltip(info_button, "Click to learn why a date range is used.")
        # --- Koniec zmiany ---

        ttk.Label(date_frame, text="Start Date:").grid(
            row=0, column=0, padx=(0, 5), sticky="w"
        )
        self.start_date_entry = DateEntry(
            date_frame, date_pattern="yyyy-mm-dd", year=2025, month=5, day=1
        )
        self.start_date_entry.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(date_frame, text="End Date:").grid(
            row=0, column=2, padx=(0, 5), sticky="w"
        )
        self.end_date_entry = DateEntry(
            date_frame, date_pattern="yyyy-mm-dd", year=2025, month=6, day=11
        )
        self.end_date_entry.grid(row=0, column=3)

        explanation_label = ttk.Label(
            date_frame,
            text="The app will find the best quality (least cloudy) image within this period.",
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray",
        )
        explanation_label.grid(
            row=1, column=0, columnspan=5, pady=(10, 0), sticky="w"
        )

        self.fetch_button = ttk.Button(
            self,
            text="Fetch & Save Data for This View",
            command=self._on_fetch_button_click,
        )
        self.fetch_button.grid(row=3, column=0, pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    def _get_precise_view_data(self) -> tuple:
        upper_left_tile = self.map_widget.upper_left_tile_pos
        lower_right_tile = self.map_widget.lower_right_tile_pos
        zoom = self.map_widget.zoom

        nw_lat, nw_lon = osm_to_decimal(
            upper_left_tile[0], upper_left_tile[1], zoom
        )
        se_lat, se_lon = osm_to_decimal(
            lower_right_tile[0], lower_right_tile[1], zoom
        )

        top_left = (nw_lat, nw_lon)
        bottom_right = (se_lat, se_lon)
        image_size = (
            self.map_widget.winfo_width(),
            self.map_widget.winfo_height(),
        )

        return top_left, bottom_right, image_size

    def _on_fetch_button_click(self):
        top_left, bottom_right, image_size = self._get_precise_view_data()
        start_date = self.start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date_entry.get_date().strftime("%Y-%m-%d")
        time_interval = (start_date, end_date)
        self.on_fetch_callback(top_left, bottom_right, image_size, time_interval)

    def set_status(self, message: str):
        self.status_var.set(message)

    def set_button_state(self, is_enabled: bool):
        state = "!disabled" if is_enabled else "disabled"
        self.fetch_button.state([state])

    def _show_date_range_info(self):
        title = "Why Select a Date Range?"
        message = (
            "Instead of a single day, you select a period. Here's why:\n\n"
            "1.  **Avoids Clouds:** The application automatically finds the image with the least cloud cover within your selected range.\n\n"
            "2.  **Ensures Data Availability:** Satellites don't scan every location daily. A range guarantees you'll find data if the satellite passed over during that time.\n\n"
            "A wider range increases the chance of getting a perfect, cloud-free image."
        )
        messagebox.showinfo(title, message, parent=self)