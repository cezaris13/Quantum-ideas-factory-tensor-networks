from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import algorithms.grover as grover
import utils.entropy as entropy
import algorithms.quantum_random_walk as quantum_random_walk
import algorithms.qft as qft
from algorithm import Algorithm

TEMPLATE_DIR = Path(__file__).parent / "template"
print(TEMPLATE_DIR)
TEMPLATE_NAME = "explorer.html.j2"
OUTPUT_FILE = Path(__file__).parent / "entropy_3d_explorer.html"

MARKED_STATE = 7  # shared oracle target

ALGORITHMS: list[Algorithm] = [
    Algorithm(
        key="grover",
        label="Grover",
        color="#21918c",
        colorscale=[
            [0.0, "#440154"],
            [0.2, "#3b528b"],
            [0.4, "#21918c"],
            [0.6, "#5ec962"],
            [0.8, "#a0da39"],
            [1.0, "#fde725"],
        ],
        build_circuit=lambda n, t: grover.construct_grover(n, t, MARKED_STATE),
        extra_qubits=1,
        n_range_nt=range(2, 9),
        t_range_nt=range(0, 30),
        n_range_nj=range(2, 9),
        t_fixed_nj=3,
        n_fixed_jt=7,
        t_range_jt=range(0, 30),
    ),
    Algorithm(
        key="walk",
        label="Quantum Walk",
        color="#cc4778",
        colorscale=[
            [0.0, "#440154"],
            [0.2, "#3b528b"],
            [0.4, "#21918c"],
            [0.6, "#5ec962"],
            [0.8, "#a0da39"],
            [1.0, "#fde725"],
        ],
        build_circuit=lambda n, t: quantum_random_walk.construct_walk(n, t),
        extra_qubits=1,
        n_range_nt=range(2, 8),
        t_range_nt=range(0, 40),
        n_range_nj=range(2, 8),
        t_fixed_nj=10,
        n_fixed_jt=6,
        t_range_jt=range(0, 40),
    ),
    Algorithm(
        key="qft",
        label="Quantum Fourier Transform",
        color="#21918c",
        colorscale=[
            [0.0, "#440154"],
            [0.2, "#3b528b"],
            [0.4, "#21918c"],
            [0.6, "#5ec962"],
            [0.8, "#a0da39"],
            [1.0, "#fde725"],
        ],
        build_circuit=lambda n, t: qft.qft(n, t, 0b0),
        extra_qubits=0,
        n_range_nt=range(2, 9),
        t_range_nt=range(0, 30),
        n_range_nj=range(2, 9),
        t_fixed_nj=3,
        n_fixed_jt=7,
        t_range_jt=range(0, 30),
    ),
]


def sweep_nt(algo: Algorithm) -> dict:
    n_vals, t_vals = list(algo.n_range_nt), list(algo.t_range_nt)
    S = []
    for n in n_vals:
        row = [
            entropy.von_neumann_entropy(
                algo.build_circuit(n, t), n, n // 2, algo.extra_qubits
            )
            for t in t_vals
        ]
        S.append(row)
        print(f"  [{algo.key}] S(n,t): n={n}")
    return {"n": n_vals, "t": t_vals, "S": S}


def sweep_nj(algo: Algorithm) -> dict:
    n_vals = list(algo.n_range_nj)
    S = []
    for n in n_vals:
        qc = algo.build_circuit(n, algo.t_fixed_nj)
        row = [
            entropy.von_neumann_entropy(qc, n, j, algo.extra_qubits)
            for j in range(1, n)
        ]
        S.append(row)
        print(f"  [{algo.key}] S(n,j): n={n}")
    return {"n": n_vals, "S": S, "t_fixed": algo.t_fixed_nj}


def sweep_jt(algo: Algorithm) -> dict:
    n_fixed = algo.n_fixed_jt
    t_vals = list(algo.t_range_jt)
    j_vals = list(range(1, n_fixed))
    S = []
    for j in j_vals:
        row = [
            entropy.von_neumann_entropy(
                algo.build_circuit(n_fixed, t), n_fixed, j, algo.extra_qubits
            )
            for t in t_vals
        ]
        S.append(row)
        print(f"  [{algo.key}] S(j,t): j={j}")
    return {"j": j_vals, "t": t_vals, "S": S, "n_fixed": n_fixed}


def compute_all(algorithms: list[Algorithm]) -> dict:
    data = {}
    for algo in algorithms:
        print(f"\n{'=' * 40}\n  {algo.label.upper()}\n{'=' * 40}")
        data[f"{algo.key}_nt"] = sweep_nt(algo)
        data[f"{algo.key}_nj"] = sweep_nj(algo)
        data[f"{algo.key}_jt"] = sweep_jt(algo)
    return data


def build_template_context(algorithms: list[Algorithm], data: dict) -> dict:
    algo_meta = []
    for i, algo in enumerate(algorithms):
        algo_meta.append(
            {
                "key": algo.key,
                "label": algo.label,
                "color": algo.color,
                "colorscale": algo.colorscale,
                "is_default": i == 0,
            }
        )

    return {
        "title": "Entanglement Entropy Explorer",
        "subtitle": "Quantum Ideas Factory 2026 &middot; CESQ Strasbourg",
        "marked_state": MARKED_STATE,
        "data_json": json.dumps(data),
        "algorithms": algo_meta,
        "algorithms_json": json.dumps({a["key"]: a for a in algo_meta}),
        "default_algo": algorithms[0].key,
        "plot_tabs": [
            {"key": "nt", "label": "S(n, t)"},
            {"key": "nj", "label": "S(n, j)"},
            {"key": "jt", "label": "S(j, t)"},
        ],
    }


def render_html(algorithms: list[Algorithm], data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    ctx = build_template_context(algorithms, data)
    return template.render(**ctx)


if __name__ == "__main__":
    data = compute_all(ALGORITHMS)
    html = render_html(ALGORITHMS, data)

    out = Path(OUTPUT_FILE)
    out.write_text(html)

    print(f"\n✓ Interactive explorer saved to {out.resolve()}")
    print("  Open it in any browser — no server needed.")
