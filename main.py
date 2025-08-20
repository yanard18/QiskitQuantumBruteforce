from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseOracle, GroverOperator
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator # api calls
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.transpiler import generate_preset_pass_manager
from matplotlib import pyplot as plt

# --- User inputs ---
SECRET = input("Enter the secret bitstring (e.g., '11'): ").strip()
n_qubits = len(SECRET)

mode = input("Choose execution mode ('sampler' for classical counts, 'estimator' for expectation values): ").strip().lower()
if mode not in ['sampler', 'estimator']:
    raise ValueError("Invalid mode. Choose 'sampler' or 'estimator'.")

# --- Build Grover's Oracle ---
expression = " & ".join([f"x{i}" if bit == "1" else f"~x{i}" for i, bit in enumerate(SECRET)])
oracle = PhaseOracle(expression)
grover_op = GroverOperator(oracle)


# --- Build Grover's Circuit ---
qc = QuantumCircuit(n_qubits) # so we go with 2 qbits
qc.h(range(n_qubits)) # puts all qbits into superposition
qc.compose(grover_op, inplace=True)
if mode == 'sampler':
    qc.measure_all() # CRITIC: Must include this to get classical counts

# Return a drawing of the circuit using MatPlotLib ("mpl").
# These guides are written by using Jupyter notebooks, which
# display the output of the last line of each cell.
# If you're running this in a script, use `print(qc.draw())` to
# print a text drawing.
print(qc.draw())

# --- Observables for estimation ---
# Here we just use Z for all qubits as a simple example
observables_labels = [f"{'Z'*i + 'I'*(n_qubits-i)}" for i in range(1, n_qubits+1)]
observables = [SparsePauliOp(label) for label in observables_labels]
 
service = QiskitRuntimeService()
backend = service.least_busy(simulator=False, operational=True)

if mode == 'sampler':
    qc_transpiled = transpile(qc, backend)
    sampler = Sampler(mode=backend)
    job = sampler.run([qc_transpiled], shots=1024)
    result = job.result()
    counts = result[0].data.meas.get_counts()
    print("============ Classical counts ===========")
    print(counts)


elif mode == 'estimator':
    # ------------------------------- ISA CIRCUIT VERSION -----------------------------------
    # Convert to an ISA circuit and layout-mapped observables.
    # Transpiling (convert circuit into a form that can a specific backend service run)
    # Maps qubits in your circuit to the physical qubits of the device.
    # Replaces unsupported gates with sequences of supported ones.
    # Optimizes the circuit to reduce gate count and depth, which helps reduce errors.
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1) # 
    isa_circuit = pm.run(qc)

    print("ISA circuit:")
    print(isa_circuit.draw())

    estimator = Estimator(mode=backend)
    estimator.options.resilience_level = 1
    estimator.options.default_shots = 5000

    mapped_observables = [
        observable.apply_layout(isa_circuit.layout) for observable in observables
    ]

    # One pub, with one circuit to run against five different observables.
    job = estimator.run([(isa_circuit, mapped_observables)])
    
    # Use the job ID to retrieve your job data later
    print(f">>> Job ID: {job.job_id()}")
    
    # This is the result of the entire submission.  You submitted one Pub,
    # so this contains one inner result (and some metadata of its own).
    job_result = job.result()
    
    # This is the result from our single pub, which had six observables,
    # so contains information on all six.
    pub_result = job.result()[0]


    values = pub_result.data.evs
    errors = pub_result.data.stds
    
    # plotting graph
    plt.plot(observables_labels, values, "-o")
    plt.xlabel("Observables")
    plt.ylabel("Values")
    plt.show()