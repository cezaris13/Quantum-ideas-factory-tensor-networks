from dataclasses import dataclass, field
from qiskit import QuantumCircuit
from typing import Callable


@dataclass
class Algorithm:
    key: str  # unique id, used in data keys + JS
    label: str  # display name for UI
    color: str  # accent hex for button / gradient
    colorscale: list[list]  # Plotly colorscale stops
    build_circuit: Callable[[int, int], QuantumCircuit]  # (n, t) -> circuit
    extra_qubits: int = 1  # ancilla / coin qubits beyond n

    # sweep ranges — override per algorithm
    n_range_nt: range = field(default_factory=lambda: range(2, 9))
    t_range_nt: range = field(default_factory=lambda: range(0, 13))
    n_range_nj: range = field(default_factory=lambda: range(2, 9))
    t_fixed_nj: int = 3
    n_fixed_jt: int = 7
    t_range_jt: range = field(default_factory=lambda: range(0, 15))
