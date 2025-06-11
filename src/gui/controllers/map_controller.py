import threading
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Tuple

from src.core.io.data_writer import save_bands_to_geotiff
from src.gui.views.api_processing_view import ApiProcessingView

if TYPE_CHECKING:
    from src.gui.app import MainApplication
    from src.gui.views.map_view import MapView
    from src.gui.controllers.view_controller import ViewController


class MapController:
    """
    Handles ALL business logic related to the MapView, including saving
    data and showing previews.
    """

    def __init__(self, app: "MainApplication", view_controller: "ViewController"):
        self.app = app
        self.view_controller = view_controller
        self.view: "MapView" | None = None

    def set_view(self, view: "MapView"):
        """Connects this controller to its corresponding view."""
        self.view = view

    def handle_fetch_and_save(
        self,
        top_left: tuple,
        bottom_right: tuple,
        image_size: tuple,
        time_interval: Tuple[str, str],
    ):
        """Handles the 'Save to File' action."""
        if not self.view:
            return
        output_path = filedialog.asksaveasfilename(
            title="Save Sentinel Data As",
            filetypes=[("GeoTIFF files", "*.tif *.tiff")],
            defaultextension=".tif",
            initialfile="sentinel_data.tif",
        )
        if not output_path:
            self.view.set_status("Save operation cancelled.")
            return
        self.view.set_button_state(is_enabled=False)
        self.view.set_status("Starting data fetch...")
        thread = threading.Thread(
            target=self._worker_fetch_and_save,
            args=(
                top_left,
                bottom_right,
                image_size,
                time_interval,
                output_path,
            ),
            daemon=True,
        )
        thread.start()

    def handle_show_preview(
        self,
        top_left: tuple,
        bottom_right: tuple,
        image_size: tuple,
        time_interval: Tuple[str, str],
    ):
        """Handles the 'Show Preview' action by switching to the processing view."""
        print("MapController: Preview requested. Switching view.")
        north_lat, west_lng = top_left
        south_lat, east_lng = bottom_right
        bbox_coords = (west_lng, south_lat, east_lng, north_lat)

        self.view_controller.switch_to(
            ApiProcessingView,
            bbox=bbox_coords,
            image_size=image_size,
            time_interval=time_interval,
        )

    def _worker_fetch_and_save(
        self,
        top_left: tuple,
        bottom_right: tuple,
        image_size: tuple,
        time_interval: Tuple[str, str],
        output_path: str,
    ):
        """Worker thread for the 'Save to File' action."""
        try:
            if not self.app.data_loader:
                raise Exception("DataLoader not initialized.")
            north_lat, west_lng = top_left
            south_lat, east_lng = bottom_right
            bbox_coords = (west_lng, south_lat, east_lng, north_lat)
            self.app.after(0, self.view.set_status, "Requesting data...")
            bands = self.app.data_loader.fetch_bands(
                bbox_coords, image_size, time_interval=time_interval
            )
            if not bands:
                raise Exception("API call failed. No data received.")
            self.app.after(0, self.view.set_status, "Data received. Saving...")
            save_bands_to_geotiff(bands, bbox_coords, output_path)
            self.app.after(0, self.view.set_status, "Success! Data saved.")
        except Exception as e:
            error_str = str(e).lower()
            if (
                "exceeds the limit" in error_str
                and "meters per pixel" in error_str
            ):
                user_message = "Map area is too large. Please zoom in."
                self.app.after(
                    0,
                    lambda: messagebox.showwarning(
                        "Zoom Level Too Low",
                        f"{user_message}\n\nThe requested area is too large for the current window size, which exceeds the API's resolution limit.",
                    ),
                )
                if self.view:
                    self.app.after(0, self.view.set_status, user_message)
            else:
                user_message = "An unexpected error occurred."
                self.app.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"An unexpected error occurred:\n\n{e}"
                    ),
                )
                if self.view:
                    self.app.after(
                        0, self.view.set_status, f"{user_message} See console."
                    )
        finally:
            if self.view:
                self.app.after(0, self.view.set_button_state, True)