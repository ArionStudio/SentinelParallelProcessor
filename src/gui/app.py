import tkinter as tk
from tkinter import ttk

from sentinelhub import SHConfig
from src.core.data_loader.data_loader import SentinelDataLoader

# Importuj kontrolery, które będą zarządzać logiką
from src.gui.controllers.view_controller import ViewController
from src.gui.controllers.map_controller import MapController

# Importuj tylko widok startowy
from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView
from src.gui.views.api_processing_view import ApiProcessingView


class MainApplication(ttk.Frame):
    """
    The main application frame, acting as a "Composition Root".
    It initializes controllers and holds shared application state.
    """

    def __init__(self, root: tk.Tk):
        super().__init__(root, padding="10")
        self.root = root
        self.root.title("Sentinel Hub Processor")
        self.root.geometry("1200x800")
        self._center_window()

        self.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- State Management ---
        self.sh_config: SHConfig | None = None
        self.data_loader: SentinelDataLoader | None = None

        # --- Controller Initialization ---
        self.view_controller = ViewController(self)
        self.map_controller = MapController(self)

        # --- Start the application ---
        self.view_controller.switch_to(LoginView)

    def _center_window(self):
        self.root.update_idletasks()
        # ... (reszta kodu bez zmian) ...
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"+{x}+{y}")

    # --- Public API for Controllers and Views ---

    def on_login_success(self, config: SHConfig):
        """Callback for successful login."""
        print("App: Login successful. Initializing core components.")
        self.sh_config = config
        self.data_loader = SentinelDataLoader(config=self.sh_config)
        self.view_controller.switch_to(MapView)

    def on_bbox_selected(self, bbox: tuple):
        """Callback for when a BBOX is selected on the map."""
        print(f"App: BBOX selected {bbox}. Switching to Processing View.")
        if not self.sh_config:
            print("Error: SHConfig not available. Returning to login.")
            self.view_controller.switch_to(LoginView)
            return
        self.view_controller.switch_to(ApiProcessingView, bbox=bbox)

    def show_map_view(self):
        """Allows other views to request a switch back to the map."""
        print("App: Returning to Map View.")
        self.view_controller.switch_to(MapView)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    app.run()