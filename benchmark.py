"""
Benchmark para comparar A* (con distintas heurísticas) y Greedy
con gestión de batería.

- Origen fijo: Ciudad Vieja
- Destinos: todos los barrios de MONTEVIDEO_BARRIOS (excepto Ciudad Vieja)
- Algoritmos:
    * astar_euclidean → A* con distancia Euclidiana
    * astar_manhattan → A* con distancia Manhattan
    * astar_octile    → A* con distancia Octile
    * greedy          → Greedy original

Los resultados NO se imprimen, se guardan en un JSON.
Las imágenes muestran el path simple (sin colores de batería).
"""

import copy
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import sys
from halo import Halo

from algorithms.astar_battery_core import astar_battery
from algorithms.greedy_battery_core import greedy_battery
from graph.chargers_loader import get_charger_nodes
from graph.graph_setup import load_graph
from graph.montevideo_barrios import MONTEVIDEO_BARRIOS, get_nearest_node
from utils.helpers import euclidean_distance, manhattan_distance, octile_distance
from visualization.plotting import plot_graph
from visualization.styles import style_path_edge, style_unvisited_edge


GAMMA = 1.2
MAX_CAPACITY = 5.0
INITIAL_CHARGE = 5.0  # kWh - Comenzar con batería llena
RECHARGE_AMOUNT = 4.5  # kWh - Recarga al 90% de capacidad

# A* como 3 algoritmos distintos (por heurística/gamma_min)
ASTAR_VARIANTS = [
    ("astar_euclidean", euclidean_distance, GAMMA),
    ("astar_manhattan", manhattan_distance, GAMMA),
    ("astar_octile", octile_distance, GAMMA),
]

GREEDY_NAME = "greedy"

GENERATE_IMAGES = False

DOTS_SPINNER = {
    "interval": 80,
    "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
}

# Dibuja el camino encontrado sobre el grafo y lo guarda 
def save_path_visualization(
    G_original,
    path: List[int],
    charger_nodes: List[int],
    origen: int,
    destino: int,
    save_path: str,
):
    """
    Visualización simple:
    - path en cian (style_path_edge)
    - cargadores en violeta
    - sin colores de batería.
    """
    G = copy.deepcopy(G_original)

    # Inicializar propiedades de nodos
    for node in G.nodes:
        G.nodes[node]["size"] = 0
        G.nodes[node]["on_path"] = False
        G.nodes[node]["is_start"] = False
        G.nodes[node]["is_end"] = False
        G.nodes[node]["is_charger"] = False
        G.nodes[node]["charger_visited"] = False

    # Marcar cargadores
    for node in charger_nodes:
        if node in G.nodes:
            G.nodes[node]["is_charger"] = True
            G.nodes[node]["size"] = 50

    # Inicializar edges
    for edge in G.edges:
        style_unvisited_edge(G, edge)

    # Marcar origen y destino
    G.nodes[origen]["is_start"] = True
    G.nodes[origen]["size"] = 100
    G.nodes[destino]["is_end"] = True
    G.nodes[destino]["size"] = 100

    # Path
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        G.nodes[u]["on_path"] = True
        style_path_edge(G, (u, v, 0))
        if G.nodes[u].get("is_charger"):
            G.nodes[u]["charger_visited"] = True
            G.nodes[u]["size"] = 80

    G.nodes[path[-1]]["on_path"] = True

    # Guardar
    plot_graph(G, has_chargers=True, save_path=save_path, high_quality=True)


# Ejecuta una variante de A* llamando a la función astar_battery
def run_astar_variant(
    variant_name: str,
    heuristic_func,
    gamma_min: float,
    G,
    charger_nodes: List[int],
    origen: int,
    destino: int,
) -> Tuple[Dict, Optional[List[int]]]:
    """Ejecuta una variante de A* y devuelve (metrics, path)."""
    result = astar_battery(
        G,
        origen,
        destino,
        heuristic_func=heuristic_func,  # <-- NUEVO
        max_capacity=MAX_CAPACITY,
        initial_charge=INITIAL_CHARGE,
        gamma_min=gamma_min,
        charger_nodes=charger_nodes,
        recharge_amount=RECHARGE_AMOUNT,
    )

    metrics: Dict = {
        "algoritmo": variant_name,
        "tipo": "astar",
        "gamma_min": gamma_min,
        "energy_kwh": None,
        "nodes_expanded": None,
        "num_recharges": None,
        "time_seconds": None,
        "path_length": None,
        "reached_destination": False,
    }

    if result is None:
        return metrics, None

    path, energy, nodes_expanded, num_recharges, time_s = result
    metrics.update(
        {
            "energy_kwh": energy,
            "nodes_expanded": nodes_expanded,
            "num_recharges": num_recharges,
            "time_seconds": time_s,
            "path_length": len(path),
            "reached_destination": True,
        }
    )
    return metrics, path

# Corre la función greedy_battery 
def run_greedy(
    G,
    charger_nodes: List[int],
    origen: int,
    destino: int,
) -> Tuple[Dict, Optional[List[int]]]:
    """Ejecuta Greedy y devuelve (metrics, path)."""
    result = greedy_battery(
        G,
        origen,
        destino,
        max_capacity=MAX_CAPACITY,
        initial_charge=INITIAL_CHARGE,
        gamma_min=GAMMA,
        charger_nodes=charger_nodes,
        recharge_amount=RECHARGE_AMOUNT,
    )

    metrics: Dict = {
        "algoritmo": GREEDY_NAME,
        "tipo": "greedy",
        "gamma_min": None,
        "energy_kwh": None,
        "nodes_expanded": None,
        "num_recharges": None,
        "time_seconds": None,
        "path_length": None,
        "reached_destination": False,
    }

    if result is None:
        return metrics, None

    path, energy, nodes_expanded, num_recharges, time_s = result
    metrics.update(
        {
            "energy_kwh": energy,
            "nodes_expanded": nodes_expanded,
            "num_recharges": num_recharges,
            "time_seconds": time_s,
            "path_length": len(path),
            "reached_destination": True,
        }
    )
    return metrics, path


# Esta función ejecuta todos los algoritmos para origen/destino
def run_test(
    G,
    charger_nodes: List[int],
    origen_name: str,
    destino_name: str,
    test_num: int,
    output_dir: str,
):
    """Ejecuta todas las variantes para un origen/destino y devuelve dict con resultados."""
    origen = get_nearest_node(G, origen_name)
    destino = get_nearest_node(G, destino_name)

    test_dir = os.path.join(
        output_dir,
        f"test_{test_num}_{origen_name.replace(' ', '_')}_to_{destino_name.replace(' ', '_')}",
    )
    os.makedirs(test_dir, exist_ok=True)

    test_result: Dict = {
        "test_id": test_num,
        "origen_name": origen_name,
        "destino_name": destino_name,
        "origen_node": origen,
        "destino_node": destino,
        "algorithms": [],
    }

    # ---- A* (3 heurísticas) ----
    for variant_name, heuristic_func, gamma_min in ASTAR_VARIANTS:
        metrics, path = run_astar_variant(
            variant_name, heuristic_func, gamma_min, G, charger_nodes, origen, destino
        )
        test_result["algorithms"].append(metrics)

        if path is not None and GENERATE_IMAGES:  # <-- AGREGAR "and GENERATE_IMAGES"
            img_path = os.path.join(test_dir, f"{variant_name}_path.png")
            save_path_visualization(G, path, charger_nodes, origen, destino, img_path)

    # ---- Greedy ----
    metrics_g, path_g = run_greedy(G, charger_nodes, origen, destino)
    test_result["algorithms"].append(metrics_g)

    if path_g is not None and GENERATE_IMAGES:  # <-- AGREGAR "and GENERATE_IMAGES"
        img_path_g = os.path.join(test_dir, f"{GREEDY_NAME}_path.png")
        save_path_visualization(G, path_g, charger_nodes, origen, destino, img_path_g)

    return test_result


def main():
    print("=" * 80)
    print("BENCHMARK: A* (3 heurísticas) vs Greedy con Gestión de Batería")
    print("=" * 80)

    # Directorio de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", "benchmark_heuristicas", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Cargar grafo
    with Halo(text="Cargando grafo de Montevideo...", spinner=DOTS_SPINNER):
        G = load_graph("Montevideo, Uruguay", gamma=GAMMA)
    print(f"Grafo cargado: {len(G.nodes)} nodos")

    # Cargar cargadores
    charger_nodes, _ = get_charger_nodes(G)
    print(f"Cargadores del JSON: {len(charger_nodes)}")

    origen_fijo = "Ciudad Vieja"
    if origen_fijo not in MONTEVIDEO_BARRIOS:
        raise ValueError(
            f"El barrio de origen fijo '{origen_fijo}' no existe en MONTEVIDEO_BARRIOS."
        )

    tests = [
        (origen_fijo, barrio)
        for barrio in MONTEVIDEO_BARRIOS.keys()
        if barrio != origen_fijo
    ]

    all_results: Dict = {
        "config": {
            "GAMMA": GAMMA,
            "MAX_CAPACITY": MAX_CAPACITY,
            "INITIAL_CHARGE": INITIAL_CHARGE,
            "RECHARGE_AMOUNT": RECHARGE_AMOUNT,
            "astar_variants": [
                {"name": name, "heuristic": heur.__name__, "gamma_min": gm}
                for name, heur, gm in ASTAR_VARIANTS
            ],
            "greedy_name": GREEDY_NAME,
        },
        "tests": [],
    }

    print(f"\nEjecutando {len(tests)} tests desde {origen_fijo} a todos los barrios...")

    spinner = Halo(text="Iniciando tests...", spinner=DOTS_SPINNER)
    spinner.start()

    for i, (origen_name, destino_name) in enumerate(tests, 1):
        spinner.text = (
            f"Ejecutando test {i}/{len(tests)}: {origen_name} -> {destino_name}"
        )
        test_result = run_test(
            G, charger_nodes, origen_name, destino_name, i, output_dir
        )
        all_results["tests"].append(test_result)

    spinner.succeed("Todos los tests completados.")

    # Guardar JSON con todos los resultados
    json_path = os.path.join(output_dir, "resultados.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("\nBenchmark completado.")
    print(f"Resultados guardados en: {json_path}")


if __name__ == "__main__":
    main()
