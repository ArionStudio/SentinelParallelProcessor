import threading
import os
import hashlib
import time
from tkinter import messagebox
from typing import TYPE_CHECKING

from src.core.io.data_writer import save_bands_to_geotiff
from src.core.io.data_reader import read_geotiff_bands
from src.core.processing.index_calculator import calculate_index

if TYPE_CHECKING:
    from src.gui.app import MainApplication
    from src.gui.views.map_view import MapView

class MapController:
    CACHE_DIR = "data"

    def __init__(self, app: "MainApplication", view_controller):
        self.app = app
        self.view_controller = view_controller
        self.view: "MapView" | None = None
        self.raw_data = None
        self.index_result = None
        self.result_mask = None
        self.last_calculated_index = None
        self.timer_running = False
        self.start_time = 0.0
        self.timer_after_id = None
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def set_view(self, view: "MapView"):
        self.view = view

    def handle_fetch_data(self):
        if not self.view: return
        
        data = self.view.get_view_parameters()
        if not data: return

        top_left, bottom_right, image_size, time_interval, zoom = data
        
        self.view.set_fetch_button_state(False)
        self.view.set_calc_buttons_state(False)
        self.view.set_status("Rozpoczynam ładowanie danych...")
        
        thread = threading.Thread(
            target=self._data_loader_worker,
            args=(top_left, bottom_right, image_size, time_interval, zoom),
            daemon=True
        )
        thread.start()

    def handle_calculate_index(self, index_type: str):
        if not self.raw_data:
            self.view.set_status("Błąd: Brak danych do obliczeń.")
            return
        
        self.view.set_status(f"Obliczanie {index_type}...")
        self.view.set_all_buttons_state(False)
        self._start_timer()
        
        thread = threading.Thread(target=self._calculation_worker, args=(index_type,), daemon=True)
        thread.start()

    def _data_loader_worker(self, top_left, bottom_right, image_size, time_interval, zoom):
        try:
            precision = self._get_precision_for_zoom(zoom)
            north_lat, west_lng = top_left
            south_lat, east_lng = bottom_right
            bbox = self._round_bbox((west_lng, south_lat, east_lng, north_lat), precision)
            
            cache_path = self._generate_cache_path(bbox, image_size, time_interval, zoom)

            if os.path.exists(cache_path):
                self.app.after(0, self.view.set_status, "Cache hit! Ładowanie danych z dysku...")
                self.raw_data = read_geotiff_bands(cache_path)
            else:
                self.app.after(0, self.view.set_status, "Cache miss. Pobieranie danych z API...")
                fetched_data = self.app.data_loader.fetch_data(bbox, image_size, time_interval)
                if not fetched_data: raise Exception("Nie udało się pobrać danych.")
                self.app.after(0, self.view.set_status, "Zapisywanie danych w cache...")
                save_bands_to_geotiff(fetched_data, bbox, cache_path)
                self.raw_data = fetched_data
            
            self.app.after(0, self.view.set_status, "Dane załadowane. Gotowy do obliczeń.")
            self.app.after(0, self.view.set_calc_buttons_state, True)
        except Exception as e:
            self.app.after(0, self.view.set_status, f"Błąd podczas ładowania danych: {e}")
        finally:
            self.app.after(0, self.view.set_fetch_button_state, True) # Zawsze odblokuj fetch

    def _calculation_worker(self, index_type: str):
        try:
            self.last_calculated_index = index_type
            self.index_result, self.result_mask = calculate_index(self.raw_data, index_type)
            self.app.after(0, self.view.display_result, index_type)
        except Exception as e:
            # ZMIANA: Wyświetlaj błędy w okienku dialogowym, a nie tylko w statusie
            error_message = f"An error occurred during calculation:\n\n{type(e).__name__}: {e}"
            print(f"ERROR in calculation worker: {error_message}") # Zostawiamy też w konsoli
            self.app.after(0, lambda: messagebox.showerror("Calculation Error", error_message))
            self.app.after(0, self.view.set_status, "Calculation failed. See error details.")
        finally:
            self._stop_timer()
            self.app.after(0, self.view.set_all_buttons_state, True)

    def _get_precision_for_zoom(self, zoom: int) -> int:
        if zoom <= 6: return 2
        if zoom <= 10: return 3
        if zoom <= 14: return 4
        return 5

    def _round_bbox(self, bbox: tuple, precision: int) -> tuple:
        return tuple(round(coord, precision) for coord in bbox)

    def _generate_cache_path(self, bbox: tuple, image_size: tuple, time_interval: tuple, zoom: int) -> str:
        request_string = f"{bbox}-{image_size}-{time_interval}-{zoom}"
        request_hash = hashlib.md5(request_string.encode()).hexdigest()
        return os.path.join(self.CACHE_DIR, f"{request_hash}.tif")

    def _start_timer(self):
        self.start_time = time.perf_counter()
        self.timer_running = True
        self._update_timer()

    def _update_timer(self):
        if not self.timer_running: return
        elapsed = time.perf_counter() - self.start_time
        if self.view and self.view.winfo_exists():
            self.app.after(0, self.view.update_timer_display, elapsed)
            self.timer_after_id = self.app.after(100, self._update_timer)

    def _stop_timer(self):
        self.timer_running = False
        if self.timer_after_id:
            self.app.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        elapsed = time.perf_counter() - self.start_time
        if self.view and self.view.winfo_exists():
            self.app.after(0, lambda: self.view.update_timer_display(elapsed, is_final=True))