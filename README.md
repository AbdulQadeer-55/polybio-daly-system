# Weighted Prioritized Pairwise Generator

![Language](https://img.shields.io/badge/language-Python-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

[cite_start]A Python implementation of **Prioritized Interaction Testing** based on the research by **Bryce & Colbourn (2006)** [cite: 59-67]. This tool generates pairwise test suites that prioritize the most important interactions early, ensuring maximum coverage even under tight time or budget constraints.

## 📌 Overview

Traditional pairwise testing treats all interactions as equal. However, in real-world software testing, some configurations are critical (high risk), while others are rarely used.

[cite_start]This tool implements the **Weighted Deterministic Density Algorithm (DDA)** [cite: 296-300] to:
1.  [cite_start]**Prioritize:** Ensure high-weight pairs are covered in the first few tests [cite: 74-75].
2.  [cite_start]**Optimize:** Maximize the "Prefix Quality" (cumulative weight covered early)[cite: 21, 39].
3.  [cite_start]**Constrain:** Handle **Seeds** (pre-existing tests) and **Avoids** (forbidden combinations) [cite: 227-240].

## 🚀 Features

* [cite_start]**Weighted Prioritization:** Supports importance weights from `-1.0` (Avoid) to `1.0` (Critical) [cite: 162-164].
* [cite_start]**Greedy DDA Strategy:** Implements the "one-test-at-a-time" greedy approach for efficient generation[cite: 296].
* **Constraint Handling:**
    * [cite_start]**Seeds:** Respects pre-existing tests to avoid redundant coverage[cite: 227].
    * [cite_start]**Avoids:** Handles soft constraints by assigning negative weights [cite: 239-240].
* [cite_start]**Visual Validation:** Automatically generates "Cumulative Weight" graphs to prove prioritization efficiency (matches Figure 3 in the paper)[cite: 416].
* [cite_start]**Real-World Case Study:** Includes a runnable script for the **Web Services Reliability** example (Rain/Wind/Temp factors) [cite: 213-223].

## 📂 Project Structure

```text
prioritized-pairwise-gen/
├── src/
│   ├── generator.py       # Core Weighted DDA Algorithm
│   ├── metrics.py         # Evaluation metrics & CSV Export
│   └── weight_utils.py    # Utilities to generate weight distributions (Equal, 50/50, Random)
├── examples/
│   ├── demo_run.py        # Replicates Table 5 from the paper
│   ├── case_study_webservices.py  # Web Services Reliability Case Study
│   └── plot_results.py    # Generates the "Cumulative Weight" visualization
├── tests/
│   └── test_generator.py  # Unit tests for seeds and avoids
├── requirements.txt
└── README.md
🛠️ Installation
Clone the repository:

Bash
git clone [https://github.com/YOUR_USERNAME/prioritized-pairwise-gen.git](https://github.com/YOUR_USERNAME/prioritized-pairwise-gen.git)
cd prioritized-pairwise-gen
Install dependencies:

Bash
pip install -r requirements.txt
📖 Usage
1. Basic Demo (Table 5 Replication)
Run the standard demo to verify the algorithm against the paper's specific example:

Bash
python3 examples/demo_run.py
Output: Generates a test suite and saves it to demo_results.csv.

2. Web Services Case Study
Run the "Reliability" case study, which generates tests for Rain, Temperature, and Wind forecasting services based on their reliability ratings :

Bash
python3 examples/case_study_webservices.py
3. Visual Proof (Generate Graph)
To see the prioritization in action, generate the Cumulative Weight Curve:

Bash
python3 examples/plot_results.py
Output: Creates examples/cumulative_weight_curve.png.


Interpretation: The blue curve (Weighted) will rise significantly faster than the linear baseline, proving that the algorithm successfully prioritizes important tests.

🧪 Testing
Run the automated unit tests to verify that constraints (Seeds and Avoids) are strictly respected:

Bash
python3 -m pytest tests/test_generator.py
📄 Reference
Bryce, R. C., & Colbourn, C. J. (2006). Prioritized interaction testing for pair-wise coverage with seeding and constraints. Information and Software Technology, 48(10), 960-970. 

Developed by: Abdul Qadeer