"""Implementación del algoritmo de Dijkstra."""

import heapq
import os
import random

from graph.chargers_loader import get_charger_nodes
from visualization.plotting import plot_graph
from visualization.styles import (
    style_active_edge,
    style_unvisited_edge,
    style_visited_edge,
)


def dijkstra_ev(
    G,
    orig,
    dest,
    max_capacity=100,
    initial_charge=100,
    chargers_amount=10,
    plot=False,
    save_dir=None,
    algorithm_name="dijkstra_ev",
    save_frames=False,
):
    """
    Algoritmo de Dijkstra para encontrar el camino más corto con nodos cargadores.

    Args:
        G: Grafo de NetworkX
        orig: Nodo origen
        dest: Nodo destino
        max_capacity: Capacidad máxima de la batería (no usada aún en costos)
        chargers_amount: Cantidad de cargadores a marcar
        plot: Si mostrar el gráfico final
        save_dir: Directorio donde guardar frames (None para no guardar)
        algorithm_name: Nombre del algoritmo para nombrar los frames
        save_frames: Si guardar frames intermedios (cada iteración/paso)

    TODO - IMPLEMENTAR GESTION DE ENERGIA (EV) SEGUN ENTREGa_algabo.md:
    ==================================================================

    Alcance (sin codigo, solo definicion):

    1) Modelo de estado
       - Expandir a (nodo, bateria). La bateria es el recurso limitante.
       - La cola de prioridad usa como clave el costo acumulado (energia, no tiempo).

    2) Costo a minimizar
       - Energia total consumida: sumar e_ij por arista.
       - e_ij = gamma_ij * d_ij, con d_ij en km (usar longitud real de la arista).
       - Objetivo: minimizar sum(e_ij) desde origen hasta destino.

    3) Restriccion de autonomia
       - Movimiento permitido solo si bateria_actual >= e_ij.
       - Al moverse: bateria_nueva = bateria_actual - e_ij.

    4) Recarga en estaciones
       - Si el nodo es cargador: permitir recarga discreta
         b_nueva = min(B_max, b_actual + Delta_b_i).
       - La recarga no incrementa el costo (solo habilita continuar).

    5) Gestion de estados repetidos
       - Un mismo nodo puede visitarse con distintos niveles de bateria.
       - Guardar el mejor estado alcanzado por nodo considerando costo y bateria.
       - Evitar descartar estados potencialmente utiles (p.ej., llegar con mas bateria).

    6) Parametros/hipotesis
       - B_max (capacidad), b_0 (carga inicial), gamma (kWh/km) o gamma_ij.
       - Discretizacion de bateria si es necesario para acotar el espacio de estados.

    7) Salida esperada
       - Camino y costo energetico total; reconstruccion de ruta como hasta ahora.

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

    # Initialize nodes
    for node in G.nodes:
        G.nodes[node]["visited"] = False
        G.nodes[node]["distance"] = float("inf")
        G.nodes[node]["previous"] = None
        G.nodes[node]["size"] = 0
        G.nodes[node]["is_start"] = False
        G.nodes[node]["is_end"] = False

        # Dijkstra EV
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

    G.nodes[orig]["distance"] = 0
    G.nodes[orig]["size"] = 20
    G.nodes[orig]["is_start"] = True
    G.nodes[dest]["is_end"] = True
    G.nodes[dest]["size"] = 20
    G.nodes[orig]["battery_remaining"] = max_capacity

    pq = [(0, orig)]
    step = 0

    while pq:
        _, node = heapq.heappop(pq)

        # Verificar si ya visitamos este nodo (puede estar duplicado en la cola)
        if G.nodes[node]["visited"]:
            continue

        if G.nodes[node].get("is_charger", False):
            G.nodes[node]["charger_visited"] = True

        # Si es el destino, terminamos inmediatamente
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
            break  # Detener inmediatamente cuando se encuentra el destino

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
