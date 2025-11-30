"""Funciones auxiliares."""

from typing import Dict, List, Set, Tuple


def euclidean_distance(G, node1, node2):
    """
    Calcula la distancia euclidiana entre dos nodos.

    Args:
        G: Grafo de NetworkX
        node1: Primer nodo
        node2: Segundo nodo

    Returns:
        Distancia euclidiana entre los nodos
    """
    x1, y1 = G.nodes[node1]["x"], G.nodes[node1]["y"]
    x2, y2 = G.nodes[node2]["x"], G.nodes[node2]["y"]
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def manhattan_distance(G, node1, node2):
    """
    Calcula la distancia de Manhattan entre dos nodos.
    Suma de las diferencias absolutas en x e y.
    """
    x1, y1 = G.nodes[node1]["x"], G.nodes[node1]["y"]
    x2, y2 = G.nodes[node2]["x"], G.nodes[node2]["y"]
    return abs(x2 - x1) + abs(y2 - y1)


def octile_distance(G, node1, node2):
    """
    Distancia octil: permite movimientos diagonales.
    Optimizada para grids con movimiento en 8 direcciones.
    """
    x1, y1 = G.nodes[node1]["x"], G.nodes[node1]["y"]
    x2, y2 = G.nodes[node2]["x"], G.nodes[node2]["y"]
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return max(dx, dy) + (2**0.5 - 1) * min(dx, dy)


def count_recharges(
    came_from: Dict[Tuple[int, float], Tuple[int, float]],
    final_state: Tuple[int, float],
    charger_set: Set[int],
) -> int:
    """
    Cuenta recargas rastreando transiciones de estado donde la batería AUMENTA.
    """
    recharges = 0
    current_state = final_state

    while current_state in came_from:
        prev_state = came_from[current_state]
        prev_node, prev_battery = prev_state
        curr_node, curr_battery = current_state

        # Si es el mismo nodo pero la batería aumentó = RECARGA
        if prev_node == curr_node and curr_battery > prev_battery:
            if prev_node in charger_set:
                recharges += 1

        current_state = prev_state

    return recharges


def reconstruct_path(
    came_from: Dict[Tuple[int, float], Tuple[int, float]],
    current_state: Tuple[int, float],
) -> List[int]:
    """
    Reconstruye el camino desde el origen hasta el estado actual (SOLO NODOS).

    Args:
        came_from: Diccionario de predecesores
        current_state: Estado final

    Returns:
        Lista de nodos desde origen a destino
    """
    path = [current_state[0]]  # Solo guardamos los nodos, no la batería

    while current_state in came_from:
        current_state = came_from[current_state]
        # Evitar agregar duplicados consecutivos (cuando recargamos en el mismo nodo)
        if not path or current_state[0] != path[-1]:
            path.append(current_state[0])

    path.reverse()
    return path


def reconstruct_path_with_battery(
    came_from: Dict[Tuple[int, float], Tuple[int, float]],
    current_state: Tuple[int, float],
    charger_set: Set[int],
) -> List[Tuple[int, float, bool]]:
    """
    Reconstruye el camino CON información de batería y recargas.

    Args:
        came_from: Diccionario de predecesores
        current_state: Estado final
        charger_set: Conjunto de nodos con cargadores

    Returns:
        Lista de tuplas (nodo, batería, recargó_aquí) desde origen a destino
    """
    path_with_battery = []
    
    while True:
        node, battery = current_state
        
        # Verificar si hubo recarga en este nodo
        recharged = False
        if current_state in came_from:
            prev_state = came_from[current_state]
            prev_node, prev_battery = prev_state
            
            # Si es el mismo nodo pero la batería aumentó = RECARGA
            if prev_node == node and battery > prev_battery and node in charger_set:
                recharged = True
        
        path_with_battery.append((node, battery, recharged))
        
        if current_state not in came_from:
            break
        
        current_state = came_from[current_state]
    
    path_with_battery.reverse()
    return path_with_battery


def discretize_battery(battery: float, step: float = 0.1) -> float:
    """
    Discretiza el nivel de batería para reducir espacio de estados.
    
    Step=0.1 proporciona suficiente granularidad para baterías pequeñas (~3 kWh)
    sin explotar el espacio de estados.
    """
    return round(battery / step) * step
