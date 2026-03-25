from qiskit import QuantumCircuit, QuantumRegister
import numpy as np

def qft(n, t):
    qr = QuantumRegister(n)
    qc = QuantumCircuit(qr)
    
    t_curr = 0
    for target in range(len(qr)): 
        qc.h(qr[target])
        for control in range(target+1, n):
            angle=np.pi/(2**(control-target))
            qc.cp(angle, qr[control], qr[target])
        
        if t_curr >= t:
            return qc

        t_curr +=1
        
    for i in range(n//2):
        qc.swap(qr[i], qr[n-1-i])

    return qc