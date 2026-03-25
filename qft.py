from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
import numpy as np
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector, partial_trace, entropy

n=15 #number_of_qubits
def qft(noq):
    qr = QuantumRegister(noq)
    #cr = ClassicalRegister(noq)
    qc = QuantumCircuit(qr)#QuantumCircuit(qr, cr)

    for target in range(len(qr)): #from qubit zero to number of qubits

        qc.h(qr[target])
        for control in range(target+1, noq):
            angle=np.pi/(2**(control-target))
            qc.cp(angle, qr[control], qr[target])

        
    #swap afterwards
    for i in range(noq//2):
        qc.swap(qr[i], qr[noq-1-i])

    #qc.measure(qr, cr)

    return qc

qc = qft(n)

qc.draw(output="mpl",style="clifford") #minimalistischer qc.draw()
