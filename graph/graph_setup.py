"""Configuración y carga del grafo de OpenStreetMap."""

import osmnx as ox


def load_graph(place_name="Uruguay", gamma=2.5):
    """
    Carga y limpia el grafo de OpenStreetMap.

    Args:
        place_name: Nombre del lugar a cargar (por defecto "Uruguay")
        gamma: Coeficiente de consumo de energía por kilómetro (por defecto 2.5 kWh/km)

    Returns:
        Grafo de NetworkX con pesos calculados

    Nota:
        - "Uruguay" carga todo el país (puede tardar unos minutos)
        - "Ciudad Vieja, Montevideo, Uruguay" carga solo un barrio (más rápido para testing)
    """
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

        # gamma en Wh/m (2.5 Wh/m = 2.5 kWh/km)
        distance_km = G.edges[edge]["length"] / 1000  # convertir metros a km
        G.edges[edge]["energy_cost"] = gamma * distance_km  # kWh

    return G
