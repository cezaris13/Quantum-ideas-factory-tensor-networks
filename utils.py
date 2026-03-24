from qiskit.primitives import StatevectorSampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit import QuantumCircuit


def measure(qc: QuantumCircuit, shots:int, skip_qubits=[]):
    for i in range(qc.num_qubits):
        if i in skip_qubits:
           continue 
        qc.measure(i, i)
    sampler = StatevectorSampler()
    pm = generate_preset_pass_manager(optimization_level=1)
    isa = pm.run(qc)
    job = sampler.run([isa], shots=shots)
    pub = job.result()[0]
    return pub.data.c.get_counts()