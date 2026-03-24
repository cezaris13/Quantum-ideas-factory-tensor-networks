from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector, partial_trace, entropy

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
