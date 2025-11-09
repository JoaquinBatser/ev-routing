"""Visualizador de mapas sin ejecutar algoritmos.

Este script permite cargar y visualizar el mapa de Uruguay con:
- Nodos de origen y destino
- Cargadores eléctricos (opcional)
- Sin ejecutar algoritmos de búsqueda
"""

import random
import os
import questionary
from graph.graph_setup import load_graph
from graph.uruguay_cities import get_nearest_node as get_nearest_city_node, list_cities
from graph.montevideo_barrios import get_nearest_node as get_nearest_barrio_node, list_barrios
from graph.chargers_loader import get_charger_nodes
from visualization.styles import style_unvisited_edge
from visualization.plotting import plot_graph


def main():
    print("=" * 60)
    print("  VISUALIZADOR DE MAPAS - Sin Algoritmos")
    print("=" * 60)
    
    # Seleccionar área a cargar
    area_choice = questionary.select(
        "\nQue area del mapa quieres cargar?",
        choices=[
            "Uruguay completo (mas lento, ~2-5 min primera vez)",
            "Montevideo (rapido, ideal para testing)"
        ],
    ).ask()
    
    if not area_choice:
        print("Operacion cancelada.")
        return
    
    # Determinar el lugar a cargar
    if "Uruguay completo" in area_choice:
        place_name = "Uruguay"
    else:
        place_name = "Montevideo, Uruguay"
    
    # Cargar el grafo
    print(f"\nCargando grafo de {place_name}...")
    G = load_graph(place_name)
    print("Grafo cargado.\n")
    
    # Seleccionar si incluir cargadores
    include_chargers = questionary.confirm(
        "Incluir cargadores electricos en el mapa?",
        default=True
    ).ask()
    
    charger_nodes = []
    charger_info = {}
    
    if include_chargers:
        # Preguntar cuántos cargadores
        chargers_amount_str = questionary.text(
            "Cuantos cargadores mostrar? (Enter para todos)",
            default="20"
        ).ask()
        
        try:
            chargers_amount = int(chargers_amount_str) if chargers_amount_str else None
        except ValueError:
            chargers_amount = 20
        
        # Cargar cargadores
        try:
            print(f"\nCargando cargadores electricos...")
            charger_nodes, charger_info = get_charger_nodes(G, max_chargers=chargers_amount)
            print(f"Se cargaron {len(charger_nodes)} cargadores")
        except Exception as e:
            print(f"Error al cargar cargadores: {e}")
            charger_nodes = []
    
    # Seleccionar modo de selección de nodos
    node_selection_mode = questionary.select(
        "\nComo seleccionar origen y destino?",
        choices=["Ciudades de Uruguay", "Nodos aleatorios", "Sin origen/destino"],
    ).ask()
    
    if not node_selection_mode:
        print("Operacion cancelada.")
        return
    
    start = None
    end = None
    
    if node_selection_mode == "Ciudades de Uruguay":
        # Determinar si usar barrios de Montevideo o ciudades de Uruguay
        if "Montevideo" in place_name and place_name != "Uruguay":
            # Usar barrios de Montevideo
            locations = list_barrios()
            location_type = "barrio"
            print("\nUsando barrios de Montevideo")
        else:
            # Usar ciudades de Uruguay
            locations = list_cities()
            location_type = "ciudad"
            print("\nUsando ciudades de Uruguay")
        
        # Seleccionar origen
        origin_location = questionary.select(
            f"\nSelecciona el {location_type} de ORIGEN:",
            choices=locations,
        ).ask()
        
        if not origin_location:
            print("Operacion cancelada.")
            return
        
        # Seleccionar destino
        dest_location = questionary.select(
            f"\nSelecciona el {location_type} de DESTINO:",
            choices=locations,
        ).ask()
        
        if not dest_location:
            print("Operacion cancelada.")
            return
        
        # Obtener nodos más cercanos
        try:
            if location_type == "barrio":
                start = get_nearest_barrio_node(G, origin_location)
                end = get_nearest_barrio_node(G, dest_location)
            else:
                start = get_nearest_city_node(G, origin_location)
                end = get_nearest_city_node(G, dest_location)
            
            print(f"\nOrigen: {origin_location} (nodo {start})")
            print(f"Destino: {dest_location} (nodo {end})")
        except Exception as e:
            print(f"Error al encontrar nodos: {e}")
            return
    
    elif node_selection_mode == "Nodos aleatorios":
        # Seleccionar nodos aleatorios
        start = random.choice(list(G.nodes))
        end = random.choice(list(G.nodes))
        print(f"\nNodo de inicio: {start}")
        print(f"Nodo de destino: {end}")
    
    # Excluir origen y destino de los cargadores si están presentes
    if start and end and charger_nodes:
        charger_nodes = [n for n in charger_nodes if n != start and n != end]
    
    # Inicializar visualización del grafo
    print("\nPreparando visualizacion...")
    
    # Inicializar todos los nodos
    for node in G.nodes:
        G.nodes[node]["size"] = 0
        G.nodes[node]["is_start"] = False
        G.nodes[node]["is_end"] = False
        G.nodes[node]["is_charger"] = False
        G.nodes[node]["charger_visited"] = False
        G.nodes[node]["on_path"] = False
        G.nodes[node]["visited"] = False
    
    # Marcar origen y destino
    if start:
        G.nodes[start]["size"] = 50
        G.nodes[start]["is_start"] = True
    
    if end:
        G.nodes[end]["size"] = 50
        G.nodes[end]["is_end"] = True
    
    # Marcar cargadores
    for node in charger_nodes:
        G.nodes[node]["is_charger"] = True
        G.nodes[node]["size"] = 15
    
    # Estilizar todas las aristas como no visitadas
    for edge in G.edges:
        style_unvisited_edge(G, edge)
    
    # Directorio de salida
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generar nombre de archivo
    area_name = "uruguay" if "Uruguay completo" in area_choice else "montevideo"
    chargers_suffix = "_con_cargadores" if include_chargers else ""
    nodes_suffix = ""
    if start and end:
        nodes_suffix = "_con_nodos"
    
    filename = f"mapa_{area_name}{chargers_suffix}{nodes_suffix}.png"
    save_path = os.path.join(output_dir, filename)
    
    # Visualizar
    print("\nGenerando visualizacion de alta calidad...")
    plot_graph(G, save_path=save_path, high_quality=True)
    print(f"Imagen guardada en: {save_path}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print(f"Area: {place_name}")
    print(f"Nodos totales: {len(G.nodes)}")
    print(f"Aristas totales: {len(G.edges)}")
    if include_chargers:
        print(f"Cargadores mostrados: {len(charger_nodes)}")
    if start and end:
        print(f"Origen: {start}")
        print(f"Destino: {end}")
    print("=" * 60)
    print("\nColores:")
    print("  Azul = Origen")
    print("  Rojo = Destino")
    if include_chargers:
        print("  Morado = Cargadores")
    print("  Gris = Nodos normales")
    print("=" * 60)


if __name__ == "__main__":
    main()

