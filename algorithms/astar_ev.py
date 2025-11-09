"""Implementación del algoritmo A*."""

import heapq
import os
import random

from graph.chargers_loader import get_charger_nodes
from utils.helpers import euclidean_distance
from visualization.plotting import plot_graph
from visualization.styles import (
    style_active_edge,
    style_unvisited_edge,
    style_visited_edge,
)


def a_star_ev(
    G,
    orig,
    dest,
    plot=False,
    save_dir=None,
    algorithm_name="a_star",
    save_frames=False,
    max_capacity=100,
    initial_charge=100,
    chargers_amount=10,
):
    """
    Algoritmo A* para encontrar el camino más corto con vehículo eléctrico.

    Args:
        G: Grafo de NetworkX
        orig: Nodo origen
        dest: Nodo destino
        plot: Si mostrar el gráfico final
        save_dir: Directorio donde guardar frames (None para no guardar)
        algorithm_name: Nombre del algoritmo para nombrar los frames
        save_frames: Si guardar frames intermedios (cada iteración/paso)

    TODO - IMPLEMENTAR GESTION DE ENERGIA (EV) SEGUN ENTREGa_algabo.md:
    ==================================================================

    Alcance (sin codigo, solo definicion):

    1) Modelo de estado y puntajes
       - Estado: (nodo, bateria). g_score = energia acumulada; f = g + h.

    2) Costo energetico en g_score
       - e_ij = gamma_ij * d_ij (km). Acumular energia, no distancia.
       - Movimiento valido solo si bateria_actual >= e_ij; luego restar e_ij.

    3) Heuristica admisible basada en energia
       - h(n) = gamma_min * dist_linea_recta(n, destino) (en km).
       - Admisible: no sobreestima (distancia euclidiana) y usa consumo minimo.

    4) Recarga en estaciones
       - En nodos cargadores: b_nueva = min(B_max, b_actual + Delta_b_i), sin costo.

    5) Gestion de estados y dominancia
       - Permitir re-visitar un nodo si mejora energia o bateria util.
       - Estructura para recordar mejor estado alcanzado por nodo.

    6) Parametros/hipotesis
       - B_max, b_0, gamma/gamma_ij, gamma_min. Posible discretizacion de bateria.

    7) Salida esperada
       - Ruta y energia total; reconstruccion como en version actual.

    """

    print(f"id origen: {orig}")
    print(f"id destino: {dest}")

    # Intentar cargar cargadores reales desde JSON
    try:
        charger_nodes, charger_info = get_charger_nodes(G, max_chargers=chargers_amount)

        # Excluir origen y destino de los cargadores
        charger_nodes = [n for n in charger_nodes if n != orig and n != dest]

    except Exception:
        # Fallback a cargadores aleatorios
        nodes = list(G.nodes)
        # Excluir origen y destino para cargadores
        if orig in nodes:
            nodes.remove(orig)
        if dest in nodes:
            nodes.remove(dest)

        charger_nodes = random.sample(nodes, k=min(chargers_amount, len(nodes)))
        charger_info = {}

    for node in G.nodes:
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
        G.nodes[node]["g_score"] = float("inf")
        G.nodes[node]["f_score"] = float("inf")
        G.nodes[node]["visited"] = False
        G.nodes[node]["is_start"] = False
        G.nodes[node]["is_end"] = False

        # A* EV
        G.nodes[node]["battery_remaining"] = max_capacity
        G.nodes[node]["charger_visited"] = False
        G.nodes[node]["is_charger"] = False
        G.nodes[node]["charger_size"] = 0

    for node in charger_nodes:
        # visibilidad asegurada en el plot (usa 'size')
        G.nodes[node]["is_charger"] = True
        G.nodes[node]["charger_size"] = 50
        G.nodes[node]["size"] = 10

    for edge in G.edges:
        style_unvisited_edge(G, edge)

    G.nodes[orig]["size"] = 20
    G.nodes[dest]["size"] = 20
    G.nodes[orig]["g_score"] = 0
    G.nodes[orig]["f_score"] = euclidean_distance(G, orig, dest)
    G.nodes[orig]["battery_remaining"] = max_capacity
    G.nodes[orig]["is_start"] = True
    G.nodes[dest]["is_end"] = True

    pq = [(G.nodes[orig]["f_score"], orig)]
    step = 0
    reached = False

    while pq:
        _, node = heapq.heappop(pq)

        if G.nodes[node]["visited"]:
            continue

        if G.nodes[node].get("is_charger", False):
            G.nodes[node]["charger_visited"] = True

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
