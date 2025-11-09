"""Implementación del algoritmo de Dijkstra."""

import heapq
import os

from visualization.plotting import plot_graph
from visualization.styles import (
    style_active_edge,
    style_unvisited_edge,
    style_visited_edge,
)


def dijkstra(
    G,
    orig,
    dest,
    plot=False,
    save_dir=None,
    algorithm_name="dijkstra",
    save_frames=False,
):
    """
    Algoritmo de Dijkstra para encontrar el camino más corto.

    Args:
        G: Grafo de NetworkX
        orig: Nodo origen
        dest: Nodo destino
        plot: Si mostrar el gráfico final
        save_dir: Directorio donde guardar frames (None para no guardar)
        algorithm_name: Nombre del algoritmo para nombrar los frames
        save_frames: Si guardar frames intermedios (cada iteración/paso)
    """
    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float("inf")
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0

    for edge in G.edges:
        style_unvisited_edge(G, edge)

    G.nodes[orig]["distance"] = 0
    G.nodes[orig]["size"] = 20
    G.nodes[dest]["size"] = 20

    pq = [(0, orig)]
    step = 0
    reached = False

    while pq:
        _, node = heapq.heappop(pq)

        # Verificar si ya visitamos este nodo (puede estar duplicado en la cola)
        if G.nodes[node]["visited"]:
            continue

        # Si es el destino, terminamos
        if node == dest:
            if plot:
                print("Iteraciones:", step)
                plot_graph(G)
            # Guardar frame de llegada solo si se quieren frames intermedios
            if save_dir and save_frames:
                save_path = os.path.join(
                    save_dir, f"{algorithm_name}_frame_{step:05d}.png"
                )
                plot_graph(G, save_path=save_path)
            reached = True
            break

        # Marcar como visitado
        G.nodes[node]["visited"] = True

        # Procesar vecinos
        for edge in G.out_edges(node):
            style_visited_edge(G, (edge[0], edge[1], 0))
            neighbor = edge[1]
            weight = G.edges[(edge[0], edge[1], 0)]["weight"]
            if G.nodes[neighbor]["distance"] > G.nodes[node]["distance"] + weight:
                G.nodes[neighbor]["distance"] = G.nodes[node]["distance"] + weight
                G.nodes[neighbor]["previous"] = node
                heapq.heappush(pq, (G.nodes[neighbor]["distance"], neighbor))
                for edge2 in G.out_edges(neighbor):
                    style_active_edge(G, (edge2[0], edge2[1], 0))

        step += 1
        # Frames intermedios
        if save_dir and save_frames:
            save_path = os.path.join(save_dir, f"{algorithm_name}_frame_{step:05d}.png")
            plot_graph(G, save_path=save_path)

    # SIEMPRE guardar el último estado de exploración
    if save_dir:
        final_frame_path = os.path.join(
            save_dir, f"{algorithm_name}_final_exploration.png"
        )
        print(f"Guardando último frame de exploración en {final_frame_path}")
        plot_graph(G, save_path=final_frame_path)
