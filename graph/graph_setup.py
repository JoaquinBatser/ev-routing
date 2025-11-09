"""Configuración y carga del grafo de OpenStreetMap."""
import osmnx as ox


def load_graph(place_name="Uruguay"):
    """
    Carga y limpia el grafo de OpenStreetMap.
    
    Args:
        place_name: Nombre del lugar a cargar (por defecto "Uruguay")
        
    Returns:
        Grafo de NetworkX con pesos calculados
        
    Nota: 
        - "Uruguay" carga todo el país (puede tardar unos minutos)
        - "Ciudad Vieja, Montevideo, Uruguay" carga solo un barrio (más rápido para testing)
    """
    print(f"Cargando mapa de: {place_name}...")
    G = ox.graph_from_place(place_name, network_type="drive")
    
    # Limpiar y calcular pesos
    for edge in G.edges:
        # Limpiar el atributo "maxspeed"
        maxspeed = 40
        if "maxspeed" in G.edges[edge]:
            maxspeed = G.edges[edge]["maxspeed"]
            if type(maxspeed) == list:
                speeds = [int(speed) for speed in maxspeed]
                maxspeed = min(speeds)
            elif type(maxspeed) == str:
                maxspeed = int(maxspeed)
        G.edges[edge]["maxspeed"] = maxspeed
        # Agregar el atributo "weight" (tiempo = distancia / velocidad)
        G.edges[edge]["weight"] = G.edges[edge]["length"] / maxspeed
    
    return G

