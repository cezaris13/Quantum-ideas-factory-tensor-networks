from qiskit import QuantumCircuit
import numpy as np
import matplotlib.pyplot as plt

import utils


def get_pos_distribution(qc, n_pos, shots, skip_qubits=[]):
    n_nodes = 2**n_pos
    probs = utils.measure(qc, shots, skip_qubits)
    pos_prob = np.zeros(n_nodes)
    probs = {int(k, 2): v for k, v in probs.items()}
    for k, v in probs.items():
        pos_prob[k % n_nodes] += v / shots
    return pos_prob


def signed_nodes(n_nodes):
    nodes = np.arange(n_nodes)
    return np.where(nodes < n_nodes // 2, nodes, nodes - n_nodes)


#  -o--o--o--x
#  -o--o--X---
#  -o--X------
#  -X---------
def increment_circuit(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    for i in range(n - 1, 0, -1):
        qc.mcx(list(range(i)), i)
    qc.x(0)
    return qc


#  -X--o--o--o
#  ----x--o--o
#  -------x--o
#  ----------x
def decrement_circuit(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    qc.x(0)
    for i in range(1, n):
        qc.mcx(list(range(i)), i)
    return qc


def dtqw_step_1d(n_pos: int) -> QuantumCircuit:
    n = n_pos + 1
    pos_qubits = list(range(n_pos))
    coin_qubit = n_pos

    qc = QuantumCircuit(n)

    qc.h(coin_qubit)

    # ── Conditional increment (coin=|1>) ──
    inc = increment_circuit(n_pos)
    # Control on coin=|1>: X-flip coin, apply controlled-inc, X-flip back
    qc.append(inc.control(1), [coin_qubit] + pos_qubits)
    qc.x(coin_qubit)

    # ── Conditional decrement (coin=|0>) ──
    dec = decrement_circuit(n_pos)

    qc.append(dec.control(1), [coin_qubit] + pos_qubits)
    qc.x(coin_qubit)

    return qc


def construct_walk(n_position_qubits: int, steps: int) -> QuantumCircuit:
    """
    Build a complete discrete-time quantum walk circuit.

    Parameters
    ----------
    n_position_qubits : qubits for the position register (cycle of 2^n).
    steps             : number of walk steps.
    coin_type         : 'hadamard' or 'grover'.
    symmetric         : if True, initialise coin in 1/√2(|0⟩+i|1⟩) for a
                        symmetric distribution; otherwise coin starts in |0⟩.

    Returns
    -------
    QuantumCircuit with position qubits 0..n-1 and coin qubit n.
    """
    n_total = n_position_qubits + 1
    qc = QuantumCircuit(n_total, n_total-1, name=f"QWalk_{steps}steps")

    coin = n_position_qubits
    position = list(range(n_position_qubits))

    qc.h(coin)
    qc.s(coin)

    initial_position = 0
    for i, q in enumerate(position):
        if (initial_position >> i) & 1:
            qc.x(q)

    # apply walk steps
    step = dtqw_step_1d(n_position_qubits)
    for _ in range(steps):
        qc = qc.compose(step)

    return qc


def walk_distribution(
    n_position_qubits: int, steps: int, shots:int =1024
) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Run a discrete-time quantum walk and return the position distribution.

    Returns
    -------
    (nodes, probs, variance) where nodes are signed positions.
    """
    qc = construct_walk(n_position_qubits, steps)
    n_nodes = 2**n_position_qubits
    nodes = signed_nodes(n_nodes)
    probs = get_pos_distribution(qc, n_position_qubits, shots, [n_position_qubits])

    mean = np.sum(nodes * probs)
    var = np.sum((nodes - mean) ** 2 * probs)
    return nodes, probs, var


def plot_walk(n_position_qubits: int, steps: int, shots:int = 1024) -> None:
    _, probs, var = walk_distribution(n_position_qubits, steps, shots = shots)
    ns = signed_nodes(2**n_position_qubits)

    plt.figure(figsize=(13, 5))
    plt.bar(ns, probs, color="steelblue", alpha=0.85, width=0.85)
    plt.xlabel("Position (signed)", fontsize=12)
    plt.ylabel("Probability", fontsize=11)
    plt.title(
        f"Symmetric quantum walk, " f"t={steps}  [σ² = {var:.1f}]",
        fontsize=13,
    )
    plt.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.show()
