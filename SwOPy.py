"""
SwOPy - Sewer Network Optimization in Python
=====

Ferramenta computacional em Python para otimização de redes coletoras de esgoto:

- rede hipotética com 18 trechos e 19 nós, reconstruída a partir da Figura 5.1;
- dados hidráulicos da Tabela 5.1;
- diâmetros discretos da Tabela 5.2;
- declividades discretas da Tabela 5.3;
- parâmetros do AG alinhados ao estudo:
    população = 300
    gerações = 1000
    Pc = 0.90
    Pm = 0.30
    elitismo
- penalidade crescente por geração para:
    y/D > 0.75
    tensão trativa < 1.00 Pa

Observação importante
---------------------
Detalhes operacionais do AG que foram aproximados:
- seleção por roleta com elitismo;
- cruzamento de um ponto;
- mutação em um único componente do cromossomo;
- topologia reconstruída a partir da figura da rede.

"""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================
# PARÂMETROS DO EXPERIMENTO 
# ============================================================

RANDOM_SEED = 6
POP_SIZE = 500
N_GENERATIONS = 5000
ELITE_COUNT = 3              # escolha prática para elitismo
CROSSOVER_RATE = 0.90        # Pc
MUTATION_RATE = 0.30         # Pm

AC_MIN = 1.50                # profundidade inicial adotada para pontas de rede
K_PENALTY = 0.8              # expoente sugerido no texto
P1_LAMINA = 500_000.0
P2_SHEAR = 50_000.0

DISCRETE_DIAMETERS_MM = [150, 200, 250, 300, 350, 400, 450]
DISCRETE_SLOPES = [0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009]
DEPTH_CLASSES = [2.0, 3.0, 4.5, 6.0, 8.0]

# Solução ótima publicada na Tabela 5.4 / Tabela 5.5 da dissertação
PUBLISHED_OPTIMUM = [
    (150, 0.005),
    (150, 0.005),
    (200, 0.004),
    (200, 0.004),
    (200, 0.005),
    (150, 0.004),
    (150, 0.004),
    (200, 0.003),
    (200, 0.003),
    (150, 0.005),
    (200, 0.005),
    (200, 0.007),
    (250, 0.007),
    (150, 0.005),
    (150, 0.007),
    (150, 0.006),
    (150, 0.009),
    (300, 0.007),
]
PUBLISHED_OPTIMUM_TOTAL_USD = 107_197.98

# ============================================================
# DADOS DA REDE EXEMPLO
# Ordem dos trechos alinhada à planilha de resultados (Tabelas 5.5 a 5.8)
# ============================================================

@dataclass(frozen=True)
class Edge:
    row_id: int
    label: str
    upstream: int
    downstream: int
    length_m: float
    n_manning: float
    q_ini_m3s: float
    q_fin_m3s: float
    ground_down_m: float
    ground_up_m: float


EDGES: List[Edge] = [
    Edge(1,  "1-2",   1,  2, 100, 0.013, 0.0022, 0.0040, 200, 200),
    Edge(2,  "2-2",   3,  2, 100, 0.013, 0.0022, 0.0040, 200, 200),
    Edge(3,  "10-2",  2,  4,  80, 0.013, 0.0056, 0.0112, 200, 200),
    Edge(4,  "10-4",  4,  5,  90, 0.013, 0.0074, 0.0140, 200, 200),
    Edge(5,  "10-6",  5,  6,  80, 0.013, 0.0090, 0.0180, 200, 200),
    Edge(6,  "4-2",   7,  8,  90, 0.013, 0.0022, 0.0036, 200, 200),
    Edge(7,  "5-2",   9,  8,  90, 0.013, 0.0022, 0.0036, 200, 200),
    Edge(8,  "8-2",   8, 10,  80, 0.013, 0.0052, 0.0112, 200, 200),
    Edge(9,  "8-4",  10, 12,  60, 0.013, 0.0064, 0.0128, 200, 200),
    Edge(10, "3-2",  11, 12,  80, 0.013, 0.0022, 0.0032, 200, 200),
    Edge(11, "9-2",  12, 13,  80, 0.013, 0.0096, 0.0192, 200, 200),
    Edge(12, "9-4",  13,  6,  80, 0.013, 0.0104, 0.0208, 200, 200),
    Edge(13, "11-2",  6, 14,  80, 0.013, 0.0218, 0.0436, 200, 200),
    Edge(14, "6-2",  15, 18,  90, 0.013, 0.0022, 0.0036, 200, 200),
    Edge(15, "7-2",  16, 18,  90, 0.013, 0.0022, 0.0036, 200, 200),
    Edge(16, "12-2", 18, 17,  80, 0.013, 0.0052, 0.0104, 200, 200),
    Edge(17, "12-4", 17, 14,  70, 0.013, 0.0066, 0.0132, 200, 200),
    Edge(18, "13-2", 14, 19,  60, 0.013, 0.0296, 0.0592, 200, 200),
]

# Custos da Tabela 4.5
PV_COST_TABLE = {
    100: {2.0: 556.00, 3.0: 556.00, 4.5: 1461.00, 6.0: 1636.00, 8.0: 2054.00},
    150: {2.0: 556.00, 3.0: 556.00, 4.5: 1461.00, 6.0: 1636.00, 8.0: 2054.00},
    175: {2.0: 556.00, 3.0: 556.00, 4.5: 1461.00, 6.0: 1636.00, 8.0: 2054.00},
    200: {2.0: 769.00, 3.0: 844.00, 4.5: 1461.00, 6.0: 1636.00, 8.0: 2054.00},
    250: {2.0: 769.00, 3.0: 844.00, 4.5: 1461.00, 6.0: 1636.00, 8.0: 2054.00},
    300: {2.0: 769.00, 3.0: 844.00, 4.5: 1461.00, 6.0: 1636.00, 8.0: 2054.00},
    350: {2.0: 1131.00, 3.0: 1288.00, 4.5: 1633.00, 6.0: 1822.00, 8.0: 2282.00},
    375: {2.0: 1131.00, 3.0: 1288.00, 4.5: 1633.00, 6.0: 1822.00, 8.0: 2282.00},
    400: {2.0: 1131.00, 3.0: 1288.00, 4.5: 1633.00, 6.0: 1822.00, 8.0: 2282.00},
    450: {2.0: 1131.00, 3.0: 1288.00, 4.5: 1633.00, 6.0: 1822.00, 8.0: 2282.00},
}

# Coeficientes a_ij da Tabela 4.4
# A forma que reproduz corretamente os custos das planilhas é:
# C_unit = sum_i sum_j a_ij * D^i * h^j
A_IJ = {
    0: {0: -29.3185, 1: 28.92595, 2: -5.42286, 3: 0.524836},
    1: {0: 0.338185, 1: 0.045221, 2: -0.0063, 3: 7.81e-04},
    2: {0: -0.00149, 1: -1.15e-04, 2: 1.66e-05, 3: -1.97e-06},
    3: {0: 3.29e-06, 1: 1.60e-07, 2: -2.30e-08, 3: 2.75e-09},
}

# ============================================================
# ESTRUTURAS
# ============================================================

@dataclass
class EdgeResult:
    edge: Edge
    diameter_mm: int
    slope: float
    uc_up_m: float
    dc_down_m: float
    depth_up_m: float
    depth_down_m: float
    depth_class_m: float
    y_over_d_ini: float
    y_over_d_fin: float
    v_ini: float
    v_fin: float
    v_critical: float
    shear_pa: float
    collector_cost_usd: float
    upstream_pv_cost_usd: float
    row_total_usd: float


@dataclass
class EvaluationResult:
    total_cost_usd: float
    final_pv_cost_usd: float
    excess_lamina: float
    deficit_shear: float
    rows: List[EdgeResult]


@dataclass
class GARunResult:
    best_chromosome: List[int]
    best_eval: EvaluationResult
    best_penalized_cost_usd: float
    best_penalty_usd: float
    best_generation: int
    history_best: List[float]


# ============================================================
# TOPOLOGIA DA REDE
# ============================================================

IN_EDGES: Dict[int, List[int]] = defaultdict(list)
OUT_EDGE: Dict[int, int] = {}
NODES = set()

for idx, edge in enumerate(EDGES):
    IN_EDGES[edge.downstream].append(idx)
    OUT_EDGE[edge.upstream] = idx
    NODES.add(edge.upstream)
    NODES.add(edge.downstream)

indegree = {node: 0 for node in NODES}
for edge in EDGES:
    indegree[edge.downstream] += 1

queue = deque(sorted(node for node, deg in indegree.items() if deg == 0))
TOPO_NODE_ORDER: List[int] = []

while queue:
    node = queue.popleft()
    TOPO_NODE_ORDER.append(node)
    if node in OUT_EDGE:
        next_node = EDGES[OUT_EDGE[node]].downstream
        indegree[next_node] -= 1
        if indegree[next_node] == 0:
            queue.append(next_node)

# ============================================================
# FUNÇÕES HIDRÁULICAS
# ============================================================

def theta_from_y_over_d(y_over_d: float) -> float:
    y_over_d = max(1e-9, min(0.999999, y_over_d))
    return 2.0 * math.acos(1.0 - 2.0 * y_over_d)


def circular_section_properties(diameter_m: float, theta: float) -> Tuple[float, float]:
    area = (diameter_m ** 2 / 8.0) * (theta - math.sin(theta))
    perimeter = (diameter_m / 2.0) * theta
    if perimeter <= 0:
        return 0.0, 0.0
    rh = area / perimeter
    return area, rh


def flow_for_y_over_d(y_over_d: float, diameter_m: float, slope: float, n_manning: float) -> float:
    theta = theta_from_y_over_d(y_over_d)
    area, rh = circular_section_properties(diameter_m, theta)
    if area <= 0 or rh <= 0 or slope <= 0:
        return 0.0
    return (1.0 / n_manning) * area * (rh ** (2.0 / 3.0)) * math.sqrt(slope)


def solve_y_over_d_for_flow(flow_m3s: float, diameter_m: float, slope: float, n_manning: float) -> float:
    if flow_m3s <= 0.0:
        return 0.0
    lo, hi = 1e-8, 0.999999
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if flow_for_y_over_d(mid, diameter_m, slope, n_manning) < flow_m3s:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# Pré-cálculo hidráulico para todas as combinações discretas
HYDRAULIC_CACHE: Dict[Tuple[int, int, float], Tuple[float, float, float, float, float, float]] = {}

for idx, edge in enumerate(EDGES):
    for diameter_mm in DISCRETE_DIAMETERS_MM:
        diameter_m = diameter_mm / 1000.0
        for slope in DISCRETE_SLOPES:
            y_ini = solve_y_over_d_for_flow(edge.q_ini_m3s, diameter_m, slope, edge.n_manning)
            y_fin = solve_y_over_d_for_flow(edge.q_fin_m3s, diameter_m, slope, edge.n_manning)

            area_ini, rh_ini = circular_section_properties(diameter_m, theta_from_y_over_d(y_ini))
            area_fin, rh_fin = circular_section_properties(diameter_m, theta_from_y_over_d(y_fin))

            v_ini = edge.q_ini_m3s / area_ini if area_ini > 0 else 0.0
            v_fin = edge.q_fin_m3s / area_fin if area_fin > 0 else 0.0
            v_critical = 6.0 * math.sqrt(9.81 * rh_fin) if rh_fin > 0 else 0.0
            shear = 9810.0 * rh_ini * slope if rh_ini > 0 else 0.0

            HYDRAULIC_CACHE[(idx, diameter_mm, slope)] = (y_ini, y_fin, v_ini, v_fin, v_critical, shear)

# ============================================================
# CUSTOS
# ============================================================

def ceil_depth_class(depth_m: float) -> float:
    for cls in DEPTH_CLASSES:
        if depth_m <= cls + 1e-9:
            return cls
    return DEPTH_CLASSES[-1]


def collector_unit_cost_usd_per_m(diameter_mm: int, depth_class_m: float) -> float:
    total = 0.0
    for i in range(4):
        for j in range(4):
            total += A_IJ[i][j] * (diameter_mm ** i) * (depth_class_m ** j)
    return total


def pv_cost_usd(max_depth_m: float, max_diameter_mm: int) -> float:
    available = PV_COST_TABLE[max_diameter_mm]
    for cls in sorted(available):
        if max_depth_m <= cls + 1e-9:
            return available[cls]
    return available[max(sorted(available))]


# ============================================================
# CROMOSSOMO
# cromossomo = [d1,s1,d2,s2,...,d18,s18] com códigos 0..6
# ============================================================

def random_chromosome() -> List[int]:
    return [random.randrange(7) for _ in range(2 * len(EDGES))]


def decode_chromosome(chromosome: List[int]) -> List[Tuple[int, float]]:
    genes: List[Tuple[int, float]] = []
    for i in range(0, len(chromosome), 2):
        diameter_mm = DISCRETE_DIAMETERS_MM[chromosome[i]]
        slope = DISCRETE_SLOPES[chromosome[i + 1]]
        genes.append((diameter_mm, slope))
    return genes


def chromosome_from_solution(solution: List[Tuple[int, float]]) -> List[int]:
    codes: List[int] = []
    for diameter_mm, slope in solution:
        codes.append(DISCRETE_DIAMETERS_MM.index(diameter_mm))
        codes.append(DISCRETE_SLOPES.index(slope))
    return codes


PUBLISHED_OPTIMUM_CODES = chromosome_from_solution(PUBLISHED_OPTIMUM)

# ============================================================
# AVALIAÇÃO DA SOLUÇÃO
# ============================================================

BASE_EVAL_CACHE: Dict[Tuple[int, ...], EvaluationResult] = {}

def evaluate_base(chromosome: List[int]) -> EvaluationResult:
    key = tuple(chromosome)
    if key in BASE_EVAL_CACHE:
        return BASE_EVAL_CACHE[key]

    genes = decode_chromosome(chromosome)
    raw_rows = [None] * len(EDGES)

    # 1) Propagação geométrica ao longo da topologia
    for node in TOPO_NODE_ORDER:
        if node not in OUT_EDGE:
            continue

        edge_idx = OUT_EDGE[node]
        edge = EDGES[edge_idx]
        diameter_mm, slope = genes[edge_idx]

        if IN_EDGES[edge.upstream]:
            uc_up = min(raw_rows[in_idx]["dc_down_m"] for in_idx in IN_EDGES[edge.upstream])
            depth_up = edge.ground_up_m - uc_up
        else:
            depth_up = AC_MIN
            uc_up = edge.ground_up_m - depth_up

        dc_down = uc_up - slope * edge.length_m
        depth_down = edge.ground_down_m - dc_down

        mean_depth = (depth_up + depth_down) / 2.0
        depth_class = ceil_depth_class(mean_depth)

        y_ini, y_fin, v_ini, v_fin, v_critical, shear = HYDRAULIC_CACHE[(edge_idx, diameter_mm, slope)]
        collector_cost = collector_unit_cost_usd_per_m(diameter_mm, depth_class) * edge.length_m

        raw_rows[edge_idx] = {
            "edge": edge,
            "diameter_mm": diameter_mm,
            "slope": slope,
            "uc_up_m": uc_up,
            "dc_down_m": dc_down,
            "depth_up_m": depth_up,
            "depth_down_m": depth_down,
            "depth_class_m": depth_class,
            "y_over_d_ini": y_ini,
            "y_over_d_fin": y_fin,
            "v_ini": v_ini,
            "v_fin": v_fin,
            "v_critical": v_critical,
            "shear_pa": shear,
            "collector_cost_usd": collector_cost,
        }

    # 2) Características dos PVs por nó
    node_max_depth: Dict[int, float] = defaultdict(float)
    node_max_diameter: Dict[int, int] = defaultdict(int)

    for row in raw_rows:
        edge = row["edge"]

        node_max_depth[edge.upstream] = max(node_max_depth[edge.upstream], row["depth_up_m"])
        node_max_depth[edge.downstream] = max(node_max_depth[edge.downstream], row["depth_down_m"])

        node_max_diameter[edge.upstream] = max(node_max_diameter[edge.upstream], row["diameter_mm"])
        node_max_diameter[edge.downstream] = max(node_max_diameter[edge.downstream], row["diameter_mm"])

    # 3) PV associado à linha da tabela = PV do nó de montante do trecho
    rows: List[EdgeResult] = []
    pv_sum = 0.0

    for row in raw_rows:
        edge = row["edge"]
        upstream_pv_cost = pv_cost_usd(node_max_depth[edge.upstream], node_max_diameter[edge.upstream])
        pv_sum += upstream_pv_cost

        rows.append(
            EdgeResult(
                edge=edge,
                diameter_mm=row["diameter_mm"],
                slope=row["slope"],
                uc_up_m=row["uc_up_m"],
                dc_down_m=row["dc_down_m"],
                depth_up_m=row["depth_up_m"],
                depth_down_m=row["depth_down_m"],
                depth_class_m=row["depth_class_m"],
                y_over_d_ini=row["y_over_d_ini"],
                y_over_d_fin=row["y_over_d_fin"],
                v_ini=row["v_ini"],
                v_fin=row["v_fin"],
                v_critical=row["v_critical"],
                shear_pa=row["shear_pa"],
                collector_cost_usd=row["collector_cost_usd"],
                upstream_pv_cost_usd=upstream_pv_cost,
                row_total_usd=row["collector_cost_usd"] + upstream_pv_cost,
            )
        )

    final_node = 19
    final_pv_cost = pv_cost_usd(node_max_depth[final_node], node_max_diameter[final_node])

    total_cost = sum(r.collector_cost_usd for r in rows) + pv_sum + final_pv_cost
    excess_lamina = sum(max(r.y_over_d_fin - 0.75, 0.0) for r in rows)
    deficit_shear = sum(max(1.0 - r.shear_pa, 0.0) for r in rows)

    result = EvaluationResult(
        total_cost_usd=total_cost,
        final_pv_cost_usd=final_pv_cost,
        excess_lamina=excess_lamina,
        deficit_shear=deficit_shear,
        rows=rows,
    )
    BASE_EVAL_CACHE[key] = result
    return result


def penalized_cost(chromosome: List[int], generation: int, max_generations: int) -> Tuple[float, EvaluationResult, float]:
    base = evaluate_base(chromosome)
    generation_factor = (generation / max_generations) ** K_PENALTY
    # O AG compara indivíduos por este acréscimo ao custo base quando há violação hidráulica.
    penalty = generation_factor * (
        P1_LAMINA * base.excess_lamina +
        P2_SHEAR * base.deficit_shear
    )
    return base.total_cost_usd + penalty, base, penalty


# ============================================================
# ALGORITMO GENÉTICO
# ============================================================

def aptitude_values(sorted_penalized_costs: List[float]) -> List[float]:
    worst = max(sorted_penalized_costs)
    return [max(worst * 1.2 - value, 1e-9) for value in sorted_penalized_costs]


def roulette_select(population: List[List[int]], aptitudes: List[float]) -> List[int]:
    total = sum(aptitudes)
    r = random.random() * total
    acc = 0.0
    for chromosome, aptitude in zip(population, aptitudes):
        acc += aptitude
        if acc >= r:
            return chromosome.copy()
    return population[-1].copy()


def one_point_crossover(parent_a: List[int], parent_b: List[int]) -> Tuple[List[int], List[int]]:
    if random.random() >= CROSSOVER_RATE:
        return parent_a.copy(), parent_b.copy()

    cut = random.randint(1, len(parent_a) - 1)
    child_a = parent_a[:cut] + parent_b[cut:]
    child_b = parent_b[:cut] + parent_a[cut:]
    return child_a, child_b


def mutate_one_component(chromosome: List[int]) -> None:
    if random.random() >= MUTATION_RATE:
        return

    idx = random.randrange(len(chromosome))
    current = chromosome[idx]
    options = [x for x in range(7) if x != current]
    chromosome[idx] = random.choice(options)


def run_ga() -> GARunResult:
    random.seed(RANDOM_SEED)

    population = [random_chromosome() for _ in range(POP_SIZE)]
    history_best: List[float] = []

    best_chromosome: List[int] | None = None
    best_eval: EvaluationResult | None = None
    best_penalized = float("inf")
    best_penalty = 0.0
    best_generation = 1

    for generation in range(1, N_GENERATIONS + 1):
        # Cada cromossomo vira uma tupla: (custo_penalizado, avaliação_base, penalidade).
        evaluated = [penalized_cost(chromosome, generation, N_GENERATIONS) for chromosome in population]

        # A população é ordenada pelo custo penalizado (item[1][0]), do menor para o maior.
        ranked = sorted(
            zip(population, evaluated),
            key=lambda item: item[1][0]
        )

        population = [chromosome for chromosome, _ in ranked]
        penalized_values = [triple[0] for _, triple in ranked]
        base_evals = [triple[1] for _, triple in ranked]
        penalties = [triple[2] for _, triple in ranked]

        if penalized_values[0] < best_penalized:
            best_penalized = penalized_values[0]
            best_chromosome = population[0].copy()
            best_eval = base_evals[0]
            best_penalty = penalties[0]
            best_generation = generation

        history_best.append(penalized_values[0])

        if generation == 1 or generation % 100 == 0:
            print(
                f"Geração {generation:4d} | "
                f"Melhor custo penalizado = {penalized_values[0]:,.2f} | "
                f"Custo base = {base_evals[0].total_cost_usd:,.2f} | "
                f"Penalidade = {penalties[0]:,.2f}"
            )

        aptitudes = aptitude_values(penalized_values)

        # O elitismo preserva diretamente os melhores indivíduos segundo o custo penalizado.
        new_population: List[List[int]] = [population[i].copy() for i in range(ELITE_COUNT)]

        while len(new_population) < POP_SIZE:
            parent_a = roulette_select(population, aptitudes)
            parent_b = roulette_select(population, aptitudes)

            child_a, child_b = one_point_crossover(parent_a, parent_b)

            mutate_one_component(child_a)
            mutate_one_component(child_b)

            new_population.append(child_a)
            if len(new_population) < POP_SIZE:
                new_population.append(child_b)

        population = new_population

    assert best_chromosome is not None and best_eval is not None
    return GARunResult(
        best_chromosome=best_chromosome,
        best_eval=best_eval,
        best_penalized_cost_usd=best_penalized,
        best_penalty_usd=best_penalty,
        best_generation=best_generation,
        history_best=history_best,
    )


# ============================================================
# RELATÓRIOS
# ============================================================

def row_inconsistencies(row: EdgeResult) -> List[str]:
    inconsistencies: List[str] = []
    if row.y_over_d_fin > 0.75 + 1e-12:
        inconsistencies.append(f"lamina y/D final = {row.y_over_d_fin:.4f} > 0.7500")
    if row.shear_pa < 1.0 - 1e-12:
        inconsistencies.append(f"arraste insuficiente: tau = {row.shear_pa:.4f} Pa < 1.0000 Pa")
    return inconsistencies


def solution_problem_messages(result: EvaluationResult) -> List[str]:
    problematic_rows: List[str] = []
    for row in result.rows:
        inconsistencies = row_inconsistencies(row)
        if inconsistencies:
            problematic_rows.append(
                f"Trecho {row.edge.row_id} ({row.edge.label}, {row.edge.upstream}->{row.edge.downstream}): "
                + " | ".join(inconsistencies)
            )
    return problematic_rows


def print_solution(
    title: str,
    chromosome: List[int],
    result: EvaluationResult,
    best_penalized_cost_usd: float | None = None,
    best_penalty_usd: float | None = None,
    best_generation: int | None = None,
    final_penalized_cost_usd: float | None = None,
    final_penalty_usd: float | None = None,
) -> None:
    feasible = result.excess_lamina <= 1e-12 and result.deficit_shear <= 1e-12
    problematic_rows = solution_problem_messages(result)

    print("\n" + "=" * 108)
    print(title)
    print("=" * 108)
    print(f"Custo total calculado:            {result.total_cost_usd:,.2f} US$")
    if best_penalized_cost_usd is not None:
        print(f"Custo penalizado no AG:           {best_penalized_cost_usd:,.2f} US$")
    if best_penalty_usd is not None:
        print(f"Penalidade no AG:                 {best_penalty_usd:,.2f} US$")
    if best_generation is not None:
        print(f"Geração do melhor penalizado:     {best_generation}")
    if final_penalized_cost_usd is not None:
        print(f"Custo penalizado na geração final:{final_penalized_cost_usd:>13,.2f} US$")
    if final_penalty_usd is not None:
        print(f"Penalidade na geração final:      {final_penalty_usd:,.2f} US$")
    print(f"Custo PV final (nó 19):           {result.final_pv_cost_usd:,.2f} US$")
    print(f"Solução sem violação hidráulica?  {'sim' if feasible else 'não'}")
    print(f"Excesso total de y/D (>0,75):     {result.excess_lamina:.6f}")
    print(f"Déficit total de tensão (<1 Pa):  {result.deficit_shear:.6f}")
    if feasible:
        print("Atende os limitantes hidráulicos adotados: lâmina (y/D <= 0,75) e arraste (tau >= 1,00 Pa).")
    else:
        print("Trechos problemáticos e incoerências hidráulicas:")
        for message in problematic_rows:
            print(f"  - {message}")

    header = (
        f"{'Tr':>2} {'Rótulo':>6} {'U->D':>7} {'L':>5} {'D':>4} {'S':>7} "
        f"{'ProfM':>7} {'ProfJ':>7} {'h_cls':>6} "
        f"{'y/D i':>6} {'y/D f':>6} {'tau':>8} {'C_col':>12} {'C_PV':>9} {'Total':>12}"
    )
    print(header)
    print("-" * len(header))

    for row in result.rows:
        print(
            f"{row.edge.row_id:>2} "
            f"{row.edge.label:>6} "
            f"{f'{row.edge.upstream}->{row.edge.downstream}':>7} "
            f"{row.edge.length_m:>5.0f} "
            f"{row.diameter_mm:>4d} "
            f"{row.slope:>7.3f} "
            f"{row.depth_up_m:>7.2f} "
            f"{row.depth_down_m:>7.2f} "
            f"{row.depth_class_m:>6.1f} "
            f"{row.y_over_d_ini:>6.2f} "
            f"{row.y_over_d_fin:>6.2f} "
            f"{row.shear_pa:>8.5f} "
            f"{row.collector_cost_usd:>12,.2f} "
            f"{row.upstream_pv_cost_usd:>9,.2f} "
            f"{row.row_total_usd:>12,.2f}"
        )


def compare_against_published(best_eval: EvaluationResult) -> None:
    published_eval = evaluate_base(PUBLISHED_OPTIMUM_CODES)
    diff_model_vs_published = published_eval.total_cost_usd - PUBLISHED_OPTIMUM_TOTAL_USD
    diff_best_vs_published = best_eval.total_cost_usd - PUBLISHED_OPTIMUM_TOTAL_USD

    print("\n" + "-" * 108)
    print("COMPARAÇÃO COM A DISSERTAÇÃO")
    print("-" * 108)
    print(f"Solução ótima publicada (Tabela 5.4 / 5.5):   {PUBLISHED_OPTIMUM_TOTAL_USD:,.2f} US$")
    print(f"Ótimo publicado recalculado por este script:  {published_eval.total_cost_usd:,.2f} US$")
    print(f"Desvio do recálculo interno:                  {diff_model_vs_published:,.2f} US$")
    print(f"Melhor solução encontrada nesta execução:     {best_eval.total_cost_usd:,.2f} US$")
    print(f"Desvio desta execução vs. publicado:          {diff_best_vs_published:,.2f} US$")


def export_solution_csv(result: EvaluationResult, filepath: Path) -> None:
    feasible = result.excess_lamina <= 1e-12 and result.deficit_shear <= 1e-12
    problematic_rows = solution_problem_messages(result)
    hydraulic_message = (
        "Atende os limitantes hidraulicos adotados: lamina (y/D <= 0,75) e arraste (tau >= 1,00 Pa)."
        if feasible
        else "Nao atende a todos os limitantes hidraulicos adotados; ver trechos problematicos."
    )

    with filepath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "trecho_id", "rotulo", "upstream", "downstream", "length_m",
            "diameter_mm", "slope", "uc_up_m", "dc_down_m",
            "depth_up_m", "depth_down_m", "depth_class_m",
            "y_over_d_ini", "y_over_d_fin", "v_ini_m_s", "v_fin_m_s",
            "v_critical_m_s", "shear_pa", "collector_cost_usd",
            "upstream_pv_cost_usd", "row_total_usd",
            "violates_lamina", "violates_arraste", "hydraulic_inconsistencies"
        ])
        for row in result.rows:
            inconsistencies = row_inconsistencies(row)
            writer.writerow([
                row.edge.row_id, row.edge.label, row.edge.upstream, row.edge.downstream,
                row.edge.length_m, row.diameter_mm, row.slope,
                row.uc_up_m, row.dc_down_m, row.depth_up_m, row.depth_down_m,
                row.depth_class_m, row.y_over_d_ini, row.y_over_d_fin,
                row.v_ini, row.v_fin, row.v_critical, row.shear_pa,
                row.collector_cost_usd, row.upstream_pv_cost_usd, row.row_total_usd,
                "sim" if row.y_over_d_fin > 0.75 + 1e-12 else "nao",
                "sim" if row.shear_pa < 1.0 - 1e-12 else "nao",
                " | ".join(inconsistencies),
            ])
        writer.writerow([])
        writer.writerow(["summary_key", "summary_value"])
        writer.writerow(["solution_feasible", "sim" if feasible else "nao"])
        writer.writerow(["hydraulic_message", hydraulic_message])
        writer.writerow(["excess_lamina", result.excess_lamina])
        writer.writerow(["deficit_shear", result.deficit_shear])
        for message in problematic_rows:
            writer.writerow(["problematic_section", message])
        writer.writerow(["final_pv_cost_usd", result.final_pv_cost_usd])
        writer.writerow(["total_cost_usd", result.total_cost_usd])


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("SwOPy")
    print("Rede exemplo da dissertação com configuração mais fiel.")
    print(f"População = {POP_SIZE} | Gerações = {N_GENERATIONS} | Pc = {CROSSOVER_RATE:.2f} | Pm = {MUTATION_RATE:.2f}")

    published_eval = evaluate_base(PUBLISHED_OPTIMUM_CODES)
    print(f"\nÓtimo publicado na dissertação: {PUBLISHED_OPTIMUM_TOTAL_USD:,.2f} US$")
    print(f"Ótimo publicado recalculado por este script: {published_eval.total_cost_usd:,.2f} US$")

    ga_result = run_ga()
    final_penalized_cost_usd, _, final_penalty_usd = penalized_cost(
        ga_result.best_chromosome,
        N_GENERATIONS,
        N_GENERATIONS,
    )
    print_solution(
        "MELHOR SOLUÇÃO ENCONTRADA",
        ga_result.best_chromosome,
        ga_result.best_eval,
        best_penalized_cost_usd=ga_result.best_penalized_cost_usd,
        best_penalty_usd=ga_result.best_penalty_usd,
        best_generation=ga_result.best_generation,
        final_penalized_cost_usd=final_penalized_cost_usd,
        final_penalty_usd=final_penalty_usd,
    )
    compare_against_published(ga_result.best_eval)

    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "SwOPy_resultado.csv"
    export_solution_csv(ga_result.best_eval, csv_path)
    print(f"\nArquivo exportado: {csv_path.name}")


if __name__ == "__main__":
    main()
