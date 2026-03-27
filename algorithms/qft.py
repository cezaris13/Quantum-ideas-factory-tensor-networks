from qiskit import QuantumCircuit, QuantumRegister
import numpy as np


def qft(n, t, initial_state=None):
    qc = QuantumCircuit(n)

    initial_bitstring = format(initial_state, f"0{n}b")
    if initial_state is not None:
        for i, bit in enumerate(initial_bitstring):
            if bit == "1":
                qc.x(i)

    qc.barrier()
    t_curr = 0
    for target in range(len(qc.qubits)):
        qc.h(target)
        for control in range(target + 1, n):
            angle = np.pi / (2 ** (control - target))
            qc.cp(angle, control, target)

            if t_curr >= t:
                return qc
            t_curr += 1

    for i in range(n // 2):
        qc.swap(i, n - 1 - i)

    return qc
