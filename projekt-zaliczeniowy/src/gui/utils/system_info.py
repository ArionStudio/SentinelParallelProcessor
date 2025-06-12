
import platform
from typing import Dict

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

try:
    import psutil
except ImportError:
    psutil = None

def get_system_specs() -> Dict[str, str]:
    """
    Zbiera i formatuje kluczowe informacje o specyfikacji sprzętowej i systemowej.
    """
    specs = {}

    specs['OS'] = f"{platform.system()} {platform.release()} ({platform.machine()})"

    if cpuinfo:
        info = cpuinfo.get_cpu_info()
        l2_cache_kb = info.get('l2_cache_size', 0) // 1024
        l3_cache_mb = info.get('l3_cache_size', 0) // (1024 * 1024)
        
        specs['CPU'] = info.get('brand_raw', "N/A")
        specs['CPU Details'] = (
            f"Cores: {info.get('count', 'N/A')}, "
            f"Frequency: {info.get('hz_advertised_friendly', 'N/A')}, "
            f"L2 Cache: {l2_cache_kb} KB, L3 Cache: {l3_cache_mb} MB" 
        )
    else:
        specs['CPU'] = "N/A (required: 'py-cpuinfo')"
        specs['CPU Details'] = "N/A"

    if psutil:
        ram_gb = psutil.virtual_memory().total / (1024**3)
        specs['System RAM'] = f"{ram_gb:.2f} GB"
    else:
        specs['System RAM'] = "N/A (required: 'psutil')"

    specs['GPU'] = "Device used by Taichi backend (e.g., NVIDIA, AMD, Intel)"

    return specs