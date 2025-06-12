import numpy as np
import taichi as ti
from typing import Dict, Tuple
import sys

# --- Inteligentna inicjalizacja Taichi (bez zmian) ---
print("Wykrywam system operacyjny w celu optymalizacji Taichi...")
if sys.platform == "win32":
    print("System Windows wykryty. Używam backendu DirectX 11 (dx11).")
    ti.init(arch=ti.dx11)
elif sys.platform == "darwin":
    print("System macOS wykryty. Używam backendu Metal.")
    ti.init(arch=ti.metal)
else:
    print(f"System {sys.platform} wykryty. Używam domyślnego backendu GPU.")
    ti.init(arch=ti.gpu)


# --- ZMIANA: Usunięto kernel do downscalingu ---

# --- Zoptymalizowany kernel Taichi do obliczeń wskaźnika (bez zmian) ---
@ti.kernel
def _normalized_diff_kernel(
    band1: ti.template(), band2: ti.template(), result: ti.template()
):
    for i, j in result:
        b1_val = band1[i, j]
        b2_val = band2[i, j]
        denominator = b1_val + b2_val
        # Unikamy dzielenia przez zero
        if denominator > 1e-6: # Używamy małej wartości, aby uniknąć problemów z float
            result[i, j] = (b1_val - b2_val) / denominator
        else:
            result[i, j] = 0.0


def warm_up_taichi():
    """Rozgrzewa tylko kernel obliczeniowy."""
    print("Rozgrzewka kompilatora Taichi (jednorazowa operacja)...")
    dummy_10m = np.zeros((4, 4), dtype=np.float32)
    band1_field = ti.field(dtype=ti.f32, shape=(4, 4))
    band2_field = ti.field(dtype=ti.f32, shape=(4, 4))
    result_field = ti.field(dtype=ti.f32, shape=(4, 4))
    band1_field.from_numpy(dummy_10m)
    band2_field.from_numpy(dummy_10m)
    _normalized_diff_kernel(band1_field, band2_field, result_field)
    print("Kompilator Taichi gotowy do pracy wielowątkowej.")

warm_up_taichi()


# --- ZMIANA: Usunięto funkcję _downscale_band ---

def calculate_index(
    bands: Dict[str, np.ndarray], index_type: str
) -> Tuple[np.ndarray, np.ndarray]:
    """
    ZMIANA: Oblicza wskaźnik na natywnej, pełnej rozdzielczości (10m)
    dostarczonej przez API, bez downscalingu.
    """
    print(f"Rozpoczynam obliczenia dla wskaźnika: {index_type} przy użyciu Taichi na pełnej rozdzielczości...")
    
    # Maska danych ma tę samą rozdzielczość co pasma (10m)
    data_mask = bands["dataMask"]

    if index_type == "NDVI":
        # Używamy bezpośrednio pasm B04 i B08 w rozdzielczości 10m
        b4, b8 = bands["B04"], bands["B08"]
        h, w = b4.shape
        
        b4_field = ti.field(dtype=ti.f32, shape=(h, w))
        b8_field = ti.field(dtype=ti.f32, shape=(h, w))
        result_field = ti.field(dtype=ti.f32, shape=(h, w))
        
        b4_field.from_numpy(b4.astype(np.float32))
        b8_field.from_numpy(b8.astype(np.float32))
        
        _normalized_diff_kernel(b8_field, b4_field, result_field)
        return result_field.to_numpy(), data_mask
        
    elif index_type == "NDMI":
        # Używamy bezpośrednio pasm B08 i B11. API dostarcza je już
        # w tej samej rozdzielczości (10m).
        b8, b11 = bands["B08"], bands["B11"]
        h, w = b8.shape

        b8_field = ti.field(dtype=ti.f32, shape=(h, w))
        b11_field = ti.field(dtype=ti.f32, shape=(h, w))
        result_field = ti.field(dtype=ti.f32, shape=(h, w))

        b8_field.from_numpy(b8.astype(np.float32))
        b11_field.from_numpy(b11.astype(np.float32))

        _normalized_diff_kernel(b8_field, b11_field, result_field)
        return result_field.to_numpy(), data_mask
    else:
        raise ValueError(f"Nieznany typ wskaźnika: {index_type}")