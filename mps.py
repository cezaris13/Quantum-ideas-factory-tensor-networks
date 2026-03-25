from qiskit import QuantumCircuit, transpile
import numpy as np
from qiskit_aer import AerSimulator
import grover
from qiskit.primitives import StatevectorSampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import matplotlib.pyplot as plt
import time

def get_mps_simulator(max_bond_dim: int = None,
                      truncation_threshold: float = 1e-8) -> AerSimulator:
    """
    Create an MPS AerSimulator instance.

    Parameters
    ----------
    max_bond_dim          : cap on bond dimension. None = exact (no truncation).
    truncation_threshold  : singular values below this are discarded.
    """
    options = {"method": "matrix_product_state",
               "matrix_product_state_truncation_threshold": truncation_threshold}
    if max_bond_dim is not None:
        options["matrix_product_state_max_bond_dimension"] = max_bond_dim
    return AerSimulator(**options)


def run_mps(qc: QuantumCircuit, shots: int = 10240,
            max_bond_dim: int = None,
            truncation_threshold: float = 1e-8) -> dict:
    """
    Transpile and run a circuit on the MPS simulator.

    Parameters
    ----------
    qc                   : circuit that already has measurements added.
    shots                : number of samples.
    max_bond_dim         : cap on bond dimension. None = exact.
    truncation_threshold : singular values below this are discarded.

    Returns
    -------
    counts : dict mapping bitstring -> count
    """
    simulator  = get_mps_simulator(max_bond_dim, truncation_threshold)
    transpiled = transpile(qc, simulator, optimization_level=1)
    job        = simulator.run(transpiled, shots=shots)
    return job.result().get_counts()


# ── measurement helpers ───────────────────────────────────────────────────────

def add_measurements(qc: QuantumCircuit, qubits: int) -> QuantumCircuit:
    """
    Return a copy of qc with measurements on the search qubits only
    (excludes ancilla at index qubits).
    """
    qc_m = qc.copy()
    # add classical register if not present
    if qc_m.num_clbits == 0:
        from qiskit.circuit import ClassicalRegister
        qc_m.add_register(ClassicalRegister(qubits, "c"))
    for i in range(qubits):
        qc_m.measure(i, i)
    return qc_m


def measure_mps(qc: QuantumCircuit, qubits: int, shots: int = 10240,
                max_bond_dim: int = None,
                truncation_threshold: float = 1e-8) -> dict:
    """
    Add measurements to qc and run on MPS simulator.
    This is the drop-in replacement for your original measure() function.
    """
    qc_measured = add_measurements(qc, qubits)
    return run_mps(qc_measured, shots, max_bond_dim, truncation_threshold)

def run_comparison(
    circuit_builder:  callable,
    target_bitstring: callable,
    k_values:         list[int],
    qubits:           int,
    shots:            int      = 10240,
    theory_fn:        callable = None,
    k_optimal:        int      = None,
    label_x:          str      = "Iterations k",
    label_prob:        str      = "P(target state)",
    title:            str      = "Statevector vs MPS",
) -> dict:

    sv_probs  = []
    mps_probs = []
    theory    = []

    for k in k_values:
        qc     = circuit_builder(k)
        target = target_bitstring(k)

        theory.append(theory_fn(k) if theory_fn is not None else None)

        #  add measurements 
        qc_measured = qc.copy()
        if qc_measured.num_clbits == 0:
            from qiskit.circuit import ClassicalRegister
            qc_measured.add_register(ClassicalRegister(qubits, "c"))
        for i in range(qubits):
            qc_measured.measure(i, i)

        #  StatevectorSampler 
        pm     = generate_preset_pass_manager(optimization_level=1)
        isa    = pm.run(qc_measured)
        counts = StatevectorSampler().run([isa], shots=shots).result()[0].data.c.get_counts()
        sv_probs.append(counts.get(target, 0) / shots)

        #  MPS
        mps_counts = measure_mps(qc, qubits, shots=shots)
        mps_probs.append(mps_counts.get(target, 0) / shots)

        theory_str = f"  theory={theory[-1]:.4f}" if theory_fn else ""
        print(f"k={k:2d}  sv={sv_probs[-1]:.4f}  "
            f"mps={mps_probs[-1]:.4f}{theory_str}")

    results = dict(sv_probs=sv_probs, mps_probs=mps_probs,
                theory=theory, k_values=list(k_values))

    _plot_comparison(results, k_optimal=k_optimal, label_x=label_x,
                    label_prob=label_prob, title=title,
                    shots=shots, qubits=qubits)
    return results


def _plot_comparison(results: dict, k_optimal: int = None,
                    label_x:   str = "Iterations k",
                    label_prob: str = "P(target state)",
                    title:     str = "Statevector vs MPS",
                    shots:     int = 10240,
                    qubits:    int = 0) -> None:

    k_values  = results["k_values"]
    sv_probs  = results["sv_probs"]
    mps_probs = results["mps_probs"]
    theory    = results["theory"]
    has_theory = any(t is not None for t in theory)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # ── panel 1: probability curves ────────────────────────────
    ax = axes[0]
    if has_theory:
        ax.plot(k_values, theory, label="Theory",
                linewidth=2, color="black")
    ax.plot(k_values, sv_probs,  label="Statevector",
            marker="o", linestyle="--", color="steelblue", markersize=6)
    ax.plot(k_values, mps_probs, label="MPS",
            marker="s", linestyle="--", color="tomato", markersize=6)
    if k_optimal is not None:
        ax.axvline(x=k_optimal, color="gray", linestyle=":",
                linewidth=1.5, label=f"k_optimal={k_optimal}")
    ax.set_xlabel(label_x, fontsize=12)
    ax.set_ylabel(label_prob, fontsize=12)
    ax.set_title(f"Success probability — {qubits} qubits", fontsize=13)
    ax.set_xticks(k_values)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ── panel 2: error vs theory or SV vs MPS diff ─────────────
    ax = axes[1]
    if has_theory:
        sv_error  = [abs(s - t) for s, t in zip(sv_probs,  theory)]
        mps_error = [abs(m - t) for m, t in zip(mps_probs, theory)]
        ax.plot(k_values, sv_error,  label="|Statevector − Theory|",
                marker="o", linestyle="--", color="steelblue", markersize=6)
        ax.plot(k_values, mps_error, label="|MPS − Theory|",
                marker="s", linestyle="--", color="tomato", markersize=6)
        ax.set_ylabel("Absolute error", fontsize=12)
        ax.set_title(f"Error vs theory — {qubits} qubits", fontsize=13)
    else:
        diff = [abs(s - m) for s, m in zip(sv_probs, mps_probs)]
        ax.plot(k_values, diff, label="|Statevector − MPS|",
                marker="o", linestyle="--", color="purple", markersize=6)
        ax.set_ylabel("Absolute difference", fontsize=12)
        ax.set_title(f"SV vs MPS agreement — {qubits} qubits", fontsize=13)
    if k_optimal is not None:
        ax.axvline(x=k_optimal, color="gray", linestyle=":",
                linewidth=1.5, label=f"k_optimal={k_optimal}")
    ax.set_xlabel(label_x, fontsize=12)
    ax.set_xticks(k_values)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.suptitle(f"{title}  |  qubits={qubits}  |  shots={shots}",
                fontsize=12, y=1.02)
    plt.tight_layout()
    plt.show()

def run_scaling_comparison(
    circuit_builder: callable,
    qubit_sizes:     list[int],
    k_fixed:         int   = 1,
    shots:           int   = 1024,
    title:           str   = "MPS vs Statevector — scaling with qubit count",
) -> dict:
    """
    Generic runtime scaling comparison between StatevectorSampler and MPS
    across increasing qubit counts.

    Parameters
    ----------
    circuit_builder : callable(n) -> QuantumCircuit
                      Builds the circuit for n qubits.
                      Must NOT include measurements.
    qubit_sizes     : list of qubit counts to sweep over.
    k_fixed         : fixed iteration count (informational, used by caller
                      when building the circuit).
    shots           : number of samples per run.
    title           : suptitle string.

    Returns
    -------
    results : dict with keys sv_times, mps_times, sv_failed, qubit_sizes
    """
    sv_times  = []
    mps_times = []
    sv_failed = []

    for n in qubit_sizes:
        qc = circuit_builder(n)

        # ── StatevectorSampler ──────────────────────────────────
        try:
            qc_m = qc.copy()
            if qc_m.num_clbits == 0:
                from qiskit.circuit import ClassicalRegister
                qc_m.add_register(ClassicalRegister(n, "c"))
            for i in range(n):
                qc_m.measure(i, i)
            pm  = generate_preset_pass_manager(optimization_level=1)
            isa = pm.run(qc_m)
            t0  = time.perf_counter()
            StatevectorSampler().run([isa], shots=shots).result()
            sv_times.append(time.perf_counter() - t0)
            sv_failed.append(False)
        except Exception as e:
            print(f"n={n}  SV failed: {e}")
            sv_times.append(None)
            sv_failed.append(True)

        # ── MPS ─────────────────────────────────────────────────
        t0 = time.perf_counter()
        measure_mps(qc, n, shots=shots)
        mps_times.append(time.perf_counter() - t0)

        sv_str = f"{sv_times[-1]:.3f}s" if not sv_failed[-1] else "FAILED"
        print(f"n={n:2d}  sv={sv_str:>10}  mps={mps_times[-1]:.3f}s")

    results = dict(sv_times=sv_times, mps_times=mps_times,
                   sv_failed=sv_failed, qubit_sizes=qubit_sizes)

    _plot_scaling(results, k_fixed=k_fixed, shots=shots, title=title)
    return results


def _plot_scaling(results: dict, k_fixed: int = 1,
                  shots: int = 1024,
                  title: str = "MPS vs Statevector — scaling with qubit count") -> None:
    """Internal plot helper — called automatically by run_scaling_comparison."""
    qubit_sizes = results["qubit_sizes"]
    sv_times    = results["sv_times"]
    mps_times   = results["mps_times"]
    sv_failed   = results["sv_failed"]

    valid_n  = [n for n, f in zip(qubit_sizes, sv_failed) if not f]
    valid_sv = [t for t, f in zip(sv_times,    sv_failed) if not f]
    speedup  = [s / m for s, m, f in zip(sv_times, mps_times, sv_failed) if not f]

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # ── left: raw runtime ───────────────────────────────────────
    ax = axes[0]
    ax.plot(valid_n,     valid_sv,  marker="o", color="steelblue",
            linewidth=2, label="Statevector")
    ax.plot(qubit_sizes, mps_times, marker="s", color="tomato",
            linewidth=2, label="MPS (exact)")
    if any(sv_failed):
        first_fail = qubit_sizes[sv_failed.index(True)]
        ax.axvline(x=first_fail, color="red", linestyle="--",
                   linewidth=1.5, label=f"SV fails at n={first_fail}")
    ax.set_xlabel("Number of qubits n", fontsize=12)
    ax.set_ylabel("Wall-clock time (s)", fontsize=12)
    ax.set_title(f"Runtime vs qubit count  (k={k_fixed}, shots={shots})", fontsize=13)
    ax.set_xticks(qubit_sizes)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ── right: speedup bars ─────────────────────────────────────
    ax     = axes[1]
    colors = ["tomato" if s > 1 else "steelblue" for s in speedup]
    ax.bar(valid_n, speedup, color=colors, alpha=0.8, edgecolor="white")
    ax.axhline(y=1.0, color="black", linestyle="--",
               linewidth=1.5, label="Breakeven (speedup=1×)")
    for n, s in zip(valid_n, speedup):
        ax.annotate(f"{s:.1f}×", xy=(n, s), xytext=(0, 5),
                    textcoords="offset points", ha="center", fontsize=8)
    ax.set_xlabel("Number of qubits n", fontsize=12)
    ax.set_ylabel("Speedup (SV time / MPS time)", fontsize=12)
    ax.set_title("MPS speedup over Statevector", fontsize=13)
    ax.set_xticks(valid_n)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.suptitle(f"{title}  |  shots={shots}", fontsize=12, y=1.02)
    plt.tight_layout()
    plt.show()

    