from graph.graph_setup import load_graph
from graph.chargers_loader import get_charger_nodes
from graph.montevideo_barrios import get_nearest_node
from algorithms.astar_battery_core import astar_battery
from visualization.plotting import plot_graph
from visualization.styles import style_unvisited_edge, style_path_edge_with_battery
import os
from datetime import datetime
import copy

GAMMA = 1.2
MAX_CAPACITY = 5.0
INITIAL_CHARGE = 5.0     # kWh - Comenzar con batería llena
RECHARGE_AMOUNT = 4.5    # kWh - Recarga casi completa

print("=" * 80)
print("TEST DE VISUALIZACION: Path con colores segun bateria")
print("=" * 80)
print("\nColores:")
print("  VERDE:    > 66% bateria")
print("  AMARILLO: 33-66% bateria")
print("  ROJO:     < 33% bateria")
print()

# Cargar grafo
print("Cargando grafo...")
G = load_graph("Montevideo, Uruguay", gamma=GAMMA)
print(f"OK Grafo cargado: {len(G.nodes)} nodos")

# Cargar cargadores
charger_nodes, _ = get_charger_nodes(G)
print(f"OK Cargadores: {len(charger_nodes)}")

# Ejecutar A* desde Ciudad Vieja hasta Pocitos
origen_node = get_nearest_node(G, "Ciudad Vieja")
destino_node = get_nearest_node(G, "Pocitos")

print(f"\nEjecutando A* desde Ciudad Vieja a Pocitos...")
result = astar_battery(
    G,
    origen_node,
    destino_node,
    max_capacity=MAX_CAPACITY,
    initial_charge=INITIAL_CHARGE,
    gamma_min=GAMMA,
    charger_nodes=charger_nodes,
    recharge_amount=RECHARGE_AMOUNT,
    return_battery_info=True,
)

if result:
    path_with_battery, energy, nodes, recharges, time_exec = result
    print(f"OK Camino encontrado!")
    print(f"  Energia: {energy:.2f} kWh")
    print(f"  Nodos expandidos: {nodes}")
    print(f"  Recargas: {recharges}")
    print(f"  Tiempo: {time_exec:.4f}s")

    # Visualizar con colores de bateria
    print("\nGenerando visualizacion con colores de bateria...")

    # Copiar grafo
    G_vis = copy.deepcopy(G)

    # Inicializar propiedades
    for node in G_vis.nodes:
        G_vis.nodes[node]["size"] = 0
        G_vis.nodes[node]["on_path"] = False
        G_vis.nodes[node]["is_start"] = False
        G_vis.nodes[node]["is_end"] = False
        G_vis.nodes[node]["is_charger"] = False
        G_vis.nodes[node]["charger_visited"] = False

    # Marcar cargadores
    charger_set = set(charger_nodes)
    for node in charger_nodes:
        if node in G_vis.nodes:
            G_vis.nodes[node]["is_charger"] = True
            G_vis.nodes[node]["size"] = 50

    # Inicializar edges
    for edge in G_vis.edges:
        style_unvisited_edge(G_vis, edge)

    # Extraer solo los nodos del path para la visualización
    path_nodes = [node for node, _, _ in path_with_battery]
    
    # Marcar origen y destino
    G_vis.nodes[path_nodes[0]]["is_start"] = True
    G_vis.nodes[path_nodes[0]]["size"] = 100
    G_vis.nodes[path_nodes[-1]]["is_end"] = True
    G_vis.nodes[path_nodes[-1]]["size"] = 100

    # Usar la informacion REAL de bateria del algoritmo A*
    print("\nNivel de bateria a lo largo del path (segun A*):")
    
    # Validación y coloreo
    battery_went_negative = False
    
    for i in range(len(path_with_battery) - 1):
        node, battery, recharged = path_with_battery[i]
        next_node, next_battery, _ = path_with_battery[i + 1]
        
        G_vis.nodes[node]["on_path"] = True
        
        # Si hubo recarga en este nodo
        if recharged:
            G_vis.nodes[node]["charger_visited"] = True
            G_vis.nodes[node]["size"] = 80
            print(f"    [*] Recarga en nodo {node}: bateria restaurada")
        
        # Calcular porcentaje de batería ACTUAL
        battery_percent = (battery / MAX_CAPACITY) * 100
        
        # VALIDACION: Detectar bateria negativa
        if battery < 0:
            print(f"  [!] ERROR en segmento {i + 1}: Bateria NEGATIVA ({battery:.2f} kWh, {battery_percent:.1f}%)")
            battery_went_negative = True
            color_txt = "🔴"
        elif battery_percent > 66:
            color_txt = "🟢"
        elif battery_percent > 33:
            color_txt = "🟡"
        else:
            color_txt = "🔴"
        
        print(f"  Segmento {i + 1}: {battery_percent:.1f}% ({battery:.2f} kWh) [{color_txt}]")
        
        # Colorear edge si existe
        if next_node in path_nodes:
            try:
                edge = (node, next_node, 0)
                if G_vis.has_edge(node, next_node):
                    style_path_edge_with_battery(G_vis, edge, max(0, battery_percent))
            except:
                pass  # Si no existe el edge, continuar
    
    # Marcar el último nodo
    last_node, last_battery, last_recharged = path_with_battery[-1]
    G_vis.nodes[last_node]["on_path"] = True
    if last_recharged:
        G_vis.nodes[last_node]["charger_visited"] = True
        G_vis.nodes[last_node]["size"] = 80
    
    # Mostrar advertencia si hubo problema
    if battery_went_negative:
        print("\n" + "="*80)
        print("[!] ADVERTENCIA: Se detecto bateria NEGATIVA en el camino.")
        print("    Esto indica que los parametros no son suficientes para este recorrido.")
        print("    Sugerencias:")
        print("    - Aumentar MAX_CAPACITY")
        print("    - Aumentar RECHARGE_AMOUNT")
        print("    - Reducir GAMMA (consumo por km)")
        print("    - Agregar mas estaciones de carga")
        print("="*80 + "\n")

    # Guardar visualización
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", "test_battery_colors", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "path_battery_colors.png")

    plot_graph(G_vis, has_chargers=True, save_path=output_file, high_quality=True)

    print(f"\nOK Visualizacion guardada en: {output_file}")
    print("\nAbre la imagen para ver el path con colores segun bateria!")
else:
    print("[X] No se encontro camino")

print("\n" + "=" * 80)
print("TEST COMPLETADO")
print("=" * 80)