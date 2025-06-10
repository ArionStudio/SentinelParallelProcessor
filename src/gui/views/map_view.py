import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView

class MapView(ttk.Frame):
    def __init__(self, parent, on_bbox_selected=None):
        super().__init__(parent, padding=10)
        self.on_bbox_selected = on_bbox_selected

        # Instrukcja
        ttk.Label(self, text="Kliknij dwa razy: lewy górny i prawy dolny róg obszaru").pack(pady=5)

        # Widget mapy
        self.map_widget = TkinterMapView(self, width=600, height=400, corner_radius=0)
        self.map_widget.set_position(52.237, 21.017)  # Warszawa
        self.map_widget.set_zoom(6)
        self.map_widget.pack()

        self.clicks = []
        self.rect_marker = None

        # Obsługa kliknięcia
        self.map_widget.add_right_click_menu_command(label="Wybierz punkt", command=self._handle_click, pass_coords=True)

        # Przycisk zatwierdzenia
        ttk.Button(self, text="Zatwierdź obszar", command=self._confirm_bbox).pack(pady=10)

    def _handle_click(self, coords):
        lat, lon = coords
        self.clicks.append((lat, lon))
        self.map_widget.set_marker(lat, lon)

        if len(self.clicks) == 2:
            # Rysujemy prostokąt
            self._draw_rectangle()

    def _draw_rectangle(self):
        if self.rect_marker:
            self.map_widget.delete(self.rect_marker)

        lat1, lon1 = self.clicks[0]
        lat2, lon2 = self.clicks[1]

        min_lat, max_lat = sorted([lat1, lat2])
        min_lon, max_lon = sorted([lon1, lon2])

        self.rect_marker = self.map_widget.set_path([
            (min_lat, min_lon), (min_lat, max_lon),
            (max_lat, max_lon), (max_lat, min_lon),
            (min_lat, min_lon)
        ])

    def _confirm_bbox(self):
        if len(self.clicks) != 2:
            messagebox.showerror("Błąd", "Musisz kliknąć dwa punkty.")
            return

        lat1, lon1 = self.clicks[0]
        lat2, lon2 = self.clicks[1]

        min_lat, max_lat = sorted([lat1, lat2])
        min_lon, max_lon = sorted([lon1, lon2])

        bbox = [min_lon, min_lat, max_lon, max_lat]

        if self.on_bbox_selected:
            self.on_bbox_selected(bbox)
