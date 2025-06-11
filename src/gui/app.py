import tkinter as tk
from tkinter import ttk
from typing import Type, Dict, Any, TYPE_CHECKING

# --- Core Component Imports ---
# We now import SHConfig for type hinting and SentinelDataLoader to instantiate it.
from sentinelhub import SHConfig
from src.core.data_loader.data_loader import SentinelDataLoader

# --- GUI View Imports ---
from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView
from src.gui.views.api_processing_view import ApiProcessingView

# Use TYPE_CHECKING to avoid circular import errors at runtime
if TYPE_CHECKING:
    from src.gui.app import MainApplication


class MainApplication(ttk.Frame):
    """
    The main controller for the Tkinter application.
    It manages view switching and shared application state.
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
        # The controller now stores the validated SHConfig object.
        self.sh_config: SHConfig | None = None

        # --- View Management ---
        self.views: Dict[Type[ttk.Frame], ttk.Frame] = {}
        self._current_view: ttk.Frame | None = None

        self._switch_view(LoginView)

    def _center_window(self):
        """Centers the main window on the screen."""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"+{x}+{y}")

    def _switch_view(self, view_class: Type[ttk.Frame], **kwargs: Any):
        """
        Hides the current view and shows the specified view.
        Creates the view instance if it doesn't exist.
        """
        if self._current_view:
            self._current_view.grid_forget()

        view = self.views.get(view_class)
        if view is None:
            view = view_class(self, **kwargs)
            self.views[view_class] = view

        view.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._current_view = view

    # --- Callback Methods (The "Controller" Logic) ---

    def on_login_success(self, config: SHConfig):
        """
        Callback for when login is successful. Stores the validated SHConfig
        object and switches to the MapView.

        Args:
            config: The validated SHConfig instance from SentinelHubAuthenticator.
        """
        print("Controller: Login successful. Storing SHConfig.")
        self.sh_config = config  # Store the validated config

        # Create the data loader instance using the validated config
        data_loader = SentinelDataLoader(config=self.sh_config)

        # Switch to the MapView and pass it the data_loader instance
        self._switch_view(MapView, data_loader=data_loader)

    def on_bbox_selected(self, bbox: tuple):
        """
        Callback for when a BBOX is selected on the map. Creates the data
        loader and switches to the ApiProcessingView.
        """
        print(f"Controller: BBOX selected {bbox}. Switching to Processing View.")
        if not self.sh_config:
            print("Error: SHConfig not available. Returning to login.")
            self._switch_view(LoginView)
            return

        # Create the data loader instance using the stored config
        data_loader = SentinelDataLoader(config=self.sh_config)

        # Pass the BBOX and the ready-to-use data_loader to the view
        self._switch_view(
            ApiProcessingView, bbox=bbox, data_loader=data_loader
        )

    def show_map_view(self):
        """Allows other views to request a switch back to the map."""
        print("Controller: Returning to Map View.")
        self._switch_view(MapView)

    def run(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()


if __name__ == "__main__":
    # This entry point now launches the fully integrated application.
    root = tk.Tk()
    app = MainApplication(root)
    app.run()