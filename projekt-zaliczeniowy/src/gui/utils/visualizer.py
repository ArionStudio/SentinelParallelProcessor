# src/gui/utils/visualizer.py

import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.cm
from PIL import Image, ImageTk
from typing import Tuple, List, Dict, Any


def _get_index_properties(index_type: str) -> Dict[str, Any]:
    """
    Zwraca słownik z właściwościami dla danego wskaźnika:
    kolory, granice przedziałów i etykiety opisowe.
    """
    if index_type == "NDVI":
        # ZMIANA: Nowa paleta kolorów od szarości/brązu do zieleni
        return {
            "colors": [
                "#8c510a",  # Ciemny brąz (woda/śnieg)
                "#bf812d",  # Brąz
                "#dfc27d",  # Jasny brąz/piaskowy
                "#f6e8c3",  # Bardzo jasny piaskowy (goła ziemia)
                "#c7e9c0",  # Bardzo blada zieleń
                "#a1d99b",  # Blada zieleń
                "#74c476",  # Jasna zieleń
                "#41ab5d",  # Zieleń
                "#238b45",  # Ciemna zieleń
                "#005a32",  # Bardzo ciemna zieleń (gęsty las)
            ],
            "boundaries": [-1.0, -0.2, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
            "labels": {
                -1.0: "Woda/Śnieg",
                0.0: "Skały/Ziemia",
                0.3: "Niska Roślinność",
                0.6: "Gęsta Roślinność",
                1.0: "Bardzo Gęsty Las",
            },
            "title": "NDVI (Wskaźnik Wegetacji)"
        }
    elif index_type == "NDMI":
        rd_bu_cmap = matplotlib.colormaps.get("RdBu").resampled(10)
        return {
            "colors": [
                matplotlib.colors.rgb2hex(rd_bu_cmap(i))
                for i in np.linspace(0, 1, 10)
            ],
            "boundaries": [-1.0, -0.6, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "labels": {
                -1.0: "Sucha Ziemia",
                0.0: "Niska Wilgotność",
                0.4: "Wysoka Wilgotność",
                1.0: "Woda",
            },
            "title": "NDMI (Wskaźnik Wilgotności)"
        }
    else: # Domyślne wartości
        return {
            "colors": [matplotlib.colors.rgb2hex(c) for c in matplotlib.colormaps.get("viridis").colors],
            "boundaries": np.linspace(-1, 1, 11),
            "labels": {-1.0: "Min", 1.0: "Max"},
            "title": f"{index_type} Value"
        }


def _create_discrete_cmap(
    colors: List[str],
    boundaries: List[float],
) -> Tuple[matplotlib.colors.Colormap, matplotlib.colors.Normalize]:
    """Funkcja pomocnicza do tworzenia dyskretnej mapy kolorów i normalizacji."""
    cmap = matplotlib.colors.ListedColormap(colors)
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N)
    return cmap, norm


def create_heatmap_image(
    index_data: np.ndarray, data_mask: np.ndarray, index_type: str
) -> Image.Image:
    """Tworzy obraz heatmapy (PIL.Image) na podstawie danych wskaźnika."""
    props = _get_index_properties(index_type)
    colormap, norm = _create_discrete_cmap(props["colors"], props["boundaries"])
    
    rgba_image = colormap(norm(index_data))

    alpha_channel = np.full(index_data.shape, 1.0, dtype=np.float32)
    alpha_channel[data_mask == 0] = 0.0
    rgba_image[:, :, 3] = alpha_channel

    rgb_image_uint8 = (rgba_image * 255).astype(np.uint8)
    return Image.fromarray(rgb_image_uint8, "RGBA")


def create_legend_image(
    index_type: str, width: int
) -> ImageTk.PhotoImage:
    """Tworzy obraz legendy (ImageTk.PhotoImage) dla danego wskaźnika."""
    props = _get_index_properties(index_type)
    colormap, norm = _create_discrete_cmap(props["colors"], props["boundaries"])
    
    fig = plt.Figure(figsize=(width / 100, 0.8), dpi=100)
    fig.suptitle(props["title"], fontsize=10, y=1.0)
    ax = fig.add_axes([0.05, 0.4, 0.9, 0.15])

    cbar = matplotlib.colorbar.ColorbarBase(
        ax, cmap=colormap, norm=norm, orientation="horizontal"
    )
    
    tick_locations = list(props["labels"].keys())
    cbar.set_ticks(tick_locations)
    cbar.set_ticklabels([props["labels"][t] for t in tick_locations])
    cbar.ax.tick_params(labelsize=8)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig)
    return ImageTk.PhotoImage(img)


def create_heatmap_figure(
    index_data: np.ndarray,
    data_mask: np.ndarray,
    index_type: str,
    location_name: str,
) -> plt.Figure:
    """Tworzy figurę Matplotlib z heatmapą, używaną w raporcie testowym."""
    props = _get_index_properties(index_type)
    colormap, norm = _create_discrete_cmap(props["colors"], props["boundaries"])
    
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    masked_data = np.where(data_mask == 1, index_data, np.nan)

    im = ax.imshow(masked_data, cmap=colormap, norm=norm)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{props['title']} - {location_name}", fontsize=14)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    tick_locations = list(props["labels"].keys())
    cbar.set_ticks(tick_locations)
    cbar.set_ticklabels([f"{val}\n({desc})" for val, desc in props["labels"].items()])
    cbar.ax.tick_params(labelsize=9)
    cbar.set_label(f"{index_type} Value", fontsize=12)

    return fig