"""Funciones para estilizar los ejes del grafo (versión más brillante)."""

# Unvisited: de #1F2937 -> #334155 (slate más claro), más opaco
# Visited:   de #475569 -> #64748B (slate más claro)
# Active:    mantiene tono ámbar pero con un poco más de “pop”
# Path:      cian más luminoso


def style_unvisited_edge(G, edge):
    """Estiliza un eje no visitado."""
    G.edges[edge]["color"] = "#334155"  # antes: #1F2937
    G.edges[edge]["alpha"] = 0.35  # antes: 0.20
    G.edges[edge]["linewidth"] = 0.3  # antes: 0.3


def style_visited_edge(G, edge):
    """Estiliza un eje visitado."""
    G.edges[edge]["color"] = "#64748B"  # antes: #475569
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 0.8  # antes: 0.5


def style_active_edge(G, edge):
    """Estiliza un eje activo."""
    G.edges[edge]["color"] = "#FFCB3A"  # antes: #FFD166
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 0.8  # más controlado que 7, igual muy visible


def style_path_edge(G, edge):
    """Estiliza un eje que forma parte del camino."""
    G.edges[edge]["color"] = "#21C4FF"  # antes: #00B0FF
    G.edges[edge]["alpha"] = 1.0
    G.edges[edge]["linewidth"] = 1  # antes: 0.8
