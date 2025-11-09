"""Coordenadas de barrios de Montevideo."""

import osmnx as ox
from typing import Tuple


# Coordenadas (latitud, longitud) de barrios de Montevideo
MONTEVIDEO_BARRIOS = {
    # Zona Centro
    "Ciudad Vieja": (-34.9065, -56.2011),
    "Centro": (-34.9033, -56.1882),
    "Cordón": (-34.9000, -56.1833),
    "Palermo": (-34.9067, -56.1783),
    "Parque Rodó": (-34.9167, -56.1667),
    
    # Zona Este
    "Pocitos": (-34.9091, -56.1629),
    "Punta Carretas": (-34.9180, -56.1587),
    "Carrasco": (-34.8775, -56.0547),
    "Carrasco Norte": (-34.8650, -56.0450),
    "Malvín": (-34.8900, -56.1000),
    "Buceo": (-34.9000, -56.1333),
    
    # Zona Oeste
    "Aguada": (-34.8933, -56.2117),
    "Reducto": (-34.8850, -56.2050),
    "Capurro": (-34.8783, -56.2183),
    "Bella Vista": (-34.8800, -56.1950),
    "Prado": (-34.8650, -56.2100),
    "Atahualpa": (-34.8567, -56.2033),
    
    # Zona Norte
    "La Comercial": (-34.8583, -56.1717),
    "Jacinto Vera": (-34.8817, -56.1883),
    "La Figurita": (-34.8717, -56.1800),
    "Larrañaga": (-34.8633, -56.1750),
    "La Blanqueada": (-34.8850, -56.1650),
    "Tres Cruces": (-34.8933, -56.1667),
    "Unión": (-34.8800, -56.1550),
    "Villa Dolores": (-34.8650, -56.1600),
    
    # Zona Sur
    "Punta Gorda": (-34.9167, -56.0833),
    "Puerto del Buceo": (-34.9050, -56.1200),
    
    # Zona Noroeste
    "Cerro": (-34.8667, -56.2667),
    "La Teja": (-34.8733, -56.2517),
    "Paso de la Arena": (-34.8533, -56.2717),
    "Nuevo París": (-34.8483, -56.2250),
    "Belvedere": (-34.8417, -56.2200),
    "Sayago": (-34.8617, -56.2400),
    
    # Zona Nordeste
    "Ituzaingó": (-34.8500, -56.1400),
    "Flor de Maroñas": (-34.8383, -56.1483),
    "Maroñas": (-34.8333, -56.1333),
    "Villa Española": (-34.8500, -56.1667),
    "Jardines del Hipódromo": (-34.8417, -56.1233),
}


def get_nearest_node(G, barrio_name: str) -> int:
    """
    Encuentra el nodo mas cercano al barrio especificado.
    
    Args:
        G: Grafo de NetworkX
        barrio_name: Nombre del barrio
        
    Returns:
        ID del nodo mas cercano a las coordenadas del barrio
        
    Raises:
        KeyError: Si el barrio no existe en el diccionario
    """
    if barrio_name not in MONTEVIDEO_BARRIOS:
        raise KeyError(f"Barrio '{barrio_name}' no encontrado. "
                      f"Barrios disponibles: {list(MONTEVIDEO_BARRIOS.keys())}")
    
    lat, lon = MONTEVIDEO_BARRIOS[barrio_name]
    node_id = ox.nearest_nodes(G, lon, lat)
    return node_id


def list_barrios() -> list:
    """Retorna lista de barrios disponibles ordenados alfabeticamente."""
    return sorted(MONTEVIDEO_BARRIOS.keys())


def get_barrio_coords(barrio_name: str) -> Tuple[float, float]:
    """
    Obtiene las coordenadas de un barrio.
    
    Args:
        barrio_name: Nombre del barrio
        
    Returns:
        Tupla (latitud, longitud)
    """
    return MONTEVIDEO_BARRIOS[barrio_name]

