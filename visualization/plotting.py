"""Funciones para visualizar el grafo."""

import os

import matplotlib.pyplot as plt
import osmnx as ox


def plot_graph(G, has_chargers=False, save_path=None, high_quality=True):
    """
    Plotea o guarda el grafo.

    Args:
        G: Grafo de NetworkX
        has_chargers: Si el grafo tiene nodos de carga
        save_path: Ruta donde guardar la imagen (None para mostrar)
        high_quality: Si True, genera imagen de alta calidad (mayor DPI y tamaño)
    """

    node_colors = []
    for node in G.nodes:
        is_start = G.nodes[node].get("is_start", False)
        is_end = G.nodes[node].get("is_end", False)
        on_path = G.nodes[node].get("on_path", False)
        is_charger = G.nodes[node].get("is_charger", False)
        visited_ch = G.nodes[node].get("charger_visited", False)

        if is_start:
            node_colors.append("white")  # start (indigo)
        elif is_end:
            node_colors.append("white")  # end (red)
        elif on_path and is_charger:
            node_colors.append("#F59E0B")  # charger on path (amber)
        elif on_path:
            node_colors.append("#06B6D4")  # path (cyan)
        elif visited_ch:
            node_colors.append("#22C55E")  # charger visited (green)
        elif is_charger:
            node_colors.append("#8B5CF6")  # charger not visited (violet)
        else:
            node_colors.append("#CBD5E1")  # normal (light slate)

    # Configurar tamaño de figura según calidad
    if high_quality:
        figsize = (24, 18)  # Figura más grande para mejor calidad
    else:
        figsize = (12, 9)  # Tamaño estándar

    result = ox.plot_graph(
        G,
        node_size=[G.nodes[node]["size"] for node in G.nodes],
        edge_color=[G.edges[edge]["color"] for edge in G.edges],
        edge_alpha=[G.edges[edge]["alpha"] for edge in G.edges],
        edge_linewidth=[G.edges[edge]["linewidth"] for edge in G.edges],
        node_color=node_colors,
        bgcolor="#060709",
        figsize=figsize,
        show=False,
        close=False,
    )

    if save_path:
        # ox.plot_graph puede retornar (fig, ax) o solo fig
        if isinstance(result, tuple):
            fig, ax = result
        else:
            fig = result

        # Crear directorio si no existe
        dir_path = os.path.dirname(save_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Configurar DPI según calidad
        dpi = 300 if high_quality else 150

        plt.figure(fig.number)
        plt.savefig(
            save_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor()
        )
        plt.close(fig)
    else:
        if isinstance(result, tuple):
            fig, ax = result
        else:
            fig = result
        plt.show()
        plt.close(fig)
