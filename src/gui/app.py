import tkinter as tk
from tkinter import ttk
from typing import Type, Dict, Any, TYPE_CHECKING

# --- Core Component Imports ---
# We import the client for type hinting purposes.
from src.core.auth.api_auth import SentinelHubClient

# --- GUI View Imports ---
from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView
from src.gui.views.api_processing_view import ApiProcessingView

# Use TYPE_CHECKING to avoid circular import errors at runtime,
# while still allowing type checkers (like mypy) to work.
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

        # Configure the root window to make the MainApplication frame expand
        self.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- State Management ---
        # The controller owns the shared state, like the authenticated client.
        self.api_client: SentinelHubClient | None = None

        # --- View Management ---
        self.views: Dict[Type[ttk.Frame], ttk.Frame] = {}
        self._current_view: ttk.Frame | None = None

        # Start the application by showing the login view
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
            # Create the view, passing 'self' as the controller.
            # This is how views get a reference back to MainApplication.
            view = view_class(self, **kwargs)
            self.views[view_class] = view

        # Place the new view in the grid and make it expand
        view.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._current_view = view

    # --- Callback Methods (The "Controller" Logic) ---

    def on_login_success(self, api_client: SentinelHubClient):
        """
        Callback for when login is successful. Stores the authenticated
        client and switches to the MapView.

        Args:
            api_client: The fully authenticated SentinelHubClient instance.
        """
        print("Controller: Login successful. Storing API client.")
        self.api_client = api_client  # Store the shared state
        self._switch_view(MapView)

    def on_bbox_selected(self, bbox: tuple):
        """
        Callback for when a BBOX is selected on the map. Switches to the
        ApiProcessingView, passing it the required data.
        """
        print(f"Controller: BBOX selected {bbox}. Switching to Processing View.")
        if not self.api_client:
            print("Error: API client not available. Returning to login.")
            self._switch_view(LoginView)
            return

        # Pass the required state (api_client and bbox) to the new view
        self._switch_view(
            ApiProcessingView, bbox=bbox, api_client=self.api_client
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
    # Ensure your other view classes (MapView, ApiProcessingView) are
    # updated to accept `controller` as their first argument.
    root = tk.Tk()
    app = MainApplication(root)
    app.run()