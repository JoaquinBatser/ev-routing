"""Funciones para estilizar los ejes del grafo (versión más brillante)."""

# Unvisited: de #1F2937 -> #334155 (slate más claro), más opaco
# Visited:   de #475569 -> #64748B (slate más claro)
# Active:    mantiene tono ámbar pero con un poco más de “pop”
# Path:      cian más luminoso


def style_unvisited_edge(G, edge):
    """Estiliza un eje no visitado."""
    G.edges[edge]["color"] = "#334155"
    G.edges[edge]["alpha"] = 0.35
    G.edges[edge]["linewidth"] = 0.3


def style_visited_edge(G, edge):
    """Estiliza un eje visitado."""
    G.edges[edge]["color"] = "#64748B"
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 0.8


def style_active_edge(G, edge):
    """Estiliza un eje activo."""
    G.edges[edge]["color"] = "#FFCB3A"
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 0.8


def style_path_edge(G, edge):
    """Estiliza un eje que forma parte del camino."""
    G.edges[edge]["color"] = "#21C4FF"
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 1


def style_path_edge_with_battery(G, edge, battery_percent: float):
    """
    Estiliza un eje del camino según el porcentaje de batería.

    Args:
        G: Grafo
        edge: Tupla (nodo_origen, nodo_destino, key)
        battery_percent: Porcentaje de batería (0-100)
    """
    # Determinar color según nivel de batería
    if battery_percent > 66:
        color = "#00FF00"  # Verde
    elif battery_percent > 33:
        color = "#FFD700"  # Amarillo
    else:
        color = "#FF0000"  # Rojo

    G.edges[edge]["color"] = color
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 1.5
