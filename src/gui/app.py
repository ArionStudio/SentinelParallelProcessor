import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.gui.views.login_view import LoginView
from src.gui.views.map_view import MapView
from src.gui.views.api_processing_view import ApiProcessingView  # Dodaj ten widok

class MainApplication(ttk.Frame):
    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self.root = root
        self.root.title("Sentinel Hub Processor")
        
        # Configure main window
        self.root.geometry("800x600")
        self._center_window()
        
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.show_login_view()

    def _center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")

    def show_login_view(self):
        self.login_view = LoginView(
            self.main_frame,
            on_login_success=self.on_login_success
        )
        self.login_view.grid(row=0, column=0, sticky="nsew")

    def on_login_success(self):
        """Po zalogowaniu pokaż mapę i obsłuż wybór BBOX"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        def handle_bbox_selected(bbox):
            print("Wybrany BBOX:", bbox)
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            self.api_view = ApiProcessingView(self.main_frame, bbox=bbox)
            self.api_view.grid(row=0, column=0, sticky="nsew")

        self.map_view = MapView(self.main_frame, on_bbox_selected=handle_bbox_selected)
        self.map_view.grid(row=0, column=0, sticky="nsew")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    app.run()
