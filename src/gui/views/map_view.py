import tkinter as tk
from tkinter import ttk
import threading
from typing import TYPE_CHECKING
from tkintermapview.utility_functions import osm_to_decimal

# Use tkintermapview for the interactive map widget
from tkintermapview import TkinterMapView

# Use TYPE_CHECKING to avoid circular import errors at runtime
if TYPE_CHECKING:
    from src.gui.app import MainApplication
    from src.core.data_loader.data_loader import SentinelDataLoader


class MapView(ttk.Frame):
    """
    A view that displays an interactive map. A button allows the user to
    fetch band data for the current map viewport and print the results
    to the console.
    """

    def __init__(
        self,
        controller: "MainApplication",
        data_loader: "SentinelDataLoader",
        **kwargs,
    ):
        super().__init__(controller, padding=10, **kwargs)
        self.controller = controller
        self.data_loader = data_loader

        self._setup_ui()

    def _setup_ui(self):
        """Creates and arranges the widgets for this view."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        instruction_label = ttk.Label(
            self,
            text="Pan and zoom the map, then click 'Fetch Data' to get band info for the current view.",
            font=("TkDefaultFont", 10, "italic"),
        )
        instruction_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.map_widget = TkinterMapView(self, corner_radius=0)
        self.map_widget.set_position(52.237, 21.017)
        self.map_widget.set_zoom(6)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        fetch_button = ttk.Button(
            self, text="Fetch Data for This View", command=self._start_fetch_thread
        )
        fetch_button.grid(row=2, column=0, pady=10)

        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        self.get_bounding_box()

    def _start_fetch_thread(self):
        """Starts the data fetching process in a separate thread."""
        for child in self.winfo_children():
            if isinstance(child, ttk.Button):
                child.state(["disabled"])

        self.status_var.set("Starting data fetch...")
        thread = threading.Thread(target=self._fetch_and_print_data, daemon=True)
        thread.start()

    def get_bounding_box(self):
        """
        Gets the bounding box (corners) of the current map view using internal state.
        """
        upper_left_tile_pos = self.map_widget.upper_left_tile_pos
        lower_right_tile_pos = self.map_widget.lower_right_tile_pos
        zoom = round(self.map_widget.zoom)

        nw_lat, nw_lon = osm_to_decimal(
            upper_left_tile_pos[0], upper_left_tile_pos[1], zoom
        )
        ne_lat, ne_lon = osm_to_decimal(
            lower_right_tile_pos[0], upper_left_tile_pos[1], zoom
        )
        se_lat, se_lon = osm_to_decimal(
            lower_right_tile_pos[0], lower_right_tile_pos[1], zoom
        )
        sw_lat, sw_lon = osm_to_decimal(
            upper_left_tile_pos[0], lower_right_tile_pos[1], zoom
        )

        corners = {
            "nw": (nw_lat, nw_lon),
            "ne": (ne_lat, ne_lon),
            "se": (se_lat, se_lon),
            "sw": (sw_lat, sw_lon),
        }

        print(f"Bounding Box Corners: {corners}")

        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "Bounding Box",
            f"NW: {corners['nw']}\n"
            f"NE: {corners['ne']}\n"
            f"SE: {corners['se']}\n"
            f"SW: {corners['sw']}"
        )

        return corners

    def _fetch_and_print_data(self):
        """This function runs in a background thread."""
        try:
            # --- FIX #1: Use the correct method: get_current_view_corners() ---
            # It returns a nested tuple: ((north_lat, west_lng), (south_lat, east_lng))
            top_left, bottom_right = self.map_widget.get_current_view_corners()

            # --- FIX #2: Unpack the nested tuple to get the coordinates ---
            north_lat, west_lng = top_left
            south_lat, east_lng = bottom_right

            # --- FIX #3: Construct the BBOX in the correct order for Sentinel Hub ---
            # Sentinel Hub expects: (min_lon, min_lat, max_lon, max_lat)
            bbox_coords = (west_lng, south_lat, east_lng, north_lat)

            image_size = (
                self.map_widget.winfo_width(),
                self.map_widget.winfo_height(),
            )

            self.status_var.set(f"Requesting data for BBOX: {bbox_coords}...")
            bands = self.data_loader.fetch_bands(bbox_coords, image_size)

            print("\n" + "=" * 50)
            if bands:
                self.status_var.set("Success! Data info printed to console.")
                print("✅ API Call Successful. Received Band Data:")
                for band_name, data_array in bands.items():
                    print(
                        f"  - Band '{band_name}': "
                        f"Shape={data_array.shape}, "
                        f"DataType={data_array.dtype}"
                    )
            else:
                self.status_var.set("Error: Failed to fetch data. See console.")
                print("❌ API Call Failed. No data received.")
            print("=" * 50 + "\n")

        except Exception as e:
            self.status_var.set("An error occurred. See console for details.")
            print(f"An unexpected error occurred in the worker thread: {e}")
        finally:
            self.after(0, self._enable_button)

    def _enable_button(self):
        """Re-enables the fetch button. Must be run in the main thread."""
        for child in self.winfo_children():
            if isinstance(child, ttk.Button):
                child.state(["!disabled"])