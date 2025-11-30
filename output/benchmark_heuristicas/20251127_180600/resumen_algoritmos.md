# Tabla 1: Resumen General por Algoritmo

| Algoritmo | Tests | Energía (kWh) | Nodos exp. | Recargas | Tiempo (s) | Path len. | Speedup nodos | Speedup tiempo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| astar_euclidean | 34 | 6.89 | 153610 | 0.97 | 5.9779 | 75.4 | 1.00 | 1.00 |
| astar_manhattan | 34 | 6.89 | 153269 | 0.97 | 5.6861 | 75.4 | 1.00 | 1.05 |
| astar_octile | 34 | 6.89 | 153542 | 0.97 | 5.6593 | 75.4 | 1.00 | 1.06 |
| greedy | 34 | 9.31 | 4125 | 1.32 | 0.0981 | 88.2 | 37.24 | 60.91 |


# Tabla 2: Comparación de Medianas

| Algoritmo | Mediana Energía (kWh) | Mediana Nodos | Mediana Tiempo (s) |
| --- | --- | --- | --- |
| astar_euclidean | 6.58 | 137188 | 5.1082 |
| astar_manhattan | 6.58 | 136670 | 5.4304 |
| astar_octile | 6.58 | 137104 | 5.1839 |
| greedy | 9.25 | 1985 | 0.0475 |


# Tabla 3: Mejor y Peor Caso por Energía Consumida

| Algoritmo | Mejor (kWh) | Destino Mejor | Peor (kWh) | Destino Peor |
| --- | --- | --- | --- | --- |
| astar_euclidean | 0.71 | Aguada | 13.28 | Paso de la Arena |
| astar_manhattan | 0.71 | Aguada | 13.28 | Paso de la Arena |
| astar_octile | 0.71 | Aguada | 13.28 | Paso de la Arena |
| greedy | 0.72 | Aguada | 19.36 | Maroñas |


# Tabla 4: Mejor y Peor Caso por Tiempo de Ejecución

| Algoritmo | Mejor (s) | Destino Mejor | Peor (s) | Destino Peor |
| --- | --- | --- | --- | --- |
| astar_euclidean | 0.0035 | Aguada | 18.5730 | Paso de la Arena |
| astar_manhattan | 0.0035 | Aguada | 15.0498 | Cerro |
| astar_octile | 0.0031 | Aguada | 14.8599 | Cerro |
| greedy | 0.0002 | Aguada | 0.4365 | Paso de la Arena |


# Tabla 5: Análisis de Recargas

| Algoritmo | Total Recargas | Tests con Recarga | % Tests con Recarga |
| --- | --- | --- | --- |
| astar_euclidean | 33 | 21 | 61.8% |
| astar_manhattan | 33 | 21 | 61.8% |
| astar_octile | 33 | 21 | 61.8% |
| greedy | 45 | 24 | 70.6% |


# Tabla 6: Top 10 Destinos Más Lejanos - Comparación de Algoritmos

| Destino | A* Euclidean (nodos) | A* Manhattan (nodos) | A* Octile (nodos) | Greedy (nodos) |
| --- | --- | --- | --- | --- |
| Maroñas | 324133 | 323437 | 323942 | 14573 |
| Jardines del Hipódromo | 299075 | 298669 | 298938 | 4886 |
| Malvín | 268156 | 267794 | 268105 | 6090 |
| Flor de Maroñas | 276198 | 275921 | 276161 | 6423 |
| Ituzaingó | 264234 | 264074 | 264205 | 10236 |
| Villa Española | 228136 | 227706 | 228091 | 1612 |
| Belvedere | 260927 | 260594 | 260823 | 18052 |
| Paso de la Arena | 346237 | 346060 | 346178 | 20937 |
| Puerto del Buceo | 188629 | 187613 | 188515 | 5006 |
| Villa Dolores | 172007 | 171599 | 171927 | 5924 |


# Tabla 7: Eficiencia Energética (kWh por nodo del path)

| Algoritmo | Media kWh/nodo | Mediana kWh/nodo | Min | Max |
| --- | --- | --- | --- | --- |
| astar_euclidean | 0.091 | 0.087 | 0.066 | 0.170 |
| astar_manhattan | 0.091 | 0.087 | 0.066 | 0.170 |
| astar_octile | 0.091 | 0.087 | 0.066 | 0.170 |
| greedy | 0.108 | 0.096 | 0.071 | 0.170 |


# Tabla 8: Throughput (Nodos Expandidos por Segundo)

| Algoritmo | Media nodos/s | Mediana nodos/s | Min | Max |
| --- | --- | --- | --- | --- |
| astar_euclidean | 29287 | 28054 | 18642 | 47070 |
| astar_manhattan | 30313 | 30934 | 17671 | 47301 |
| astar_octile | 30703 | 30336 | 19973 | 45481 |
| greedy | 44303 | 42590 | 20051 | 70243 |


# Tabla 9: Comparación Detallada entre Heurísticas de A*

| Métrica | Euclidean | Manhattan | Octile |
| --- | --- | --- | --- |
| Nodos expandidos (media) | 153610 | 153269 | 153542 |
| Tiempo (media, s) | 5.9779 | 5.6861 | 5.6593 |
| Energía (media, kWh) | 6.89 | 6.89 | 6.89 |
| Recargas (media) | 0.97 | 0.97 | 0.97 |


# Tabla 10: A* vs Greedy - Trade-offs

| Métrica | A* Euclidean | Greedy | Diferencia | % Cambio |
| --- | --- | --- | --- | --- |
| Nodos expandidos | 153610 | 4125 | -149485 | -97.3% |
| Tiempo (s) | 5.9779 | 0.0981 | -5.8798 | -98.4% |
| Energía (kWh) | 6.89 | 9.31 | 2.42 | +35.1% |
| Longitud path | 75.4 | 88.2 | 12.8 | +17.0% |
| Recargas | 0.97 | 1.32 | 0.35 | +36.4% |