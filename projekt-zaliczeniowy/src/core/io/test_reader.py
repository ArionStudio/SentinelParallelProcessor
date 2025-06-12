import json
import os
from typing import Dict, Any, Optional

def load_test_results(filepath: str) -> Optional[Dict[str, Any]]:
    """Wczytuje wyniki testów z pliku JSON."""
    if not os.path.exists(filepath):
        print(f"Results file not found: {filepath}")
        return None
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading or parsing results file {filepath}: {e}")
        return None