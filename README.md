# Quantum Brute-Force with Grover's Algorithm

This project demonstrates a **quantum brute-force search** using **Grover's Algorithm** with Qiskit. It allows you to find a secret bitstring by exploring all possibilities faster than classical brute-force methods.

---

# Quantum Brute-Force with Grover's Algorithm

**Description:**  
This project implements a quantum brute-force search using **Grover's Algorithm**. Given a secret bitstring, the code builds a quantum circuit to find it faster than classical brute-force methods. It supports two execution modes: `sampler` (classical measurement counts) and `estimator` (expectation values of observables).

## Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yanard18/QiskitQuantumBruteforce.git
cd QiskitQuantumBruteforce
```

2. **Create a virtual environment and install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. **Set up IBM Quantum account (for API access):**

Create a new file as `api.py` and put inside:

```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_API_TOKEN")
```

Obviously you should write your own API token. This will save your authentication information to your local device.

Run the python code:

```bash
python api.py
```

## Quick Start

1. **Run the script:**

```python
python main.py
```

2. **Example Inputs:**

```out
Enter the secret bitstring (e.g., '11'): 11
Choose execution mode ('sampler' for classical counts, 'estimator' for expectation values): sampler

  grover_op = GroverOperator(oracle)
        ┌───┐┌────┐ ░ ┌─┐
   q_0: ┤ H ├┤0   ├─░─┤M├───
        ├───┤│  Q │ ░ └╥┘┌─┐
   q_1: ┤ H ├┤1   ├─░──╫─┤M├
        └───┘└────┘ ░  ║ └╥┘
meas: 2/═══════════════╩══╩═
                       0  1

============ Classical counts ===========
{'11': 979, '01': 27, '00': 1, '10': 17}
```

As seen, after 1024 attempt of measuring we found `11` bits 979 times 

## About Grover's Algorithm

Grover's Algorithm is a quantum search algorithm that amplifies the probability of the correct solution while suppressing incorrect states.

- Each possible solution is represented as a quantum state vector.
- An oracle marks the correct state without revealing it.
- Repeated amplitude amplification increases the chance of measuring the correct answer.

For a clear visual explanation, see the excellent video by 3Blue1Brown: [Grover’s Algorithm explained](https://www.youtube.com/watch?v=RQWpF2Gb-gU)

## Losing Precision

When increasing the number of qubits, the probability of measuring the correct state decreases unless the number of Grover iterations is adjusted:

Example: For a 4-qubit secret 1111 with 1000 measurements, the correct outcome may only appear ~183 times.

This happens because:

- Each additional qubit increases the search space exponentially.
- The algorithm is probabilistic, and measurement is non-deterministic.
- More qubits introduce more noise and potential error.

> Tip: More iterations can improve precision, but too many iterations can also overshoot the optimal amplitude.