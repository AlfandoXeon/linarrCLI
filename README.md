# PEMROGRAMAN LINEAR SOLUTION (PRO SUITE v2.0)

A luxurious, interactive CLI application for formulating, solving, and analyzing linear programming problems. Built with Python, Rich, MVC architecture, and an independent Two-Phase Simplex solver.

Developed by: **ALFANDOXEON**

---

## Features & Highlights

- **Luxurious & Colorful Terminal UI**:
  - Full-screen cyber-gold and royal neon aesthetic powered by the Rich engine.
  - Interactive **Navbar** with active module indicators and breadcrumb navigation.
  - Informative **Footer** with contextual shortcuts and real-time system status.
  - Executive **KPI Metric Cards** displaying optimal value ($Z^*$), solver status, pivot count, and model dimensions.
- **Two-Phase Simplex Solver**:
  - Solves Maximization and Minimization problems.
  - Supports mixed constraints (`<=`, `>=`, `=`) and negative right-hand-side (RHS) normalization.
  - Handles non-negative variables ($x \ge 0$) and unrestricted free variables ($x = x^+ - x^-$).
  - Explicit diagnostic statuses: `OPTIMAL`, `INFEASIBLE`, `UNBOUNDED`, `ITERATION_LIMIT`, and `NUMERICAL_FAILURE`.
- **Business & Sensitivity Analytics**:
  - Identifies **Binding Constraints (Bottlenecks)** where resources are 100% exhausted.
  - Identifies **Non-Binding Constraints (Idle/Slack)** with resource utilization percentages.
  - Variable contribution share breakdown to optimal objective value.
- **Curated Preset Problem Library**:
  - Includes 5 classic coursework scenarios: Furniture Mix, Hospital Diet, Chemical Blending, Infeasible Contradiction Study, and Unbounded Ray Study.
- **Interactive LP Theory & Guide**:
  - Built-in educational knowledge base explaining LP foundations, standard forms, Two-Phase Simplex mechanics, and sensitivity analysis.
- **Full Pivot Trace Transparency**:
  - Inspect Phase I and Phase II pivot iterations step-by-step (Entering variable, Leaving variable, Pivot element).
- **Built-in Quick Calculator (Kalkulator Matematika Cepat)**:
  - Safe arithmetic and math function evaluator (`+`, `-`, `*`, `/`, `//`, `%`, `**`, `sqrt`, `cbrt`, `log`, `abs`, `round`, `sin`, `cos`, `factorial`).
  - Automatic conversion to exact and mixed fractions (e.g. `15/4 [3 3/4]`), ideal for Simplex tableau pivot ratio calculations.
  - Calculation history log and `ans` memory for chained calculations.

---

## Requirements

- Python 3.10 or newer
- Windows 10/11 (or Linux/macOS with UTF-8 terminal)
- Internet connection for initial `rich` dependency installation

---

## Installation and Launch

### Quick Launch on Windows (Recommended)
Double-click `start.bat` in the project root directory. It automatically:
1. Configures UTF-8 encoding.
2. Initializes a local `.venv` if not already present.
3. Installs `rich` and registers the package in editable mode.
4. Starts the interactive CLI.

### Manual Launch via PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pls
```

Or run directly without console script registration:
```powershell
python -m pemrograman_linear_solution
```

---

## Testing

Run the full test suite (14 tests covering Two-Phase Simplex, bounds, numerical failure, validation, and preset scenarios):

```powershell
python -m unittest discover -s tests -v
```

---

## Developer & Credits

- **Developer**: ALFANDOXEON
- **GitHub**: [ALFANDOXEON](https://github.com/ALFANDOXEON)
- **Suite**: PEMROGRAMAN LINEAR SOLUTION PRO SUITE v2.0
