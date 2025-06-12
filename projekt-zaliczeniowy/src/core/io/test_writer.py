import json
import os
from typing import Dict, Any

def save_test_results(data: Dict[str, Any], filepath: str):
    """Zapisuje słownik z wynikami testów do pliku JSON."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving test results to {filepath}: {e}")