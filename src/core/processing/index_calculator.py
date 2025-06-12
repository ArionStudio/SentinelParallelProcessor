# src/core/processing/index_calculator.py

import numpy as np
import taichi as ti
from typing import Dict, Tuple
import sys

# Importujemy kalkulator CPU jako fallback
from .cpu_single_thread_calculator import calculate_index as calculate_index_cpu

_TAICHI_INITIALIZED = False
_persistent_fields = {}

@ti.kernel
def _normalized_diff_kernel(
    band1: ti.template(), band2: ti.template(), result: ti.template()
):
    # ... (bez zmian)
    for i, j in result:
        b1_val = band1[i, j]
        b2_val = band2[i, j]
        denominator = b1_val + b2_val
        if denominator > 1e-6:
            result[i, j] = (b1_val - b2_val) / denominator
        else:
            result[i, j] = 0.0

def warm_up_taichi():
    # ... (bez zmian)
    global _TAICHI_INITIALIZED
    if _TAICHI_INITIALIZED:
        return

    print("Wykrywam system operacyjny w celu optymalizacji Taichi...")
    try:
        if sys.platform == "win32":
            print("System Windows wykryty. Używam backendu DirectX 11 (dx11).")
            ti.init(arch=ti.dx11)
        elif sys.platform == "darwin":
            print("System macOS wykryty. Używam backendu Metal.")
            ti.init(arch=ti.metal)
        else:
            print(f"System {sys.platform} wykryty. Używam domyślnego backendu GPU (Vulkan).")
            ti.init(arch=ti.gpu)
        
        print("Rozgrzewka kompilatora Taichi (jednorazowa operacja)...")
        dummy_10m = np.zeros((4, 4), dtype=np.float32)
        band1_field = ti.field(dtype=ti.f32, shape=(4, 4))
        band2_field = ti.field(dtype=ti.f32, shape=(4, 4))
        result_field = ti.field(dtype=ti.f32, shape=(4, 4))
        band1_field.from_numpy(dummy_10m)
        band2_field.from_numpy(dummy_10m)
        _normalized_diff_kernel(band1_field, band2_field, result_field)
        print("Kompilator Taichi gotowy do pracy.")
        _TAICHI_INITIALIZED = True
    except Exception as e:
        print(f"❌ Nie udało się zainicjować Taichi GPU: {e}")
        print("   Przełączam na tryb 'tylko CPU'.")
        _TAICHI_INITIALIZED = False # Upewniamy się, że jest False


def calculate_index(
    bands: Dict[str, np.ndarray], index_type: str
) -> Tuple[np.ndarray, np.ndarray]:
    global _TAICHI_INITIALIZED, _persistent_fields
    
    # ZMIANA: Dodajemy blok try-except do obsługi błędów wykonania GPU
    try:
        if not _TAICHI_INITIALIZED:
            warm_up_taichi()
        
        # Jeśli inicjalizacja się nie powiodła, od razu przejdź do CPU
        if not _TAICHI_INITIALIZED:
            raise ti.TaichiRuntimeError("Taichi not initialized, falling back to CPU.")

        print(f"Rozpoczynam obliczenia dla wskaźnika: {index_type} przy użyciu Taichi...")
        
        data_mask = bands["dataMask"]
        h, w = data_mask.shape
        
        def get_or_create_field(name: str, shape: tuple):
            if name in _persistent_fields and _persistent_fields[name].shape == shape:
                return _persistent_fields[name]
            else:
                print(f"Tworzenie nowego pola Taichi dla '{name}' o kształcie {shape}")
                field = ti.field(dtype=ti.f32, shape=shape)
                _persistent_fields[name] = field
                return field

        if index_type == "NDVI":
            b4, b8 = bands["B04"], bands["B08"]
            b4_field = get_or_create_field('b4', (h, w))
            b8_field = get_or_create_field('b8', (h, w))
            result_field = get_or_create_field('result_ndvi', (h, w))
            b4_field.from_numpy(b4.astype(np.float32))
            b8_field.from_numpy(b8.astype(np.float32))
            _normalized_diff_kernel(b8_field, b4_field, result_field)
            return result_field.to_numpy(), data_mask
            
        elif index_type == "NDMI":
            b8, b11 = bands["B08"], bands["B11"]
            b8_field = get_or_create_field('b8', (h, w))
            b11_field = get_or_create_field('b11', (h, w))
            result_field = get_or_create_field('result_ndmi', (h, w))
            b8_field.from_numpy(b8.astype(np.float32))
            b11_field.from_numpy(b11.astype(np.float32))
            _normalized_diff_kernel(b8_field, b11_field, result_field)
            return result_field.to_numpy(), data_mask
        else:
            raise ValueError(f"Nieznany typ wskaźnika: {index_type}")

    except ti.TaichiRuntimeError as e:
        print(f"⚠️ Błąd wykonania Taichi (GPU): {e}")
        print("   Automatycznie przełączam na obliczenia CPU dla tego zadania.")
        # Użyj kalkulatora CPU jako trybu awaryjnego