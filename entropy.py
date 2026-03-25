from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector, partial_trace, entropy
import numpy as np

import grover

qubits = 4
marked_state = 7
k_optimal = grover.optimal_iterations(qubits)

def von_neumann_entropy_vs_j(qc: QuantumCircuit, n: int) -> list[float]:
    """
    Given a Grover circuit, compute S(j) for every bipartition j = 1..n-1.
    Traces out qubits [j .. n] (right part + ancilla) to get rho_left.
    """
    sv = Statevector(qc)
    entropies = []
    for j in range(1, n):
        qubits_to_trace = list(range(j, n + 1))
        rho_left = partial_trace(sv, qubits_to_trace)
        S = entropy(rho_left, base=2)
        entropies.append(S)
    return entropies

def von_neumann_entropy_vs_t(circuit_builder: callable, n: int,
                              j: int, t_max: int) -> list[float]:
    """
    Compute S at bipartition j for iterations t = 0 .. t_max-1.
 
    Parameters
    ----------
    circuit_builder : callable(t) -> QuantumCircuit
        A function that takes an iteration index t and returns a circuit.
    n  : number of search qubits (ancilla is qubit n).
    j  : bipartition cut position.
    t_max : number of iterations to sweep.
    """
    entropies = []
    for t in range(t_max):
        qc = circuit_builder(t)
        sv = Statevector(qc)
        qubits_to_trace = list(range(j, n + 1))
        rho_left = partial_trace(sv, qubits_to_trace)
        S = entropy(rho_left, base=2)
        entropies.append(S)
    return entropies
 
def von_neumann_entropy_vs_n(qubit_sizes: list[int], 
                             circuit_builder: callable) -> tuple[list[float], list[int]]:
    """
    Compute S at the middle bipartition j=n//2 for each n in qubit_sizes,
    at a fixed Grover iteration t_fixed.
 
    Parameters
    ----------
    qubit_sizes : list of qubit counts to sweep over.
    circuit_builder : callable(t) -> QuantumCircuit
        A function that takes an iteration index t and returns a circuit.
 
    Returns
    -------
    entropies   : S values for each n
    j_positions : middle bipartition index used for each n
    """

    entropies   = []
    j_positions = []
    for n in qubit_sizes:
        j        = n // 2
        qc = circuit_builder(n)
        sv = Statevector(qc)
        qubits_to_trace = list(range(j, n + 1))
        rho_left = partial_trace(sv, qubits_to_trace)
        S        = entropy(rho_left, base=2)
        entropies.append(S)
        j_positions.append(j)
        print(f"n={n:2d}  j={j}  S={S:.5f}")
    return entropies, j_positions


# ── plotting ──────────────────────────────────────────────────
def plot_entropy_vs_j(qc: QuantumCircuit, n: int, t: int) -> None:
    """Plot von Neumann entropy as a function of bipartition index j."""
   
    entropies = von_neumann_entropy_vs_j(qc, n)
    j_values = list(range(1, n))
 
    plt.figure(figsize=(9, 5))
    plt.plot(j_values, entropies, marker="o", linewidth=2,
             color="steelblue", markerfacecolor="tomato", markersize=8)
    plt.axhline(y=max(entropies), color="gray", linestyle="--",
                linewidth=0.8, label=f"max S = {max(entropies):.3f}")
    plt.xlabel("Bipartition index j  (left | right cut)", fontsize=12)
    plt.ylabel("Von Neumann entropy S(j)  [bits]", fontsize=12)
    plt.title(f"Entanglement across bipartitions — iteration t={t}", fontsize=12)
    plt.xticks(j_values)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
 
 
def plot_entropy_vs_t(circuit_builder: callable, n: int, j: int,
                      t_max: int) -> None:
    """Plot von Neumann entropy as a function of iteration t."""
    entropies = von_neumann_entropy_vs_t(circuit_builder, n, j, t_max)
    t_values = list(range(t_max))
 
    plt.figure(figsize=(9, 5))
    plt.plot(t_values, entropies, marker="o", linewidth=2,
             color="steelblue", markerfacecolor="tomato", markersize=8)
    plt.axhline(y=max(entropies), color="gray", linestyle="--",
                linewidth=0.8, label=f"max S = {max(entropies):.3f}")
    plt.xlabel("t", fontsize=12)
    plt.ylabel("Von Neumann entropy S(j)  [bits]", fontsize=12)
    plt.title(f"Entanglement across bipartitions — iteration j={j}", fontsize=12)
    plt.xticks(t_values)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_entropy_vs_n(qubit_sizes: list[int], circuit_builder: callable,
                      t_fixed: int) -> None:
    """
    Plot S at the middle bipartition j=n//2 vs qubit count n, at fixed t.

    Parameters
    ----------
    qubit_sizes     : list of qubit counts to sweep over.
    circuit_builder : callable(n) -> QuantumCircuit
    t_fixed         : used only for the plot title/label.
    """
    entropies, j_positions = von_neumann_entropy_vs_n(qubit_sizes, circuit_builder)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(qubit_sizes, entropies, marker="o", linewidth=2.5,
            color="steelblue", markerfacecolor="tomato",
            markersize=9, label=f"S(j=n//2) at t={t_fixed}")
    ax.fill_between(qubit_sizes, entropies, alpha=0.1, color="steelblue")

    for n, S, j in zip(qubit_sizes, entropies, j_positions):
        ax.annotate(f"j={j}", xy=(n, S), xytext=(0, 10),
                    textcoords="offset points", ha="center",
                    fontsize=8, color="gray")

    ax.set_xlabel("Number of qubits n", fontsize=12)
    ax.set_ylabel("Von Neumann entropy S(j=n//2)  [bits]", fontsize=12)
    ax.set_title(f"Entanglement at middle bipartition vs qubit size  (t={t_fixed})",
                 fontsize=13)
    ax.set_xticks(qubit_sizes)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.show()


def plot_entropy_vs_n_multi_t(qubit_sizes: list[int],
                               builder_per_t: list[tuple[int, callable]]) -> None:
    """
    Plot S at the middle bipartition j=n//2 vs qubit count n,
    for multiple t values on the same axes.

    Parameters
    ----------
    qubit_sizes    : list of qubit counts to sweep over.
    builder_per_t  : list of (t, circuit_builder) pairs where
                     circuit_builder is callable(n) -> QuantumCircuit.
    """
    colors = plt.cm.viridis(np.linspace(0, 1, len(builder_per_t)))

    plt.figure(figsize=(11, 6))
    for (t, circuit_builder), color in zip(builder_per_t, colors):
        entropies, _ = von_neumann_entropy_vs_n(qubit_sizes, circuit_builder)
        plt.plot(qubit_sizes, entropies, marker="o", linewidth=2,
                 color=color, markersize=7, label=f"t={t}")

    plt.xlabel("Number of qubits n", fontsize=12)
    plt.ylabel("Von Neumann entropy S(j=n//2)  [bits]", fontsize=12)
    plt.title("Entanglement at middle bipartition vs qubit size — multiple t values",
              fontsize=13)
    plt.xticks(qubit_sizes)
    plt.legend(title="Grover iteration t")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
