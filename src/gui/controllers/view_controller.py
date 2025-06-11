from typing import Type, Any, TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView
from src.gui.views.api_processing_view import ApiProcessingView

if TYPE_CHECKING:
    from src.gui.app import MainApplication


class ViewController:
    """
    Manages the lifecycle of views: creating, switching, and destroying them.
    """

    def __init__(self, app: "MainApplication"):
        self.app = app
        self.views: dict[Type[ttk.Frame], ttk.Frame] = {}
        self._current_view: ttk.Frame | None = None

    def switch_to(self, view_class: Type[ttk.Frame], **kwargs: Any):
        """Hides the current view and shows the specified view."""
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
        """Factory method for creating views and wiring them up."""
        if view_class is LoginView:
            return LoginView(self.app)
        if view_class is MapView:
            map_view = MapView(
                self.app,
                on_fetch_callback=self.app.map_controller.handle_fetch_and_save,
                on_preview_callback=self.app.map_controller.handle_show_preview,
            )
            self.app.map_controller.set_view(map_view)
            return map_view
        if view_class is ApiProcessingView:
            return ApiProcessingView(
                self.app,
                bbox=kwargs.get("bbox"),
                image_size=kwargs.get("image_size"),
                time_interval=kwargs.get("time_interval"),
            )
        raise ValueError(f"Unknown view class: {view_class}")