"""Punto de entrada principal del programa."""

import random
import os
import subprocess
import questionary
from graph.graph_setup import load_graph
from graph.uruguay_cities import get_nearest_node as get_nearest_city_node, list_cities
from graph.montevideo_barrios import get_nearest_node as get_nearest_barrio_node, list_barrios
from algorithms.dijkstra import dijkstra
from algorithms.astar import a_star
from algorithms.path_reconstruction import reconstruct_path
from algorithms.dijkstra_ev import dijkstra_ev
from algorithms.astar_ev import a_star_ev


def main():
    print("=" * 60)
    print("  ALGORITMOS DE BUSQUEDA - A* y Dijkstra")
    print("=" * 60)
    # Seleccionar área a cargar
    area_choice = questionary.select(
        "Selecciona el área del mapa a cargar:",
        choices=[
            "Uruguay completo (más lento, ~2-5 min primera vez)",
            "Montevideo (rápido, ideal para testing)"
        ],
    ).ask()
    
    if not area_choice:
        print("Operación cancelada.")
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

    # Seleccionar algoritmo
    algorithm_choice = questionary.select(
        "Selecciona el algoritmo de pathfinding:",
        choices=["A*", "Dijkstra", "Dijkstra EV", "A* EV"],
    ).ask()

    if not algorithm_choice:
        print("Operación cancelada.")
        return

    # Seleccionar modo de selección de nodos
    node_selection_mode = questionary.select(
        "¿Cómo quieres seleccionar los nodos?",
        choices=["Ciudades de Uruguay", "Nodos aleatorios"],
    ).ask()

    if not node_selection_mode:
        print("Operación cancelada.")
        return

    # Seleccionar nodos según el modo elegido
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
            f"Selecciona el {location_type} de ORIGEN:",
            choices=locations,
        ).ask()
        
        if not origin_location:
            print("Operacion cancelada.")
            return
        
        # Seleccionar destino
        dest_location = questionary.select(
            f"Selecciona el {location_type} de DESTINO:",
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
    else:
        # Seleccionar nodos aleatorios
        start = random.choice(list(G.nodes))
        end = random.choice(list(G.nodes))
        print(f"\nNodo de inicio: {start}")
        print(f"Nodo de destino: {end}")

    # Configurar cantidad de cargadores si es algoritmo EV
    chargers_amount = 10  # default
    if "EV" in algorithm_choice:
        print("\n" + "=" * 60)
        print("  CONFIGURACION DE CARGADORES")
        print("=" * 60)
        
        chargers_input = questionary.text(
            "Cuantos cargadores usar? (Enter para todos los disponibles)",
        ).ask()
        
        try:
            chargers_amount = int(chargers_input) if chargers_input else None
        except ValueError:
            chargers_amount = 50
    
    print("\n" + "=" * 60)
    print(f"  EJECUTANDO: {algorithm_choice}")
    print("=" * 60)

    # Determinar nombre del algoritmo antes de preguntar
    match algorithm_choice:
        case "A*":
            algorithm_name = "a_star"
        case "Dijkstra":
            algorithm_name = "dijkstra"
        case "Dijkstra EV":
            algorithm_name = "dijkstra_ev"
        case "A* EV":
            algorithm_name = "a_star_ev"
        case _:
            algorithm_name = "unknown"

    # ¿Guardar frames intermedios?
    print("\n" + "=" * 60)
    print("  CONFIGURACION DE SALIDA")
    print("=" * 60)
    
    guardar_intermedios = questionary.select(
        "Guardar frames intermedios?",
        choices=["No", "Si"],
    ).ask()
    save_frames = guardar_intermedios == "Si"

    # Directorio de frames
    save_dir = os.path.join("frames", algorithm_name)
    os.makedirs(save_dir, exist_ok=True)
    
    # Directorio para la imagen final del PATH
    final_image_dir = "output"
    os.makedirs(final_image_dir, exist_ok=True)
    
    if save_frames:
        print(f"\nFrames intermedios: {save_dir}/")
    print(f"Imagen final: {final_image_dir}/")

    # Ejecutar algoritmo seleccionado
    match algorithm_choice:
        case "A*":
            a_star(
                G,
                start,
                end,
                plot=False,
                save_dir=save_dir,
                algorithm_name=algorithm_name,
                save_frames=save_frames,
            )
        case "Dijkstra":
            dijkstra(
                G,
                start,
                end,
                plot=False,
                save_dir=save_dir,
                algorithm_name=algorithm_name,
                save_frames=save_frames,
            )
        case "Dijkstra EV":
            dijkstra_ev(
                G,
                start,
                end,
                chargers_amount=chargers_amount,
                plot=False,
                save_dir=save_dir,
                algorithm_name=algorithm_name,
                save_frames=save_frames,
            )
        case "A* EV":
            a_star_ev(
                G,
                start,
                end,
                chargers_amount=chargers_amount,
                plot=False,
                save_dir=save_dir,
                algorithm_name=algorithm_name,
                save_frames=save_frames,
            )
        case _:
            print("Algoritmo no válido.")
            return

    # Reconstruir y guardar la imagen final del camino
    print("\n" + "=" * 60)
    print("  RECONSTRUCCION DEL CAMINO")
    print("=" * 60)
    
    reconstruct_path(
        G,
        start,
        end,
        plot=False,
        save_dir=save_dir,
        algorithm_name=algorithm_name,
        final_image_dir=final_image_dir,
        save_final_image=True,
    )

    final_path = os.path.join(final_image_dir, f"{algorithm_name}_path.png")
    print(f"\nImagen final guardada: {final_path}")

    if save_frames:
        print(f"Frames guardados: {save_dir}/")
        
        # Crear video opcional
        print("\n" + "=" * 60)
        print("  GENERACION DE VIDEO")
        print("=" * 60)
        
        make_video = questionary.confirm("Crear video de las animaciones?").ask()
        if make_video:
            video_dir = "videos"
            os.makedirs(video_dir, exist_ok=True)
            
            input_pattern = os.path.join(save_dir, f"{algorithm_name}_frame_%05d.png")
            output_file = os.path.join(video_dir, f"{algorithm_name}.mp4")
            
            print(f"\nCreando video: {output_file}")
            subprocess.run(
                [
                    "ffmpeg",
                    "-framerate",
                    "10",
                    "-i",
                    input_pattern,
                    "-vf",
                    "scale=958:702",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    output_file,
                ]
            )
            print(f"Video creado: {output_file}")
    
    print("\n" + "=" * 60)
    print("  PROCESO COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
