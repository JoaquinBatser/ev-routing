import json
import os
import argparse
from statistics import mean, median, stdev
from typing import List, Dict, Any

import matplotlib.pyplot as plt


def load_resultados(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_runs(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convierte el JSON en una lista de filas (test, algoritmo)."""
    rows: List[Dict[str, Any]] = []
    for test in data.get("tests", []):
        test_id = test["test_id"]
        origen = test["origen_name"]
        destino = test["destino_name"]
        for alg in test.get("algorithms", []):
            row = {
                "test_id": test_id,
                "origen": origen,
                "destino": destino,
                "algoritmo": alg["algoritmo"],
                "tipo": alg["tipo"],
                "gamma_min": alg["gamma_min"],
                "energy_kwh": alg["energy_kwh"],
                "nodes_expanded": alg["nodes_expanded"],
                "num_recharges": alg["num_recharges"],
                "time_seconds": alg["time_seconds"],
                "path_length": alg["path_length"],
                "reached_destination": alg["reached_destination"],
            }
            rows.append(row)
    return rows


def group_by_alg(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        alg = r["algoritmo"]
        grouped.setdefault(alg, []).append(r)
    return grouped


def compute_summary_per_algorithm(
    grouped: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """
    Promedios por algoritmo (solo casos donde llegó al destino).
    """
    summary: Dict[str, Dict[str, Any]] = {}
    for alg, runs in grouped.items():
        valid = [r for r in runs if r["reached_destination"]]
        if not valid:
            continue

        summary[alg] = {
            "num_tests": len(valid),
            "mean_energy_kwh": mean(r["energy_kwh"] for r in valid),
            "median_energy_kwh": median(r["energy_kwh"] for r in valid),
            "mean_nodes_expanded": mean(r["nodes_expanded"] for r in valid),
            "median_nodes_expanded": median(r["nodes_expanded"] for r in valid),
            "mean_num_recharges": mean(r["num_recharges"] for r in valid),
            "mean_time_seconds": mean(r["time_seconds"] for r in valid),
            "median_time_seconds": median(r["time_seconds"] for r in valid),
            "mean_path_length": mean(r["path_length"] for r in valid),
        }
    return summary


def add_speedups_vs_baseline(
    summary: Dict[str, Dict[str, Any]], baseline_alg: str = "astar_euclidean"
) -> None:
    """
    Speedup vs baseline en nodos y tiempo.
    """
    if baseline_alg not in summary:
        return

    base_nodes = summary[baseline_alg]["mean_nodes_expanded"]
    base_time = summary[baseline_alg]["mean_time_seconds"]

    for alg, stats in summary.items():
        if alg == baseline_alg:
            stats["speedup_nodes_vs_baseline"] = 1.0
            stats["speedup_time_vs_baseline"] = 1.0
            continue

        nodes = stats["mean_nodes_expanded"]
        time_s = stats["mean_time_seconds"]

        stats["speedup_nodes_vs_baseline"] = (
            base_nodes / nodes if nodes and nodes > 0 else None
        )
        stats["speedup_time_vs_baseline"] = (
            base_time / time_s if time_s and time_s > 0 else None
        )


def format_float(x: Any, decimals: int = 3) -> str:
    if x is None:
        return "-"
    return f"{x:.{decimals}f}"


# ============================================================================
# TABLAS
# ============================================================================


def make_table_1_summary(summary: Dict[str, Dict[str, Any]]) -> str:
    """Tabla 1: Resumen general por algoritmo."""
    headers = [
        "Algoritmo",
        "Tests",
        "Energía (kWh)",
        "Nodos exp.",
        "Recargas",
        "Tiempo (s)",
        "Path len.",
        "Speedup nodos",
        "Speedup tiempo",
    ]

    lines: List[str] = ["# Tabla 1: Resumen General por Algoritmo\n"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for alg in sorted(summary.keys()):
        s = summary[alg]
        row = [
            alg,
            str(s["num_tests"]),
            format_float(s["mean_energy_kwh"], 2),
            format_float(s["mean_nodes_expanded"], 0),
            format_float(s["mean_num_recharges"], 2),
            format_float(s["mean_time_seconds"], 4),
            format_float(s["mean_path_length"], 1),
            format_float(s.get("speedup_nodes_vs_baseline"), 2),
            format_float(s.get("speedup_time_vs_baseline"), 2),
        ]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def make_table_2_median_comparison(summary: Dict[str, Dict[str, Any]]) -> str:
    """Tabla 2: Comparación de medianas."""
    headers = [
        "Algoritmo",
        "Mediana Energía (kWh)",
        "Mediana Nodos",
        "Mediana Tiempo (s)",
    ]

    lines: List[str] = ["\n# Tabla 2: Comparación de Medianas\n"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for alg in sorted(summary.keys()):
        s = summary[alg]
        row = [
            alg,
            format_float(s["median_energy_kwh"], 2),
            format_float(s["median_nodes_expanded"], 0),
            format_float(s["median_time_seconds"], 4),
        ]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def make_table_3_best_worst_energy(rows: List[Dict[str, Any]]) -> str:
    """Tabla 3: Mejor y peor caso por energía."""
    valid = [r for r in rows if r["reached_destination"]]
    
    lines: List[str] = ["\n# Tabla 3: Mejor y Peor Caso por Energía Consumida\n"]
    
    # Por algoritmo
    grouped = group_by_alg(valid)
    
    headers = ["Algoritmo", "Mejor (kWh)", "Destino Mejor", "Peor (kWh)", "Destino Peor"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    for alg in sorted(grouped.keys()):
        runs = grouped[alg]
        best = min(runs, key=lambda x: x["energy_kwh"])
        worst = max(runs, key=lambda x: x["energy_kwh"])
        
        row = [
            alg,
            format_float(best["energy_kwh"], 2),
            best["destino"],
            format_float(worst["energy_kwh"], 2),
            worst["destino"],
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_4_best_worst_time(rows: List[Dict[str, Any]]) -> str:
    """Tabla 4: Mejor y peor caso por tiempo."""
    valid = [r for r in rows if r["reached_destination"]]
    
    lines: List[str] = ["\n# Tabla 4: Mejor y Peor Caso por Tiempo de Ejecución\n"]
    
    grouped = group_by_alg(valid)
    
    headers = ["Algoritmo", "Mejor (s)", "Destino Mejor", "Peor (s)", "Destino Peor"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    for alg in sorted(grouped.keys()):
        runs = grouped[alg]
        best = min(runs, key=lambda x: x["time_seconds"])
        worst = max(runs, key=lambda x: x["time_seconds"])
        
        row = [
            alg,
            format_float(best["time_seconds"], 4),
            best["destino"],
            format_float(worst["time_seconds"], 4),
            worst["destino"],
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_5_recharges_analysis(rows: List[Dict[str, Any]]) -> str:
    """Tabla 5: Análisis de recargas por algoritmo."""
    valid = [r for r in rows if r["reached_destination"]]
    grouped = group_by_alg(valid)
    
    lines: List[str] = ["\n# Tabla 5: Análisis de Recargas\n"]
    
    headers = ["Algoritmo", "Total Recargas", "Tests con Recarga", "% Tests con Recarga"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    for alg in sorted(grouped.keys()):
        runs = grouped[alg]
        total_recharges = sum(r["num_recharges"] for r in runs)
        tests_with_recharge = sum(1 for r in runs if r["num_recharges"] > 0)
        pct = (tests_with_recharge / len(runs) * 100) if runs else 0
        
        row = [
            alg,
            str(int(total_recharges)),
            str(tests_with_recharge),
            f"{pct:.1f}%",
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_6_per_destination(rows: List[Dict[str, Any]]) -> str:
    """Tabla 6: Comparación por destino (top 10 más lejanos)."""
    valid = [r for r in rows if r["reached_destination"]]
    
    # Agrupar por destino
    by_dest: Dict[str, List[Dict]] = {}
    for r in valid:
        by_dest.setdefault(r["destino"], []).append(r)
    
    # Calcular distancia promedio por destino (usando path_length como proxy)
    dest_avg_dist = {}
    for dest, runs in by_dest.items():
        avg_path = mean(r["path_length"] for r in runs)
        dest_avg_dist[dest] = avg_path
    
    # Top 10 más lejanos
    top_10 = sorted(dest_avg_dist.items(), key=lambda x: x[1], reverse=True)[:10]
    
    lines: List[str] = ["\n# Tabla 6: Top 10 Destinos Más Lejanos - Comparación de Algoritmos\n"]
    
    headers = ["Destino", "A* Euclidean (nodos)", "A* Manhattan (nodos)", "A* Octile (nodos)", "Greedy (nodos)"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    for dest, _ in top_10:
        runs = by_dest[dest]
        
        alg_nodes = {}
        for r in runs:
            alg_nodes[r["algoritmo"]] = r["nodes_expanded"]
        
        row = [
            dest,
            format_float(alg_nodes.get("astar_euclidean"), 0),
            format_float(alg_nodes.get("astar_manhattan"), 0),
            format_float(alg_nodes.get("astar_octile"), 0),
            format_float(alg_nodes.get("greedy"), 0),
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_7_efficiency_ratio(rows: List[Dict[str, Any]]) -> str:
    """Tabla 7: Ratio eficiencia (energía / longitud de path)."""
    valid = [r for r in rows if r["reached_destination"]]
    grouped = group_by_alg(valid)
    
    lines: List[str] = ["\n# Tabla 7: Eficiencia Energética (kWh por nodo del path)\n"]
    
    headers = ["Algoritmo", "Media kWh/nodo", "Mediana kWh/nodo", "Min", "Max"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    for alg in sorted(grouped.keys()):
        runs = grouped[alg]
        ratios = [r["energy_kwh"] / r["path_length"] for r in runs if r["path_length"] > 0]
        
        if not ratios:
            continue
        
        row = [
            alg,
            format_float(mean(ratios), 3),
            format_float(median(ratios), 3),
            format_float(min(ratios), 3),
            format_float(max(ratios), 3),
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_8_nodes_per_second(rows: List[Dict[str, Any]]) -> str:
    """Tabla 8: Nodos expandidos por segundo."""
    valid = [r for r in rows if r["reached_destination"]]
    grouped = group_by_alg(valid)
    
    lines: List[str] = ["\n# Tabla 8: Throughput (Nodos Expandidos por Segundo)\n"]
    
    headers = ["Algoritmo", "Media nodos/s", "Mediana nodos/s", "Min", "Max"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    for alg in sorted(grouped.keys()):
        runs = grouped[alg]
        throughputs = [
            r["nodes_expanded"] / r["time_seconds"] 
            for r in runs if r["time_seconds"] > 0
        ]
        
        if not throughputs:
            continue
        
        row = [
            alg,
            format_float(mean(throughputs), 0),
            format_float(median(throughputs), 0),
            format_float(min(throughputs), 0),
            format_float(max(throughputs), 0),
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_9_astar_heuristic_comparison(summary: Dict[str, Dict[str, Any]]) -> str:
    """Tabla 9: Comparación específica entre heurísticas de A*."""
    astar_algs = [alg for alg in summary.keys() if alg.startswith("astar_")]
    
    if len(astar_algs) < 2:
        return "\n# Tabla 9: Comparación Heurísticas A* (no disponible)\n"
    
    lines: List[str] = ["\n# Tabla 9: Comparación Detallada entre Heurísticas de A*\n"]
    
    headers = ["Métrica", "Euclidean", "Manhattan", "Octile"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    metrics = [
        ("Nodos expandidos (media)", "mean_nodes_expanded", 0),
        ("Tiempo (media, s)", "mean_time_seconds", 4),
        ("Energía (media, kWh)", "mean_energy_kwh", 2),
        ("Recargas (media)", "mean_num_recharges", 2),
    ]
    
    for metric_name, metric_key, decimals in metrics:
        row = [metric_name]
        for alg in ["astar_euclidean", "astar_manhattan", "astar_octile"]:
            if alg in summary:
                row.append(format_float(summary[alg].get(metric_key), decimals))
            else:
                row.append("-")
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def make_table_10_astar_vs_greedy(summary: Dict[str, Dict[str, Any]]) -> str:
    """Tabla 10: A* vs Greedy - Trade-offs."""
    lines: List[str] = ["\n# Tabla 10: A* vs Greedy - Trade-offs\n"]
    
    if "astar_euclidean" not in summary or "greedy" not in summary:
        lines.append("Datos insuficientes para comparación.\n")
        return "\n".join(lines)
    
    astar = summary["astar_euclidean"]
    greedy = summary["greedy"]
    
    headers = ["Métrica", "A* Euclidean", "Greedy", "Diferencia", "% Cambio"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    
    comparisons = [
        ("Nodos expandidos", "mean_nodes_expanded", 0),
        ("Tiempo (s)", "mean_time_seconds", 4),
        ("Energía (kWh)", "mean_energy_kwh", 2),
        ("Longitud path", "mean_path_length", 1),
        ("Recargas", "mean_num_recharges", 2),
    ]
    
    for metric_name, metric_key, decimals in comparisons:
        astar_val = astar.get(metric_key, 0)
        greedy_val = greedy.get(metric_key, 0)
        diff = greedy_val - astar_val
        pct_change = ((greedy_val / astar_val - 1) * 100) if astar_val > 0 else 0
        
        row = [
            metric_name,
            format_float(astar_val, decimals),
            format_float(greedy_val, decimals),
            format_float(diff, decimals),
            f"{pct_change:+.1f}%",
        ]
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def save_markdown(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def save_summary_json(path: str, summary: Dict[str, Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


# ============================================================================
# GRÁFICOS
# ============================================================================


def plot_bar_metric(
    summary: Dict[str, Dict[str, Any]],
    metric_key: str,
    ylabel: str,
    title: str,
    save_path: str,
    order: list | None = None,
) -> None:
    """
    Gráfico de barras sencillo de una métrica por algoritmo.
    """
    if order is None:
        algs = sorted(summary.keys())
    else:
        algs = [a for a in order if a in summary]

    values = [summary[a][metric_key] for a in algs]

    plt.figure(figsize=(8, 5))
    plt.bar(algs, values, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_comparison_grid(summary: Dict[str, Dict[str, Any]], save_path: str, order: list) -> None:
    """Gráfico 2x2 comparando múltiples métricas."""
    algs = [a for a in order if a in summary]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Comparación Multicriterio de Algoritmos", fontsize=16)
    
    # Nodos expandidos
    axes[0, 0].bar(algs, [summary[a]["mean_nodes_expanded"] for a in algs])
    axes[0, 0].set_title("Nodos Expandidos (media)")
    axes[0, 0].set_ylabel("Nodos")
    axes[0, 0].tick_params(axis='x', rotation=15)
    
    # Tiempo
    axes[0, 1].bar(algs, [summary[a]["mean_time_seconds"] for a in algs], color="orange")
    axes[0, 1].set_title("Tiempo de Ejecución (media)")
    axes[0, 1].set_ylabel("Segundos")
    axes[0, 1].tick_params(axis='x', rotation=15)
    
    # Energía
    axes[1, 0].bar(algs, [summary[a]["mean_energy_kwh"] for a in algs], color="green")
    axes[1, 0].set_title("Energía Consumida (media)")
    axes[1, 0].set_ylabel("kWh")
    axes[1, 0].tick_params(axis='x', rotation=15)
    
    # Recargas
    axes[1, 1].bar(algs, [summary[a]["mean_num_recharges"] for a in algs], color="red")
    axes[1, 1].set_title("Número de Recargas (media)")
    axes[1, 1].set_ylabel("Recargas")
    axes[1, 1].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_speedup_comparison(summary: Dict[str, Dict[str, Any]], save_path: str, order: list) -> None:
    """Gráfico de speedups vs baseline."""
    algs = [a for a in order if a in summary and "speedup_nodes_vs_baseline" in summary[a]]
    
    if not algs:
        return
    
    speedup_nodes = [summary[a]["speedup_nodes_vs_baseline"] for a in algs]
    speedup_time = [summary[a]["speedup_time_vs_baseline"] for a in algs]
    
    x = range(len(algs))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - width/2 for i in x], speedup_nodes, width, label="Speedup Nodos", color="#1f77b4")
    ax.bar([i + width/2 for i in x], speedup_time, width, label="Speedup Tiempo", color="#ff7f0e")
    
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, label="Baseline")
    ax.set_ylabel("Speedup (mayor es mejor)")
    ax.set_title("Speedup vs A* Euclidean")
    ax.set_xticks(x)
    ax.set_xticklabels(algs, rotation=15, ha="right")
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_time_vs_energy(rows: List[Dict[str, Any]], save_path: str) -> None:
    """
    Scatter plot: Tiempo vs Energía.
    Cada punto es un test run.
    """
    valid = [r for r in rows if r["reached_destination"]]
    
    # Agrupar por algoritmo para colorear
    grouped = group_by_alg(valid)
    
    plt.figure(figsize=(10, 6))
    
    colors = {"astar_euclidean": "#1f77b4", "astar_manhattan": "#ff7f0e", 
              "astar_octile": "#2ca02c", "greedy": "#d62728"}
    
    for alg, runs in grouped.items():
        times = [r["time_seconds"] for r in runs]
        energies = [r["energy_kwh"] for r in runs]
        
        color = colors.get(alg, "gray")
        plt.scatter(times, energies, label=alg, alpha=0.7, edgecolors='w', s=60, c=color)
        
    plt.xlabel("Tiempo de Ejecución (s)")
    plt.ylabel("Energía Consumida (kWh)")
    plt.title("Trade-off: Tiempo vs Energía (Cada punto es un test)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Escala logarítmica en tiempo si hay mucha disparidad
    # plt.xscale('log') 
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_box_distributions(
    rows: List[Dict[str, Any]],
    metric_key: str,
    ylabel: str,
    title: str,
    save_path: str,
    order: list | None = None,
) -> None:
    """
    Box plot para ver la distribución de una métrica.
    """
    valid = [r for r in rows if r["reached_destination"]]
    grouped = group_by_alg(valid)
    
    if order is None:
        algs = sorted(grouped.keys())
    else:
        algs = [a for a in order if a in grouped]
        
    data = [ [r[metric_key] for r in grouped[a]] for a in algs ]
    
    plt.figure(figsize=(10, 6))
    
    # Boxplot
    bplot = plt.boxplot(data, patch_artist=True, tick_labels=algs)
    
    # Colores
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
        
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=15, ha="right")
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_table_image(
    data_rows: List[List[Any]],
    columns: List[str],
    title: str,
    save_path: str,
    col_widths: list | None = None
) -> None:
    """Genera una imagen de una tabla."""
    if not data_rows:
        return

    # Ajustar altura basada en filas
    h_cell = 0.6
    h_header = 0.8
    height = (len(data_rows) * h_cell) + h_header + 1
    
    fig, ax = plt.subplots(figsize=(10, height))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(
        cellText=data_rows,
        colLabels=columns,
        loc='center',
        cellLoc='center',
        colWidths=col_widths
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Estilo
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e')
        else:
            if row % 2 == 0:
                cell.set_facecolor('#f2f2f2')
            else:
                cell.set_facecolor('white')
            
    plt.title(title, pad=10, fontsize=12, weight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Analiza resultados de benchmark EV (A* heurísticas vs Greedy)."
    )
    parser.add_argument(
        "resultados_path",
        nargs="?",
        default="resultados.json",
        help="Ruta al archivo resultados.json (por defecto: resultados.json)",
    )
    args = parser.parse_args()

    resultados_path = args.resultados_path
    if not os.path.isfile(resultados_path):
        raise FileNotFoundError(f"No se encontró el archivo: {resultados_path}")

    base_dir = os.path.dirname(os.path.abspath(resultados_path))

    data = load_resultados(resultados_path)
    rows = flatten_runs(data)
    grouped = group_by_alg(rows)
    summary = compute_summary_per_algorithm(grouped)
    add_speedups_vs_baseline(summary, baseline_alg="astar_euclidean")

    # Generar todas las tablas
    all_tables = []
    all_tables.append(make_table_1_summary(summary))
    all_tables.append(make_table_2_median_comparison(summary))
    all_tables.append(make_table_3_best_worst_energy(rows))
    all_tables.append(make_table_4_best_worst_time(rows))
    all_tables.append(make_table_5_recharges_analysis(rows))
    all_tables.append(make_table_6_per_destination(rows))
    all_tables.append(make_table_7_efficiency_ratio(rows))
    all_tables.append(make_table_8_nodes_per_second(rows))
    all_tables.append(make_table_9_astar_heuristic_comparison(summary))
    all_tables.append(make_table_10_astar_vs_greedy(summary))

    # Guardar resumen en JSON y Markdown
    md_path = os.path.join(base_dir, "resumen_algoritmos.md")
    json_path = os.path.join(base_dir, "resumen_algoritmos_resumen.json")

    md_content = "\n\n".join(all_tables)
    save_markdown(md_path, md_content)
    save_summary_json(json_path, summary)

    # Crear gráficos con matplotlib
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    order = ["astar_euclidean", "astar_manhattan", "astar_octile", "greedy"]

    plot_bar_metric(
        summary,
        "mean_nodes_expanded",
        "Nodos expandidos (media)",
        "Comparación de nodos expandidos por algoritmo",
        os.path.join(plots_dir, "nodes_expanded.png"),
        order,
    )

    plot_bar_metric(
        summary,
        "mean_time_seconds",
        "Tiempo medio (s)",
        "Comparación de tiempo medio por algoritmo",
        os.path.join(plots_dir, "time_seconds.png"),
        order,
    )

    plot_bar_metric(
        summary,
        "mean_energy_kwh",
        "Energía media consumida (kWh)",
        "Comparación de energía consumida por algoritmo",
        os.path.join(plots_dir, "energy_kwh.png"),
        order,
    )

    plot_bar_metric(
        summary,
        "mean_num_recharges",
        "Recargas medias",
        "Comparación de número de recargas por algoritmo",
        os.path.join(plots_dir, "num_recharges.png"),
        order,
    )

    plot_comparison_grid(summary, os.path.join(plots_dir, "comparison_grid.png"), order)
    plot_speedup_comparison(summary, os.path.join(plots_dir, "speedup_comparison.png"), order)

    # Nuevos gráficos
    plot_time_vs_energy(rows, os.path.join(plots_dir, "scatter_time_energy.png"))

    plot_box_distributions(
        rows, 
        "energy_kwh", 
        "Energía (kWh)", 
        "Distribución de Energía Consumida", 
        os.path.join(plots_dir, "boxplot_energy.png"),
        order
    )
    
    plot_box_distributions(
        rows, 
        "time_seconds", 
        "Tiempo (s)", 
        "Distribución de Tiempos de Ejecución", 
        os.path.join(plots_dir, "boxplot_time.png"),
        order
    )
    
    plot_box_distributions(
        rows, 
        "nodes_expanded", 
        "Nodos Expandidos", 
        "Distribución de Nodos Expandidos", 
        os.path.join(plots_dir, "boxplot_nodes.png"),
        order
    )

    plot_box_distributions(
        rows, 
        "nodes_expanded", 
        "Nodos Expandidos", 
        "Distribución de Nodos Expandidos", 
        os.path.join(plots_dir, "boxplot_nodes.png"),
        order
    )

    # --- Generar Imágenes de Tablas ---

    # 1. Tabla Resumen (Medias)
    table1_data = []
    table1_cols = ["Algoritmo", "Energía (kWh)", "Tiempo (s)", "Nodos", "Recargas"]
    for alg in order:
        if alg in summary:
            s = summary[alg]
            table1_data.append([
                alg,
                format_float(s["mean_energy_kwh"], 2),
                format_float(s["mean_time_seconds"], 4),
                format_float(s["mean_nodes_expanded"], 0),
                format_float(s["mean_num_recharges"], 2)
            ])
    
    plot_table_image(
        table1_data, 
        table1_cols, 
        "Tabla 1: Resumen General (Promedios)", 
        os.path.join(plots_dir, "table_summary_means.png")
    )

    # 2. Tabla Medianas
    table2_data = []
    table2_cols = ["Algoritmo", "Mediana Energía", "Mediana Tiempo", "Mediana Nodos"]
    for alg in order:
        if alg in summary:
            s = summary[alg]
            table2_data.append([
                alg,
                format_float(s["median_energy_kwh"], 2),
                format_float(s["median_time_seconds"], 4),
                format_float(s["median_nodes_expanded"], 0)
            ])
            
    plot_table_image(
        table2_data, 
        table2_cols, 
        "Tabla 2: Comparación de Medianas (Robustez)", 
        os.path.join(plots_dir, "table_summary_medians.png")
    )

    # 3. Tabla Trade-offs (A* vs Greedy)
    if "astar_euclidean" in summary and "greedy" in summary:
        astar = summary["astar_euclidean"]
        greedy = summary["greedy"]
        
        table3_data = []
        table3_cols = ["Métrica", "A* Euclidean", "Greedy", "Diferencia", "% Cambio"]
        
        comparisons = [
            ("Nodos", "mean_nodes_expanded", 0),
            ("Tiempo (s)", "mean_time_seconds", 4),
            ("Energía (kWh)", "mean_energy_kwh", 2),
            ("Recargas", "mean_num_recharges", 2),
        ]
        
        for name, key, dec in comparisons:
            v1 = astar.get(key, 0)
            v2 = greedy.get(key, 0)
            diff = v2 - v1
            pct = ((v2 / v1 - 1) * 100) if v1 > 0 else 0
            
            table3_data.append([
                name,
                format_float(v1, dec),
                format_float(v2, dec),
                format_float(diff, dec),
                f"{pct:+.1f}%"
            ])
            
        plot_table_image(
            table3_data, 
            table3_cols, 
            "Tabla 3: Trade-offs A* vs Greedy", 
            os.path.join(plots_dir, "table_astar_vs_greedy.png")
        )

    print("Análisis completado.")
    print(f"- Resumen por algoritmo (JSON): {json_path}")
    print(f"- Tablas Markdown (10 tablas): {md_path}")
    print(f"- Gráficos en: {plots_dir}")
    print(f"  - nodes_expanded.png")
    print(f"  - time_seconds.png")
    print(f"  - energy_kwh.png")
    print(f"  - num_recharges.png")
    print(f"  - comparison_grid.png (2x2 grid)")
    print(f"  - speedup_comparison.png")
    print("\nVista rápida de Tabla 1:\n")
    print(make_table_1_summary(summary))


if __name__ == "__main__":
    main()
