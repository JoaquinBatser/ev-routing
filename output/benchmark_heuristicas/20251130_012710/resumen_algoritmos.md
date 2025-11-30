# Tabla 1: Resumen General por Algoritmo

| Algoritmo | Tests | Energía (kWh) | Nodos exp. | Recargas | Tiempo (s) | Path len. | Speedup nodos | Speedup tiempo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| astar_euclidean | 34 | 8.53 | 145802 | 1.35 | 4.7950 | 80.8 | 1.00 | 1.00 |
| astar_manhattan | 34 | 8.53 | 145487 | 1.35 | 4.6040 | 80.8 | 1.00 | 1.04 |
| astar_octile | 34 | 8.53 | 145736 | 1.35 | 4.6675 | 80.8 | 1.00 | 1.03 |
| greedy | 34 | 10.97 | 4464 | 1.62 | 0.0905 | 92.1 | 32.66 | 52.99 |


# Tabla 2: Comparación de Medianas

| Algoritmo | Mediana Energía (kWh) | Mediana Nodos | Mediana Tiempo (s) |
| --- | --- | --- | --- |
| astar_euclidean | 7.90 | 125655 | 3.7880 |
| astar_manhattan | 7.90 | 125156 | 3.6189 |
| astar_octile | 7.90 | 125566 | 3.7757 |
| greedy | 10.34 | 1598 | 0.0253 |


# Tabla 3: Mejor y Peor Caso por Energía Consumida

| Algoritmo | Mejor (kWh) | Destino Mejor | Peor (kWh) | Destino Peor |
| --- | --- | --- | --- | --- |
| astar_euclidean | 0.85 | Aguada | 16.07 | Paso de la Arena |
| astar_manhattan | 0.85 | Aguada | 16.07 | Paso de la Arena |
| astar_octile | 0.85 | Aguada | 16.07 | Paso de la Arena |
| greedy | 0.86 | Aguada | 22.82 | Paso de la Arena |


# Tabla 4: Mejor y Peor Caso por Tiempo de Ejecución

| Algoritmo | Mejor (s) | Destino Mejor | Peor (s) | Destino Peor |
| --- | --- | --- | --- | --- |
| astar_euclidean | 0.0040 | Aguada | 11.7865 | Jardines del Hipódromo |
| astar_manhattan | 0.0031 | Aguada | 11.8726 | Maroñas |
| astar_octile | 0.0057 | Aguada | 11.5795 | Maroñas |
| greedy | 0.0003 | Aguada | 0.5090 | Paso de la Arena |


# Tabla 5: Análisis de Recargas

| Algoritmo | Total Recargas | Tests con Recarga | % Tests con Recarga |
| --- | --- | --- | --- |
| astar_euclidean | 46 | 23 | 67.6% |
| astar_manhattan | 46 | 23 | 67.6% |
| astar_octile | 46 | 23 | 67.6% |
| greedy | 55 | 26 | 76.5% |


# Tabla 6: Top 10 Destinos Más Lejanos - Comparación de Algoritmos

| Destino | A* Euclidean (nodos) | A* Manhattan (nodos) | A* Octile (nodos) | Greedy (nodos) |
| --- | --- | --- | --- | --- |
| Jardines del Hipódromo | 286256 | 285672 | 286054 | 5568 |
| Maroñas | 307972 | 307453 | 307826 | 6490 |
| Paso de la Arena | 317902 | 317745 | 317848 | 22879 |
| Flor de Maroñas | 258736 | 258352 | 258635 | 6312 |
| Belvedere | 311359 | 310978 | 311291 | 20865 |
| Malvín | 253414 | 253114 | 253332 | 18459 |
| Cerro | 298659 | 298369 | 298569 | 12448 |
| La Teja | 255740 | 255633 | 255701 | 12050 |
| Ituzaingó | 240236 | 240099 | 240196 | 4324 |
| Villa Española | 210149 | 209734 | 210121 | 1202 |


# Tabla 7: Eficiencia Energética (kWh por nodo del path)

| Algoritmo | Media kWh/nodo | Mediana kWh/nodo | Min | Max |
| --- | --- | --- | --- | --- |
| astar_euclidean | 0.105 | 0.104 | 0.079 | 0.204 |
| astar_manhattan | 0.105 | 0.104 | 0.079 | 0.204 |
| astar_octile | 0.105 | 0.104 | 0.079 | 0.204 |
| greedy | 0.120 | 0.110 | 0.085 | 0.204 |


# Tabla 8: Throughput (Nodos Expandidos por Segundo)

| Algoritmo | Media nodos/s | Mediana nodos/s | Min | Max |
| --- | --- | --- | --- | --- |
| astar_euclidean | 33088 | 33000 | 17363 | 51167 |
| astar_manhattan | 34899 | 34847 | 22446 | 51001 |
| astar_octile | 33640 | 33207 | 17745 | 52258 |
| greedy | 52650 | 52378 | 31184 | 78270 |


# Tabla 9: Comparación Detallada entre Heurísticas de A*

| Métrica | Euclidean | Manhattan | Octile |
| --- | --- | --- | --- |
| Nodos expandidos (media) | 145802 | 145487 | 145736 |
| Tiempo (media, s) | 4.7950 | 4.6040 | 4.6675 |
| Energía (media, kWh) | 8.53 | 8.53 | 8.53 |
| Recargas (media) | 1.35 | 1.35 | 1.35 |


# Tabla 10: A* vs Greedy - Trade-offs

| Métrica | A* Euclidean | Greedy | Diferencia | % Cambio |
| --- | --- | --- | --- | --- |
| Nodos expandidos | 145802 | 4464 | -141338 | -96.9% |
| Tiempo (s) | 4.7950 | 0.0905 | -4.7045 | -98.1% |
| Energía (kWh) | 8.53 | 10.97 | 2.44 | +28.6% |
| Longitud path | 80.8 | 92.1 | 11.3 | +14.0% |
| Recargas | 1.35 | 1.62 | 0.26 | +19.6% |