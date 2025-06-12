import tkinter as tk
from tkinter import ttk
from multiprocessing import freeze_support

from sentinelhub import SHConfig
from src.core.data_loader.data_loader import SentinelDataLoader
from src.gui.controllers.view_controller import ViewController
from src.gui.controllers.map_controller import MapController
from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView
from src.gui.controllers.test_controller import TestController

class MainApplication(ttk.Frame):
    """
    The main application frame, acting as a "Composition Root".
    """

    def __init__(self, root: tk.Tk):
        super().__init__(root, padding="10")
        self.root = root
        self.root.title("Sentinel Hub Processor")
        self.root.geometry("1600x900")
        self._center_window()

        self.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.sh_config: SHConfig | None = None
        self.data_loader: SentinelDataLoader | None = None
        self.last_map_position = (52.237, 21.017)
        self.last_map_zoom = 8

        self.view_controller = ViewController(self)
        self.map_controller = MapController(self, self.view_controller)
        self.test_controller = TestController(self)

        self.view_controller.switch_to(LoginView)

    def _center_window(self):
        self.root.update_idletasks()
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        win_w, win_h = self.root.winfo_width(), self.root.winfo_height()
        x, y = (screen_w - win_w) // 2, (screen_h - win_h) // 2
        self.root.geometry(f"+{x}+{y}")

    def on_login_success(self, config: SHConfig):
        print("App: Login successful. Initializing core components.")
        self.sh_config = config
        self.data_loader = SentinelDataLoader(config=self.sh_config)
        self.view_controller.switch_to(MapView)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    freeze_support()
    root = tk.Tk()
    app = MainApplication(root)
    app.run()