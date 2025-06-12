# scripts/generate_scaled_data.py

import os
import rasterio
import numpy as np
from rasterio.transform import from_bounds
from rasterio.enums import Resampling

# --- Konfiguracja ---
SOURCE_DATA_DIR = "data"
TARGET_DATA_DIR = "test_data/scaled"
# Rozdzielczości (szerokość/wysokość w pikselach) do wygenerowania
TARGET_SIZES = [256, 512, 1024, 2048, 4096] 

def generate_data():
    """
    Tworzy zestaw danych testowych o różnych rozdzielczościach na podstawie
    jednego pliku źródłowego z folderu 'data'.
    """
    print("--- Rozpoczynam generowanie danych testowych o różnej skali ---")

    # 1. Znajdź plik źródłowy
    try:
        source_files = [f for f in os.listdir(SOURCE_DATA_DIR) if f.endswith('.tif')]
        if not source_files:
            print(f"BŁĄD: Nie znaleziono plików .tif w folderze '{SOURCE_DATA_DIR}'.")
            print("Najpierw uruchom aplikację i pobierz dane dla dowolnego obszaru.")
            return
    except FileNotFoundError:
        print(f"BŁĄD: Folder źródłowy '{SOURCE_DATA_DIR}' nie istnieje.")
        print("Najpierw uruchom aplikację i pobierz dane dla dowolnego obszaru.")
        return
    
    source_file_path = os.path.join(SOURCE_DATA_DIR, source_files[0])
    print(f"Używam pliku źródłowego: {source_file_path}")

    # 2. Stwórz folder docelowy
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)
    print(f"Dane wyjściowe zostaną zapisane w: {TARGET_DATA_DIR}")

    # 3. Przetwarzaj i generuj nowe pliki
    with rasterio.open(source_file_path) as src:
        for size in TARGET_SIZES:
            # Docelowy kształt to (liczba_pasm, wysokość, szerokość)
            target_shape = (src.count, size, size)
            output_path = os.path.join(TARGET_DATA_DIR, f"scaled_data_{size}.tif")
            
            print(f"Generowanie pliku {size}x{size}...")
            
            # Odczytaj dane ze zmianą rozmiaru (resampling)
            # Używamy Resampling.bilinear, aby uzyskać gładkie przejścia
            data = src.read(out_shape=target_shape, resampling=Resampling.bilinear)
            
            # Zaktualizuj metadane (profil) dla nowego pliku
            profile = src.profile
            profile.update({
                'height': size,
                'width': size,
                'transform': from_bounds(*src.bounds, width=size, height=size)
            })

            # Zapisz nowy plik GeoTIFF
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(data)
    
    print(f"--- Zakończono generowanie danych testowych w folderze '{TARGET_DATA_DIR}'. ---")

if __name__ == "__main__":
    generate_data()