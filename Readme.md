# Entanglement Entropy in Quantum Algorithms

This project investigates the entanglement structure of quantum algorithms — specifically **Grover's search algorithm**, **discrete-time quantum random walk** and **Quantum Fourier Transform** — by computing the von Neumann entropy across different bipartitions of the qubit register.

Developed during the [**Quantum Ideas Factory 2026**](https://www.cesq.eu/quantum-ideas-factory-2026/), a scientific hackathon organized by the European Center for Quantum Sciences (CESQ) in Strasbourg, France (March 23–26, 2026). The project falls under the challenge topic *"When is it possible to run quantum circuits on classical computers?"*, mentored by Jérôme Dubail (Strasbourg).

## Overview

The central question is: **how does entanglement grow and distribute itself in structured quantum circuits?** Understanding entanglement entropy profiles helps clarify when quantum circuits can be efficiently simulated classically (e.g., via tensor network / MPS methods) and when they cannot.

We sweep over three key parameters and measure entanglement:

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| Qubits | `n` | Number of qubits in the register |
| Iteration | `t` | Number of Grover oracle calls or walk steps |
| Bipartition | `j` | Position of the entanglement cut (left subsystem = qubits 0…j−1) |

## Algorithms

### Grover's Search

Constructs the standard Grover circuit with `n` search qubits, one ancilla, and `k` applications of the Grover operator (oracle + diffusion). The oracle marks a single computational basis state via a multi-controlled-X gate with appropriate X flips.

### Discrete-Time Quantum Walk

Implements a coined quantum walk on a cycle of 2ⁿ nodes. The coin is a Hadamard gate on a dedicated coin qubit, and the shift operator conditionally increments or decrements the position register using multi-controlled-X ladders. The coin is initialized in the symmetric state (H followed by S gate) to produce a balanced distribution.

## Entropy Analysis

For each algorithm the notebook explores three slices through the `(n, t, j)` parameter space:

- **S vs j** (fixed n, t) — entropy profile across all bipartition cuts for a single circuit instance
- **S vs t** (fixed n, j) — how entanglement at a chosen cut evolves with circuit depth
- **S vs n** (fixed t, j = n//2) — scaling of mid-chain entanglement with system size, for one or multiple values of t

All entropy computations use Qiskit's `Statevector` simulation followed by `partial_trace` and `entropy` (base-2).

## Installation:

```bash
pip install qiskit numpy matplotlib pylatexenc jinja2
```

## Team
 
- **Pijus Petkevičius** — University of Copenhagen/ Tehchnical University of Denmark
- **Merve Rumelli** — Sorbonne université
- **Trinity Hopp** — Friedrich Schiller University of Jena
- **Francesco Mainardis** — École normale supérieure, Paris 
 

## Acknowledgements

This project was developed at the [Quantum Ideas Factory 2026](https://www.cesq.eu/quantum-ideas-factory-2026/), organized by CESQ (European Center for Quantum Sciences) at the University of Strasbourg, within the [DigiQ](https://digiq.eu/) student network. 