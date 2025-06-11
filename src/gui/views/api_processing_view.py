import tkinter as tk
from tkinter import ttk
import threading
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image, ImageTk


if TYPE_CHECKING:
    from src.gui.app import MainApplication


class ApiProcessingView(ttk.Frame):
    """
    A view that shows the progress of a long-running API task and
    displays the result as a preview image.
    """

    def __init__(
        self,
        parent: "MainApplication",
        bbox: tuple,
        image_size: tuple,
        time_interval: tuple,
        **kwargs,
    ):
        super().__init__(parent, padding=20, **kwargs)
        self.app = parent
        self.bbox = bbox
        self.image_size = image_size
        self.time_interval = time_interval

        self._setup_ui()
        self._start_processing_thread()

    def _setup_ui(self):
        """Creates the widgets for the processing view."""
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(
            self, text="Processing Sentinel Hub Data...", font=("TkDefaultFont", 16)
        ).grid(row=0, column=0, pady=10)

        self.status_var = tk.StringVar(value="Initializing...")
        ttk.Label(self, textvariable=self.status_var).grid(
            row=1, column=0, pady=5
        )

        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=10)

        self.image_label = ttk.Label(self)
        self.image_label.grid(row=3, column=0, pady=10)

        self.back_button = ttk.Button(
            self,
            text="Back to Map",
            command=self.app.show_map_view,
            state="disabled",
        )
        self.back_button.grid(row=4, column=0, pady=20)

    def _start_processing_thread(self):
        """Starts the background worker thread for data fetching."""
        self.progress_bar.start()
        thread = threading.Thread(target=self._worker_thread, daemon=True)
        thread.start()

    def _worker_thread(self):
        """The actual work of fetching and processing data."""
        try:
            self.app.after(
                0, self.status_var.set, "Requesting data from API..."
            )

            bands = self.app.data_loader.fetch_bands(
                self.bbox, self.image_size, self.time_interval
            )

            if not bands:
                raise Exception("Failed to fetch data from the API.")

            self.app.after(0, self.status_var.set, "Creating preview image...")
            pil_image = self._create_preview_image(bands)

            self.app.after(0, self._display_result, pil_image)

        except Exception as e:
            self.app.after(
                0, self.status_var.set, f"Error: {e}"
            )
            print(f"Error in ApiProcessingView worker: {e}")
        finally:
            self.app.after(0, self.progress_bar.stop)
            self.app.after(0, self.back_button.config, {"state": "normal"})

    def _create_preview_image(self, bands: dict) -> Image.Image:
        """Creates a false-color composite PIL image from band data."""
        r = bands["B11"]
        g = bands["B08"]
        b = bands["B04"]

        def scale_band(band, max_val=3500):
            scaled = np.clip(band / max_val, 0, 1) * 255
            return scaled.astype(np.uint8)

        rgb_bands = [scale_band(b) for b in (r, g, b)]
        rgb_image_array = np.stack(rgb_bands, axis=-1)

        return Image.fromarray(rgb_image_array)

    def _display_result(self, pil_image: Image.Image):
        """Updates the UI to show the final image."""
        photo = ImageTk.PhotoImage(pil_image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        self.status_var.set("Processing complete!")