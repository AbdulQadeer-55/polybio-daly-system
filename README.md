# Weighted Prioritized Pairwise Generator

![Language](https://img.shields.io/badge/language-Python-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Python implementation of **Prioritized Interaction Testing** based on the research by **Bryce & Colbourn (2006)**.

This tool generates **pairwise test suites** that prioritize the most important interactions early, ensuring maximum coverage even under tight time or budget constraints.

---

## 📌 Overview

Traditional pairwise testing treats all interactions as equal. However, in real-world software testing, some configurations are critical (high risk), while others are rarely used.

This project implements the **Weighted Deterministic Density Algorithm (DDA)** to:

1. **Prioritize** – Ensure high-weight pairs are covered in the first few tests.  
2. **Optimize** – Maximize *Prefix Quality* (cumulative weight covered early).  
3. **Constrain** – Handle:
   - **Seeds** (pre-existing tests)
   - **Avoids** (forbidden or discouraged combinations)

---

## 🚀 Features

- **Weighted Prioritization**  
  Supports importance weights from `-1.0` (Avoid) to `1.0` (Critical).

- **Greedy DDA Strategy**  
  Implements a "one-test-at-a-time" greedy generation approach for efficiency.

- **Constraint Handling**
  - **Seeds:** Respects pre-existing tests to avoid redundant coverage.
  - **Avoids:** Handles soft constraints using negative weights.

- **Visual Validation**
  - Automatically generates **Cumulative Weight graphs** to demonstrate prioritization efficiency.

- **Real-World Case Study**
  - Includes a runnable **Web Services Reliability** example (Rain / Wind / Temperature factors).

---

## 📂 Project Structure

```text
prioritized-pairwise-gen/
├── src/
│   ├── generator.py       # Core Weighted DDA Algorithm
│   ├── metrics.py         # Evaluation metrics & CSV export
│   └── weight_utils.py    # Utilities for weight distributions (Equal, 50/50, Random)
├── examples/
│   ├── demo_run.py                # Replicates Table 5 from the paper
│   ├── case_study_webservices.py  # Web Services Reliability case study
│   └── plot_results.py            # Generates cumulative weight visualization
├── tests/
│   └── test_generator.py          # Unit tests (Seeds & Avoids)
├── requirements.txt
└── README.md
````

---

## 🛠️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/prioritized-pairwise-gen.git
cd prioritized-pairwise-gen
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📖 Usage

### 1️⃣ Basic Demo (Table 5 Replication)

Run the standard demo to verify the algorithm against the paper's example:

```bash
python3 examples/demo_run.py
```

**Output:**
Generates a test suite and saves results to `demo_results.csv`.

---

### 2️⃣ Web Services Case Study

Generate prioritized tests for Rain, Temperature, and Wind forecasting services based on reliability ratings:

```bash
python3 examples/case_study_webservices.py
```

---

### 3️⃣ Visual Proof – Generate Graph

Generate the Cumulative Weight Curve:

```bash
python3 examples/plot_results.py
```

**Output:**
Creates:

```
examples/cumulative_weight_curve.png
```

**Interpretation:**
The weighted curve rises significantly faster than a linear baseline, proving that the algorithm prioritizes important interactions early.

---

## 🧪 Testing

Run automated unit tests to verify that constraints (Seeds and Avoids) are strictly respected:

```bash
python3 -m pytest tests/test_generator.py
```

---

## 📄 Reference

Bryce, R. C., & Colbourn, C. J. (2006).
*Prioritized interaction testing for pair-wise coverage with seeding and constraints.*
Information and Software Technology, 48(10), 960–970.

---

## 👨‍💻 Author

**Abdul Qadeer**

```
