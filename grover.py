from qiskit import QuantumCircuit
import numpy as np

def inversion_about_mean(qc: QuantumCircuit, qubits: int):
    # Inversion about mean circuit, derivation can be found in exercise sheet:
    # H^{⊗3} X^{⊗3} (X1 Z1 X1 Z1) CCZ_{1,2,3} X^{⊗3} H^{⊗3}

    qubits_list = list(range(qubits))

    qc.h(qubits_list)
    qc.x(qubits_list)

    qc.h(qubits - 1)
    qc.mcx(list(range(qubits - 1)), qubits - 1)
    qc.h(qubits - 1)
    # - sign change
    for _ in range(2):
        qc.z(0)
        qc.x(0)

    qc.barrier()
    qc.x(qubits_list)
    qc.h(qubits_list)


def oracle(qc: QuantumCircuit, n: int, marked: int):
    """Phase oracle using X + MCX pattern."""
    qc.barrier()

    # Flip qubits whose corresponding bit in 'marked' is 0
    for i in range(n):
        if not (marked >> i) & 1:
            qc.x(i)

    # Multi-controlled X onto the ancilla (qubit n)
    qc.mcx(list(range(n)), n)

    # Undo the X flips
    for i in range(n):
        if not (marked >> i) & 1:
            qc.x(i)

    qc.barrier()


def construct_grover(qubits: int, k: int, marked_state: int) -> QuantumCircuit:
    qc = QuantumCircuit(qubits + 1, qubits)

    qc.x(qubits)

    for i in range(qubits + 1):
        qc.h(i)

    for i in range(k):
        oracle(qc, n=qubits, marked=marked_state)
        inversion_about_mean(qc, qubits)
    return qc

def optimal_iterations(n:int) -> int:
    return int(np.round(np.pi / 4 * np.sqrt(2**n) - 0.5))