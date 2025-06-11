import tkinter as tk
from tkinter import ttk

from sentinelhub import SHConfig
from src.core.data_loader.data_loader import SentinelDataLoader
from src.gui.controllers.view_controller import ViewController
from src.gui.controllers.map_controller import MapController
from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView

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

        self.sh_config: SHConfig | None = None
        self.data_loader: SentinelDataLoader | None = None

        # --- ### ZMIANA ###: Inicjalizacja kontrolerów i przekazanie zależności ---
        self.view_controller = ViewController(self)
        self.map_controller = MapController(self, self.view_controller)
        # --- Koniec zmiany ---

        self.view_controller.switch_to(LoginView)

    def _center_window(self):
        self.root.update_idletasks()
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        win_w, win_h = self.root.winfo_width(), self.root.winfo_height()
        x, y = (screen_w - win_w) // 2, (screen_h - win_h) // 2
        self.root.geometry(f"+{x}+{y}")

    def on_login_success(self, config: SHConfig):
        """Callback for successful login."""
        print("App: Login successful. Initializing core components.")
        self.sh_config = config
        self.data_loader = SentinelDataLoader(config=self.sh_config)
        self.view_controller.switch_to(MapView)

    # --- ### ZMIANA ###: Usunięto metodę handle_show_preview. Już tu nie należy. ---

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