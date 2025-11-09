"""Implementación del algoritmo A*."""

import heapq
import os
from visualization.styles import (
    style_unvisited_edge,
    style_visited_edge,
    style_active_edge,
)
from visualization.plotting import plot_graph
from utils.helpers import euclidean_distance


def a_star(
    G,
    orig,
    dest,
    plot=False,
    save_dir=None,
    algorithm_name="a_star",
    save_frames=False,
):
    """
    Algoritmo A* para encontrar el camino más corto.

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
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
        G.nodes[node]["g_score"] = float("inf")
        G.nodes[node]["f_score"] = float("inf")
        G.nodes[node]["visited"] = False

    for edge in G.edges:
        style_unvisited_edge(G, edge)

    G.nodes[orig]["size"] = 50
    G.nodes[dest]["size"] = 50
    G.nodes[orig]["g_score"] = 0
    G.nodes[orig]["f_score"] = euclidean_distance(G, orig, dest)

    pq = [(G.nodes[orig]["f_score"], orig)]
    step = 0
    reached = False

    while pq:
        _, node = heapq.heappop(pq)

        if node == dest:
            # Guardado "en el momento de llegar" (solo si se eligieron frames)
            if plot:
                print("Iteraciones:", step)
                plot_graph(G)
            if save_dir and save_frames:
                save_path = os.path.join(
                    save_dir, f"{algorithm_name}_frame_{step:05d}.png"
                )
                plot_graph(G, save_path=save_path)
            reached = True
            break

        if G.nodes[node]["visited"]:
            continue
        G.nodes[node]["visited"] = True

        for edge in G.out_edges(node):
            style_visited_edge(G, (edge[0], edge[1], 0))
            neighbor = edge[1]
            # Usar distancia euclidiana
            dist = euclidean_distance(G, node, neighbor)
            tentative_g_score = G.nodes[node]["g_score"] + dist
            if tentative_g_score < G.nodes[neighbor]["g_score"]:
                G.nodes[neighbor]["previous"] = node
                G.nodes[neighbor]["g_score"] = tentative_g_score
                # Heurística: distancia euclidiana hasta el destino
                G.nodes[neighbor]["f_score"] = tentative_g_score + euclidean_distance(
                    G, neighbor, dest
                )
                heapq.heappush(pq, (G.nodes[neighbor]["f_score"], neighbor))
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
