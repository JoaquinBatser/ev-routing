"""Reconstrucción del camino encontrado."""

import os
from visualization.styles import style_unvisited_edge, style_path_edge
from visualization.plotting import plot_graph


def reconstruct_path(
    G,
    orig,
    dest,
    plot=False,
    save_dir=None,
    algorithm_name="",
    save_final_image=False,
    final_image_dir=None,
):
    """
    Reconstruye y visualiza el camino encontrado.

    Args:
        G: Grafo de NetworkX
        orig: Nodo origen
        dest: Nodo destino
        plot: Si mostrar el gráfico
        save_dir: Directorio donde guardar la imagen
        algorithm_name: Nombre del algoritmo usado
        save_final_image: Si guardar la imagen final
    """
    for edge in G.edges:
        style_unvisited_edge(G, edge)
    dist = 0
    speeds = []
    curr = dest

    G.nodes[curr]["on_path"] = True

    while curr != orig:
        prev = G.nodes[curr].get("previous")
        if prev is None:
            break
        dist += G.edges[(prev, curr, 0)]["length"]
        speeds.append(G.edges[(prev, curr, 0)]["maxspeed"])
        style_path_edge(G, (prev, curr, 0))

        G.nodes[prev]["on_path"] = True
        # Solo hacer visible el nodo si es un cargador
        if G.nodes[prev].get("is_charger", False):
            G.nodes[prev]["size"] = max(G.nodes[prev].get("size", 0), 15)

        curr = prev
    dist /= 1000
    if plot:
        print(f"Distance: {dist}")
        print(f"Avg. speed: {sum(speeds)/len(speeds)}")
        print(f"Total time: {dist/(sum(speeds)/len(speeds)) * 60}")
        plot_graph(G)
    if save_dir:
        save_path = os.path.join(save_dir, f"{algorithm_name}_path.png")
        plot_graph(G, save_path=save_path)
    if save_final_image:
        save_path = os.path.join(final_image_dir, f"{algorithm_name}_path.png")
        plot_graph(G, save_path=save_path)
