import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import os
import tempfile

from src.core.export.image_server import save_geotiff
from src.core.processing.index_calculator import process_ndvi_parallel, process_ndmi_parallel
import rasterio


class LocalProcessingView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.grid_columnconfigure(0, weight=1)
        self._setup_ui()

    def _setup_ui(self):
        self.label = ttk.Label(self, text="Przetwarzanie lokalne danych GeoTIFF")
        self.label.grid(row=0, column=0, pady=10)

        self.select_button = ttk.Button(self, text="Wybierz plik NDVI (RED+NIR)", command=self._select_file)
        self.select_button.grid(row=1, column=0, pady=10)

        self.ndvi_button = ttk.Button(self, text="Oblicz NDVI", command=self._process_ndvi)
        self.ndvi_button.grid(row=2, column=0, pady=10)

        self.ndmi_button = ttk.Button(self, text="Oblicz NDMI", command=self._process_ndmi)
        self.ndmi_button.grid(row=3, column=0, pady=10)

        self.save_button = ttk.Button(self, text="Zapisz wynik", command=self._save_result)
        self.save_button.grid(row=4, column=0, pady=10)

        self.image_label = ttk.Label(self)
        self.image_label.grid(row=5, column=0, pady=10)

        self.input_path = ""
        self.temp_output = ""
        self.result = None
        self.profile = None

    def _select_file(self):
        self.input_path = filedialog.askopenfilename(title="Wybierz plik GeoTIFF (RED+NIR)")
        if not self.input_path:
            messagebox.showerror("Błąd", "Nie wybrano pliku.")
        else:
            messagebox.showinfo("OK", f"Wybrano plik: {os.path.basename(self.input_path)}")

    def _process_ndvi(self):
        self._run_processing(process_ndvi_parallel)

    def _process_ndmi(self):
        self._run_processing(process_ndmi_parallel)

    def _run_processing(self, func):
        try:
            _, self.temp_output = tempfile.mkstemp(suffix=".tif")
            func(self.input_path, self.temp_output)
            with rasterio.open(self.temp_output) as src:
                self.result = src.read(1)
                self.profile = src.profile
            self._show_result(self.result)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się przetworzyć danych: {e}")

    def _show_result(self, data: np.ndarray):
        norm = (data - np.min(data)) / (np.max(data) - np.min(data))
        image = Image.fromarray((norm * 255).astype(np.uint8)).resize((256, 256))
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo

    def _save_result(self):
        if self.result is None:
            messagebox.showwarning("Brak danych", "Najpierw oblicz indeks.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".tif", filetypes=[("GeoTIFF", "*.tif")])
        if filepath:
            save_geotiff(filepath, self.result, self.profile)
            messagebox.showinfo("Zapisano", f"Zapisano do {filepath}")
