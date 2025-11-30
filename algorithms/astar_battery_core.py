"""
Implementación de A* con gestión de batería para vehículos eléctricos.
Versión optimizada SIN visualización para benchmarking y comparaciones.
"""

import heapq
import time
from typing import Dict, List, Optional, Set, Tuple

from utils.helpers import (
    count_recharges,
    discretize_battery,
    euclidean_distance,
    reconstruct_path,
    reconstruct_path_with_battery,
)


def astar_battery(
    G,
    orig: int,
    dest: int,
    max_capacity: float = 100.0,
    initial_charge: float = 100.0,
    gamma_min: float = 0.15,
    charger_nodes: Optional[List[int]] = None,
    recharge_amount: float = 80.0,
    heuristic_func=None,
    return_battery_info: bool = False,  # <-- NUEVO PARÁMETRO
) -> Optional[Tuple[List[int], float, int, int, float]]:
    """
    Algoritmo A* con gestión de batería para vehículos eléctricos.

    El estado se representa como (nodo, batería_restante), permitiendo múltiples
    visitas al mismo nodo con diferentes niveles de batería.

    Args:
        G: Grafo de NetworkX con atributo 'energy_cost' en las aristas
        orig: Nodo origen
        dest: Nodo destino
        max_capacity: Capacidad máxima de batería (kWh)
        initial_charge: Carga inicial de batería (kWh)
        gamma_min: Consumo mínimo de energía por km para heurística (kWh/km)
        charger_nodes: Lista de nodos donde hay cargadores
        recharge_amount: Cantidad de energía recargada en cada estación (kWh)

    Returns:
        Si return_battery_info=False:
            Tupla (camino, energia_total, nodos_expandidos, num_recargas, tiempo_ejecucion)
        Si return_battery_info=True:
            Tupla (camino_con_bateria, energia_total, nodos_expandidos, num_recargas, tiempo_ejecucion)
            donde camino_con_bateria es List[Tuple[int, float, bool]] (nodo, batería, recargó_aquí)
        
        o None si no se encuentra camino viable.
        - camino: Lista de nodos del origen al destino
        - energia_total: Energía total consumida en el camino (kWh)
        - nodos_expandidos: Cantidad de estados explorados
        - num_recargas: Cantidad de recargas realizadas en el camino
        - tiempo_ejecucion: Tiempo de cómputo en segundos
    """
    if heuristic_func is None:
        heuristic_func = euclidean_distance

    start_time = time.time()

    if charger_nodes is None:
        charger_nodes = []

    charger_set = set(charger_nodes)

    # Estado: (nodo, batería_discretizada)
    # Para evitar explosión del espacio de estados, discretizamos la batería

    # Estructuras de datos
    # g_score: costo energético acumulado desde el origen
    # f_score: g + heurística
    initial_state = (orig, discretize_battery(initial_charge))

    g_score: Dict[Tuple[int, float], float] = {initial_state: 0.0}
    f_score: Dict[Tuple[int, float], float] = {
        initial_state: heuristic_func(G, orig, dest) * gamma_min
    }

    # Para reconstruir el camino
    came_from: Dict[Tuple[int, float], Tuple[int, float]] = {}

    # Mejor batería alcanzada por nodo (para optimización)
    best_battery_at_node: Dict[int, float] = {orig: initial_charge}

    # Cola de prioridad: (f_score, contador, estado)
    counter = 0
    pq = [(f_score[initial_state], counter, initial_state)]
    counter += 1

    # Estados visitados (completamente explorados)
    visited: Set[Tuple[int, float]] = set()

    nodes_expanded = 0

    while pq:
        current_f, _, current_state = heapq.heappop(pq)
        current_node, current_battery = current_state

        # Si ya fue visitado, continuar
        if current_state in visited:
            continue

        visited.add(current_state)
        nodes_expanded += 1

        # Si llegamos al destino
        if current_node == dest:
            # Reconstruir camino
            if return_battery_info:
                path = reconstruct_path_with_battery(came_from, current_state, charger_set)
            else:
                path = reconstruct_path(came_from, current_state)
            
            energy_total = g_score[current_state]
            num_recharges = count_recharges(came_from, current_state, charger_set)
            execution_time = time.time() - start_time

            return (path, energy_total, nodes_expanded, num_recharges, execution_time)

        # Expandir vecinos
        for neighbor in G.neighbors(current_node):
            # Obtener costo energético de la arista
            edge_data = G.get_edge_data(
                current_node, neighbor, 0
            )  # Key 0 para MultiDiGraph
            # Usar energy_cost si está disponible, sino calcular con distancia
            if edge_data and "energy_cost" in edge_data:
                energy_cost = edge_data["energy_cost"]
            else:
                # Fallback: usar distancia euclidiana * gamma_min
                distance = euclidean_distance(G, current_node, neighbor)
                energy_cost = distance * gamma_min

            # Verificar si hay suficiente batería para llegar al vecino
            if current_battery >= energy_cost:
                new_battery = current_battery - energy_cost
                new_battery_disc = discretize_battery(new_battery)

                neighbor_state = (neighbor, new_battery_disc)
                tentative_g = g_score[current_state] + energy_cost

                # Si encontramos un mejor camino a este estado
                if (
                    neighbor_state not in g_score
                    or tentative_g < g_score[neighbor_state]
                ):
                    came_from[neighbor_state] = current_state
                    g_score[neighbor_state] = tentative_g

                    # Heurística: distancia * consumo mínimo
                    h = heuristic_func(G, neighbor, dest) * gamma_min
                    f_score[neighbor_state] = tentative_g + h

                    heapq.heappush(
                        pq, (f_score[neighbor_state], counter, neighbor_state)
                    )
                    counter += 1

                    # Actualizar mejor batería en este nodo
                    if (
                        neighbor not in best_battery_at_node
                        or new_battery > best_battery_at_node[neighbor]
                    ):
                        best_battery_at_node[neighbor] = new_battery

        # Si el nodo actual es un cargador, SIEMPRE generar estado con batería recargada
        # Esto asegura que el algoritmo considere recargas incluso con batería alta
        if current_node in charger_set:
            # Recargar batería (incluso si ya está casi llena)
            recharged_battery = min(max_capacity, current_battery + recharge_amount)
            recharged_battery_disc = discretize_battery(recharged_battery)

            # Solo generar estado de recarga si realmente recarga algo significativo
            if recharged_battery_disc > current_battery:
                recharged_state = (current_node, recharged_battery_disc)

                # El costo de recargar es 0 en términos de energía consumida del vehículo
                # (asumimos que la recarga es externa)
                tentative_g = g_score[current_state]

                # Solo agregar el estado recargado si mejora nuestra situación
                if recharged_state not in g_score or tentative_g < g_score[recharged_state]:
                    came_from[recharged_state] = current_state
                    g_score[recharged_state] = tentative_g

                    h = heuristic_func(G, current_node, dest) * gamma_min
                    f_score[recharged_state] = tentative_g + h

                    heapq.heappush(pq, (f_score[recharged_state], counter, recharged_state))
                    counter += 1

    # No se encontró camino
    execution_time = time.time() - start_time
    return None
