import numpy as np
from typing import Dict, Tuple

def calculate_index(
    bands: Dict[str, np.ndarray], index_type: str
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Oblicza wskaźnik (NDVI lub NDMI) na CPU w jednym wątku,
    wykorzystując zoptymalizowane operacje wektorowe NumPy.
    """
    print(f"Rozpoczynam obliczenia dla wskaźnika: {index_type} przy użyciu CPU (Single-Thread, NumPy)...")
    
    data_mask = bands["dataMask"]
    
    if index_type == "NDVI":
        b4 = bands["B04"].astype(np.float32)
        b8 = bands["B08"].astype(np.float32)
        
        denominator = b8 + b4
        result = np.divide(b8 - b4, denominator, where=denominator > 1e-6, out=np.zeros_like(b4))
        
    elif index_type == "NDMI":
        b8 = bands["B08"].astype(np.float32)
        b11 = bands["B11"].astype(np.float32)
        
        denominator = b8 + b11
        result = np.divide(b8 - b11, denominator, where=denominator > 1e-6, out=np.zeros_like(b8))
        
    else:
        raise ValueError(f"Nieznany typ wskaźnika: {index_type}")

    return result, data_mask