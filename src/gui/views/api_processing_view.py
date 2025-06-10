import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # <-- dodano simpledialog tutaj
from PIL import Image, ImageTk
import io
import requests

from src.core.sentinel.sentinel_client import SentinelHubClient
from src.core.auth.credentials_manager import CredentialsManager

class ApiProcessingView(ttk.Frame):
    def __init__(self, parent, bbox):
        super().__init__(parent, padding=20)
        self.bbox = bbox
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Pobieranie NDVI z Sentinel Hub...").grid(row=0, column=0, pady=10)

        self.image_label = ttk.Label(self)
        self.image_label.grid(row=1, column=0, pady=10)

        # Start od razu
        self._start_download()

    def _start_download(self):
        try:
            # Wczytaj dane logowania z pliku .enc
            manager = CredentialsManager()
            credentials = manager.load_credentials(password=self._get_password())
            if not credentials:
                raise Exception("Nie znaleziono poprawnych danych logowania.")

            client = SentinelHubClient(
                client_id=credentials.client_id,
                client_secret=credentials.client_secret
            )

            image_data = client.download_ndvi_image(
                bbox=self.bbox,
                time_interval="2023-07-01/2023-07-10",
                width=512,
                height=512
            )

            image = Image.open(io.BytesIO(image_data)).resize((512, 512))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                messagebox.showwarning("Brak danych",
                    "Brak danych Sentinel-2 dla podanego obszaru i daty. Spróbuj innego zakresu.")
            else:
                messagebox.showerror("Błąd serwera",
                    f"Wystąpił błąd HTTP: {e.response.status_code}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać NDVI: {e}")

    def _get_password(self):
        # Prosty prompt do hasła (działa dzięki poprawnemu importowi)
        return simpledialog.askstring("Hasło", "Podaj hasło do odszyfrowania danych:")
