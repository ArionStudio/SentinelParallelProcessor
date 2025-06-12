# src/gui/utils/visualizer.py

import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.cm
from PIL import Image, ImageTk
from typing import Tuple, List


def _create_discrete_cmap(
    colors: List[str],
    boundaries: List[float],
) -> Tuple[matplotlib.colors.Colormap, matplotlib.colors.Normalize]:
    """Funkcja pomocnicza do tworzenia dyskretnej mapy kolorów i normalizacji."""
    cmap = matplotlib.colors.ListedColormap(colors)
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N)
    return cmap, norm


def _get_colormap_and_norm(
    index_type: str,
) -> Tuple[matplotlib.colors.Colormap, matplotlib.colors.Normalize]:
    """
    Zwraca dedykowaną, szczegółową mapę kolorów oraz normalizację.
    """
    boundaries = [
        -1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0,
    ]

    if index_type == "NDVI":
        # Paleta kolorów zoptymalizowana dla wegetacji (od brązu/fioletu do zieleni)
        colors = [
            "#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b",
            "#ffffbf", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850",
        ]
        return _create_discrete_cmap(colors, boundaries)

    elif index_type == "NDMI":
        # Paleta kolorów zoptymalizowana dla wilgotności (od czerwieni/brązu do błękitu)
        # ZMIANA: Użycie nowszego API Matplotlib
        rd_bu_cmap = matplotlib.colormaps.get("RdBu").resampled(10)
        colors = [
            matplotlib.colors.rgb2hex(rd_bu_cmap(i))
            for i in np.linspace(0, 1, 10)
        ]
        return _create_discrete_cmap(colors, boundaries)

    else:
        cmap = matplotlib.colormaps.get("viridis")
        norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)
        return cmap, norm


def create_heatmap_image(
    index_data: np.ndarray, data_mask: np.ndarray, index_type: str
) -> Image.Image:
    """Tworzy obraz heatmapy (PIL.Image) na podstawie danych wskaźnika."""
    colormap, norm = _get_colormap_and_norm(index_type)
    # Wartości NaN w index_data zostaną poprawnie obsłużone przez colormap
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
    colormap, norm = _get_colormap_and_norm(index_type)
    fig = plt.Figure(figsize=(width / 100, 0.6), dpi=100)
    ax = fig.add_axes([0.05, 0.5, 0.9, 0.2])

    cbar = matplotlib.colorbar.ColorbarBase(
        ax, cmap=colormap, norm=norm, orientation="horizontal"
    )
    if isinstance(norm, matplotlib.colors.BoundaryNorm):
        cbar.set_ticks(norm.boundaries)
        cbar.set_ticklabels([f"{b:.1f}" for b in norm.boundaries])
    cbar.set_label(f"{index_type} Value")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    buf.seek(0)
    img = Image.open(buf)
    plt.close(fig) # Zamykamy figurę, aby nie zużywać pamięci
    return ImageTk.PhotoImage(img)


def create_heatmap_figure(
    index_data: np.ndarray,
    data_mask: np.ndarray,
    index_type: str,
    location_name: str,
) -> plt.Figure:
    """Tworzy figurę Matplotlib z heatmapą, używaną w raporcie testowym."""
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    # Użycie np.nan jest idiomatycznym sposobem na maskowanie w Matplotlib
    masked_data = np.where(data_mask == 1, index_data, np.nan)
    colormap, norm = _get_colormap_and_norm(index_type)

    im = ax.imshow(masked_data, cmap=colormap, norm=norm)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        f"{index_type} ({'Vegetation' if index_type == 'NDVI' else 'Moisture'} Index) - {location_name}",
        fontsize=14,
    )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(f"{index_type} Value")

    return fig