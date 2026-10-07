# PEMROGRAMAN LINEAR SOLUTION

An interactive, English-language CLI for entering and solving linear
programming problems. Built with Python, Rich, MVC separation, and a
self-contained two-phase simplex solver.

## Requirements

- Python 3.10 or newer
- Internet access for the initial Rich dependency installation

## Install and run

On Windows, double-click `start.bat` in the project root. On first launch it
creates a local `.venv`, installs Rich if needed, and starts the CLI.

To start it manually after installing the package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
pls
```

Alternatively, launch without installing the console command:

```powershell
python -m pemrograman_linear_solution
```

## Supported models

- Maximize or minimize one linear objective.
- Enter any number of decision variables (up to 20) and constraints (up to 50).
- Constraint relations: `<=`, `>=`, and `=`.
- Variable domains: non-negative (`x >= 0`, the default) or unrestricted.
- Optimal, infeasible, unbounded, iteration-limit, and numerical-failure
  statuses are distinguished.
- The solver reports variable values, objective value, constraint slack or
  surplus, and a readable two-phase simplex pivot trace.

Unrestricted variables are represented internally as the difference of two
non-negative variables. The solver uses floating-point arithmetic with a
`1e-9` tolerance and a finite iteration limit. As with other floating-point
simplex implementations, results for ill-conditioned models may be
numerically inconclusive.

Integer programming, nonlinear optimization, persistence, and custom finite
lower/upper bounds are not supported in this first release.

## Tests

Run the standard-library test suite from the project root:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```
