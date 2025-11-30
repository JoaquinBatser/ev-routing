"""
Punto de entrada principal del proyecto EV Routing.
Ejecuta este archivo para acceder a todas las funcionalidades.
"""

import sys
import questionary
import colorama

# Inicializar colorama para soporte de ANSI en Windows
colorama.init()

# Forzar UTF-8 en stdout para que los spinners de Halo se vean bien
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python < 3.7 o entorno limitado


def run_benchmark():
    print("\nEjecutando benchmark completo...\n")
    import benchmark
    benchmark.main()


def run_analysis():
    import os
    print("\nAnalizando resultados...\n")
    
    # Buscar el archivo resultados.json más reciente
    output_dir = "output/benchmark_heuristicas"
    if not os.path.exists(output_dir):
        print("No se encontró la carpeta de resultados.")
        print("   Primero ejecuta el benchmark (opción 1).")
        return
    
    # Buscar subdirectorios ordenados por fecha
    subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    if not subdirs:
        print("No hay resultados para analizar.")
        return
    
    subdirs.sort(reverse=True)
    latest_dir = os.path.join(output_dir, subdirs[0])
    resultados_path = os.path.join(latest_dir, "resultados.json")
    
    if not os.path.exists(resultados_path):
        print(f"No se encontró {resultados_path}")
        return
    
    print(f"Usando resultados desde: {latest_dir}\n")
    
    import analizar_resultados
    sys.argv = ["analizar_resultados.py", resultados_path]
    analizar_resultados.main()


def run_battery_test():
    print("\nEjecutando test de visualización...\n")
    import test_battery_colors


def main():
    print("=" * 80)
    print("SISTEMA DE ROUTING PARA VEHÍCULOS ELÉCTRICOS")
    print("=" * 80)

    while True:
        choice = questionary.select(
            "Selecciona una opción:",
            choices=[
                "Ejecutar benchmark completo (A* vs Greedy)",
                "Analizar resultados existentes",
                "Test de visualización con colores de batería",
                "Salir"
            ]
        ).ask()
        
        if choice == "Ejecutar benchmark completo (A* vs Greedy)":
            run_benchmark()
        elif choice == "Analizar resultados existentes":
            run_analysis()
        elif choice == "Test de visualización con colores de batería":
            run_battery_test()
        elif choice == "Salir":
            print("\n¡Hasta luego!\n")
            break
        
        # Pausa para que el usuario pueda leer el output antes de limpiar o volver al menú


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido. ¡Hasta luego!\n")