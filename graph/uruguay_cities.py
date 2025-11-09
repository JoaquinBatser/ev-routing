"""Coordenadas de ciudades principales de Uruguay."""

import osmnx as ox
from typing import Tuple

# Coordenadas (latitud, longitud) de ciudades principales de Uruguay
URUGUAY_CITIES = {
    # Montevideo y área metropolitana
    "Montevideo": (-34.9011, -56.1645),
    "Ciudad Vieja": (-34.9065, -56.2011),
    "Pocitos": (-34.9091, -56.1629),
    "Carrasco": (-34.8775, -56.0547),
    "Punta Carretas": (-34.9180, -56.1587),
    
    # Costa de Oro y Este
    "Punta del Este": (-34.9486, -54.9463),
    "Maldonado": (-34.9000, -54.9500),
    "La Paloma": (-34.6654, -54.1631),
    "Piriápolis": (-34.8667, -55.2750),
    "Atlántida": (-34.7778, -55.7583),
    "La Floresta": (-34.8000, -55.3000),
    "Rocha": (-34.4833, -54.3333),
    
    # Canelones
    "Canelones": (-34.5333, -56.2833),
    "Las Piedras": (-34.7300, -56.2200),
    "Pando": (-34.7167, -55.9583),
    "Santa Lucía": (-34.4533, -56.3900),
    
    # Sur y Suroeste
    "Colonia": (-34.4651, -57.8401),
    "Carmelo": (-34.0000, -58.2833),
    "Nueva Palmira": (-33.8833, -58.4167),
    "Mercedes": (-33.2525, -58.0303),
    
    # Litoral (Oeste)
    "Fray Bentos": (-33.1167, -58.3000),
    "Paysandú": (-32.3167, -58.0833),
    "Salto": (-31.3833, -57.9667),
    "Bella Unión": (-30.2667, -57.6000),
    
    # Centro
    "Durazno": (-33.3833, -56.5167),
    "Trinidad": (-33.5167, -56.8833),
    "Florida": (-34.1000, -56.2167),
    "San José": (-34.3378, -56.7136),
    
    # Norte y Noreste
    "Tacuarembó": (-31.7167, -55.9833),
    "Rivera": (-30.9000, -55.5500),
    "Melo": (-32.3667, -54.1667),
    "Treinta y Tres": (-33.2333, -54.3833),
    
    # Este
    "Chuy": (-33.6833, -53.4500),
}


def get_nearest_node(G, city_name: str) -> int:
    """
    Encuentra el nodo más cercano a la ciudad especificada.
    
    Args:
        G: Grafo de NetworkX
        city_name: Nombre de la ciudad
        
    Returns:
        ID del nodo más cercano a las coordenadas de la ciudad
        
    Raises:
        KeyError: Si la ciudad no existe en el diccionario
    """
    if city_name not in URUGUAY_CITIES:
        raise KeyError(f"Ciudad '{city_name}' no encontrada. "
                      f"Ciudades disponibles: {list(URUGUAY_CITIES.keys())}")
    
    lat, lon = URUGUAY_CITIES[city_name]
    node_id = ox.nearest_nodes(G, lon, lat)
    return node_id


def get_nearest_node_from_coords(G, lat: float, lon: float) -> int:
    """
    Encuentra el nodo más cercano a coordenadas específicas.
    
    Args:
        G: Grafo de NetworkX
        lat: Latitud
        lon: Longitud
        
    Returns:
        ID del nodo más cercano
    """
    return ox.nearest_nodes(G, lon, lat)


def list_cities() -> list:
    """Retorna lista de ciudades disponibles ordenadas alfabéticamente."""
    return sorted(URUGUAY_CITIES.keys())


def get_city_coords(city_name: str) -> Tuple[float, float]:
    """
    Obtiene las coordenadas de una ciudad.
    
    Args:
        city_name: Nombre de la ciudad
        
    Returns:
        Tupla (latitud, longitud)
    """
    return URUGUAY_CITIES[city_name]

