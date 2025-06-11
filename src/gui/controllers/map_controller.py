import threading
import os  # <<< NOWY IMPORT
import hashlib  # <<< NOWY IMPORT
from tkinter import messagebox
from typing import TYPE_CHECKING, Tuple

from src.core.io.data_writer import save_bands_to_geotiff
from src.gui.views.api_processing_view import ApiProcessingView

if TYPE_CHECKING:
    from src.gui.app import MainApplication
    from src.gui.views.map_view import MapView
    from src.gui.controllers.view_controller import ViewController


class MapController:
    CACHE_DIR = "data"  # Definiujemy katalog na cache

    def __init__(self, app: "MainApplication", view_controller: "ViewController"):
        self.app = app
        self.view_controller = view_controller
        self.view: "MapView" | None = None
        # Upewnij się, że katalog cache istnieje
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def set_view(self, view: "MapView"):
        self.view = view

    def _generate_cache_path(
        self, bbox: tuple, image_size: tuple, time_interval: tuple
    ) -> str:
        """Generates a unique filename based on request parameters."""
        # Stwórz unikalny ciąg znaków dla zapytania
        request_string = f"{bbox}-{image_size}-{time_interval}"
        # Użyj hasha MD5 do stworzenia krótkiego i unikalnego identyfikatora
        request_hash = hashlib.md5(request_string.encode()).hexdigest()
        filename = f"{request_hash}.tif"
        return os.path.join(self.CACHE_DIR, filename)

    def handle_fetch_and_save(
        self,
        top_left: tuple,
        bottom_right: tuple,
        image_size: tuple,
        time_interval: Tuple[str, str],
    ):
        """
        Handles the 'Load/Cache Data' action. Checks cache first, then fetches.
        """
        if not self.view:
            return

        north_lat, west_lng = top_left
        south_lat, east_lng = bottom_right
        bbox_coords = (west_lng, south_lat, east_lng, north_lat)

        cache_path = self._generate_cache_path(
            bbox_coords, image_size, time_interval
        )

        # --- ### ZMIANA ###: Logika sprawdzania cache'u ---
        if os.path.exists(cache_path):
            print(f"Cache hit! Loading data from {cache_path}")
            self.view.set_status(f"Data loaded from cache: {os.path.basename(cache_path)}")
            # Tutaj w przyszłości można dodać logikę wczytania pliku i jego przetworzenia
            messagebox.showinfo("Cache Hit", f"Data for this exact request already exists and was loaded from cache:\n\n{cache_path}")
            return
        # --- Koniec zmiany ---

        print(f"Cache miss. Fetching data from API. Will save to {cache_path}")
        self.view.set_button_state(is_enabled=False)
        self.view.set_status("Cache miss. Fetching data from API...")

        thread = threading.Thread(
            target=self._worker_fetch_and_save,
            args=(
                bbox_coords,
                image_size,
                time_interval,
                cache_path,  # Przekaż ścieżkę do zapisu w cache
            ),
            daemon=True,
        )
        thread.start()

    def handle_show_preview(
        self, top_left: tuple, bottom_right: tuple, image_size: tuple, time_interval: Tuple[str, str]
    ):
        # ... (bez zmian) ...
        print("MapController: Preview requested. Switching view.")
        north_lat, west_lng = top_left
        south_lat, east_lng = bottom_right
        bbox_coords = (west_lng, south_lat, east_lng, north_lat)
        self.view_controller.switch_to(ApiProcessingView, bbox=bbox_coords, image_size=image_size, time_interval=time_interval)

    def _worker_fetch_and_save(
        self, bbox_coords: tuple, image_size: tuple, time_interval: Tuple[str, str], output_path: str
    ):
        # ... (logika wątku pozostaje bardzo podobna, tylko nazwa argumentu się zmienia) ...
        try:
            if not self.app.data_loader: raise Exception("DataLoader not initialized.")
            self.app.after(0, self.view.set_status, "Requesting data...")
            bands = self.app.data_loader.fetch_bands(bbox_coords, image_size, time_interval=time_interval)
            if not bands: raise Exception("API call failed. No data received.")
            self.app.after(0, self.view.set_status, "Data received. Saving to cache...")
            save_bands_to_geotiff(bands, bbox_coords, output_path)
            self.app.after(0, self.view.set_status, f"Success! Data saved to cache: {os.path.basename(output_path)}")
        except Exception as e:
            # ... (obsługa błędów bez zmian) ...
            error_str = str(e).lower()
            if "exceeds the limit" in error_str and "meters per pixel" in error_str:
                user_message = "Map area is too large. Please zoom in."
                self.app.after(0, lambda: messagebox.showwarning("Zoom Level Too Low", f"{user_message}\n\nThe requested area is too large for the current window size, which exceeds the API's resolution limit."))
                if self.view: self.app.after(0, self.view.set_status, user_message)
            else:
                user_message = "An unexpected error occurred."
                self.app.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred:\n\n{e}"))
                if self.view: self.app.after(0, self.view.set_status, f"{user_message} See console.")
        finally:
            if self.view: self.app.after(0, self.view.set_button_state, True)