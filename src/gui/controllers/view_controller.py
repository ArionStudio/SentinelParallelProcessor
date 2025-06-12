from typing import Type, Any, TYPE_CHECKING
from tkinter import ttk

from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView

if TYPE_CHECKING:
    from src.gui.app import MainApplication


class ViewController:
    """
    Manages the lifecycle of views. Now much simpler.
    """

    def __init__(self, app: "MainApplication"):
        self.app = app
        self.views: dict[Type[ttk.Frame], ttk.Frame] = {}
        self._current_view: ttk.Frame | None = None

    def switch_to(self, view_class: Type[ttk.Frame], **kwargs: Any):
        if self._current_view:
            self._current_view.grid_forget()
        view = self._create_view(view_class, **kwargs)
        self.views[view_class] = view
        view.grid(row=0, column=0, sticky="nsew")
        self.app.grid_rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(0, weight=1)
        self._current_view = view

    def _create_view(
        self, view_class: Type[ttk.Frame], **kwargs: Any
    ) -> ttk.Frame:
        """Factory method for creating views."""
        if view_class is LoginView:
            return LoginView(self.app)
        if view_class is MapView:
            # MapView jest teraz jedynym głównym widokiem
            map_view = MapView(
                self.app,
                controller=self.app.map_controller,
                initial_position=self.app.last_map_position,
                initial_zoom=self.app.last_map_zoom,
            )
            self.app.map_controller.set_view(map_view)
            return map_view
        raise ValueError(f"Unknown view class: {view_class}")