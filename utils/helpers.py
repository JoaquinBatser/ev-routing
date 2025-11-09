"""Funciones auxiliares."""
import osmnx as ox


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

