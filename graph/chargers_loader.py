"""Carga de cargadores eléctricos reales de Uruguay desde JSON."""

import json
import osmnx as ox
from pathlib import Path


def load_chargers_from_json(json_path="cargadores.json"):
    """
    Carga los cargadores eléctricos desde el archivo JSON.
    
    Args:
        json_path: Ruta al archivo JSON con los cargadores
        
    Returns:
        Lista de diccionarios con información de cada cargador
    """
    json_file = Path(json_path)
    
    if not json_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo {json_path}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('data', [])


def get_charger_nodes(G, json_path="cargadores.json", max_chargers=None, verbose=False):
    """
    Obtiene los nodos del grafo más cercanos a los cargadores reales.
    
    Args:
        G: Grafo de NetworkX
        json_path: Ruta al archivo JSON con los cargadores
        max_chargers: Número máximo de cargadores a usar (None = todos)
        verbose: Si True, imprime información de progreso
        
    Returns:
        Tupla (charger_nodes, charger_info)
        - charger_nodes: Lista de IDs de nodos
        - charger_info: Diccionario {node_id: info_cargador}
    """
    chargers = load_chargers_from_json(json_path)
    
    if max_chargers:
        chargers = chargers[:max_chargers]
    
    charger_nodes = []
    charger_info = {}
    
    if verbose:
        print(f"Encontrando nodos para {len(chargers)} cargadores reales...")
    
    for charger in chargers:
        try:
            lat = charger['lat']
            lng = charger['lng']
            
            # Encontrar el nodo más cercano
            node_id = ox.nearest_nodes(G, lng, lat)
            
            # Evitar duplicados (si dos cargadores mapean al mismo nodo)
            if node_id not in charger_nodes:
                charger_nodes.append(node_id)
                charger_info[node_id] = {
                    'name': charger.get('name', 'Sin nombre'),
                    'address': charger.get('address', 'Sin dirección'),
                    'city': charger.get('city', 'Desconocida'),
                    'department': charger.get('department', 'Desconocido'),
                    'status': charger.get('status', 'Desconocido'),
                    'lat': lat,
                    'lng': lng,
                    'connectors': charger.get('connectorStatusAcc', [])
                }
        except Exception:
            # Silenciosamente continuar si hay error con un cargador
            continue
    
    if verbose:
        print(f"✅ Se encontraron {len(charger_nodes)} cargadores en el grafo")
    
    return charger_nodes, charger_info


def get_chargers_by_department(chargers, department):
    """
    Filtra cargadores por departamento.
    
    Args:
        chargers: Lista de cargadores
        department: Nombre del departamento (ej: "Montevideo", "Maldonado")
        
    Returns:
        Lista de cargadores filtrados
    """
    return [c for c in chargers if c.get('department', '').lower() == department.lower()]


def get_available_chargers(chargers):
    """
    Filtra solo los cargadores disponibles (no ocupados).
    
    Args:
        chargers: Lista de cargadores
        
    Returns:
        Lista de cargadores disponibles
    """
    available_statuses = ['Disponible', 'Available', 'Libre']
    return [c for c in chargers 
            if c.get('status', '').lower() in [s.lower() for s in available_statuses]]


def print_charger_stats(chargers):
    """
    Imprime estadísticas sobre los cargadores.
    
    Args:
        chargers: Lista de cargadores
    """
    total = len(chargers)
    
    # Contar por departamento
    departments = {}
    for c in chargers:
        dept = c.get('department', 'Desconocido')
        departments[dept] = departments.get(dept, 0) + 1
    
    # Contar por status
    statuses = {}
    for c in chargers:
        status = c.get('status', 'Desconocido')
        statuses[status] = statuses.get(status, 0) + 1
    
    print(f"\n📊 Estadísticas de Cargadores:")
    print(f"   Total: {total}")
    print(f"\n   Por Departamento:")
    for dept, count in sorted(departments.items(), key=lambda x: -x[1]):
        print(f"   - {dept}: {count}")
    print(f"\n   Por Estado:")
    for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"   - {status}: {count}")

