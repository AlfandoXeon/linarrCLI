# IMPLEMENTATION PLAN

## 1. Goal and release boundary

Build a reliable, interactive Python CLI for creating and solving linear
programming models used in coursework. The application UI is English-only,
uppercase, emoji-free, and rendered with Rich. Use MVC and object-oriented
design without coupling the mathematical solver to terminal presentation.

The first release should support a user-defined linear objective, any
reasonable user-selected count of variables and constraints, maximization or
minimization, `<=`, `>=`, and `=` constraints, and explicitly selected variable
domains. Non-negative variables are the default. Return an optimal solution or
a clear non-optimal status; never disguise infeasible, unbounded, or
numerically inconclusive cases as success.

Integer programming, nonlinear models, a GUI, persistence, and guarantees for
ill-conditioned inputs are out of scope for this release.

## 2. Proposed structure

```text
src/
  pemrograman_linear_solution/
    __main__.py
    app.py
    controllers/
      problem_controller.py
    models/
      problem.py
      result.py
    services/
      solver.py
      simplex.py
      standard_form.py
    views/
      console.py
      screens.py
      prompts.py
    validation/
      inputs.py
tests/
  unit/
  integration/
```

Keep modules small and introduce no layer that does not have a clear
responsibility:

- **Model:** typed representations for variables, objective, constraints,
  domains, problem, solver status, and solution.
- **View:** Rich screens, prompts, tables, header/footer, terminal clearing,
  and uppercase application-owned text.
- **Controller:** navigation and the create-review-edit-solve-result workflow.
- **Solver service:** normalize supported models and invoke the algorithm;
  return typed results, not terminal output.
- **Validation:** reusable parsing and domain checks with actionable errors.

Use the repository's existing conventions if implementation reveals existing
project structure or tooling; do not force this proposed layout if it conflicts.

## 3. Delivery phases

### Phase 1 — Project foundation

- Inspect available Python version and establish packaging, entry point, and
  test runner using the lightest suitable setup.
- Add Rich and define the package layout and public application entry point.
- Add a basic application loop with main menu, screen transitions, shared
  header/footer, terminal clearing, and graceful exit.
- Ensure layout responds to terminal width and remains understandable without
  color.

**Acceptance:** The app launches from its documented command, navigates between
screens, clears/redraws on transitions, and does not crash on a narrow terminal
or normal exit.

### Phase 2 — Domain model and input workflow

- Model variables, objective direction and coefficients, constraints, and
  variable domains with typed structures.
- Prompt for variable and constraint counts, names, coefficients, relation
  operators, right-hand-side values, and domains/bounds.
- Validate finite numeric values, positive and reasonable counts, unique or
  unambiguous labels, valid operators, and consistent model dimensions.
- Preserve valid entries when a prompt is corrected; provide a review screen
  with edit/restart choices before solving.

**Acceptance:** Valid models can be entered and reviewed; invalid entries show
uppercase English guidance and can be corrected without silently changing the
model.

### Phase 3 — Solver and mathematical correctness

- Specify supported domain/bound semantics, numerical tolerance policy, and
  unsupported-input behavior before implementing transformations.
- Normalize maximization/minimization and mixed `<=`, `>=`, `=` constraints
  into the solver's internal representation.
- Implement a two-phase simplex method (or a verified compatible implementation)
  for feasible models, including artificial variables where required.
- Detect and return distinct statuses for optimal, infeasible, unbounded,
  iteration limit, and numerical failure.
- Keep pivot/iteration details available as structured data so the UI can show
  an explanation without embedding presentation logic in the solver.

**Acceptance:** Solver tests cover known optima, minimization, each constraint
direction, equality constraints, degenerate cases, infeasibility,
unboundedness, and domain/bound handling. Returned solutions satisfy the
original model within the documented tolerance.

### Phase 4 — Results and end-to-end workflow

- Display the status, objective value, decision-variable values, and a
  readable summary of constraints/slack or surplus where applicable.
- Explain non-optimal statuses and offer a path to edit the model or start
  another one.
- Keep all application-owned visible strings uppercase and English; preserve
  mathematical identifiers entered by the user.
- Ensure every screen has consistent branding, navigation hints, and footer.

**Acceptance:** A user can create, review, solve, inspect, edit, and solve a
second model in one run. No status is presented as an optimal solution unless
the solver verified it.

### Phase 5 — Verification and documentation

- Run formatting/linting, type checking if configured, unit tests, and CLI
  integration tests.
- Add tests for malformed input, end-of-input/interrupt behavior, terminal
  dimensions, and every solver status.
- Document installation, launch, supported model/domain semantics, numerical
  tolerances and limitations, and example usage.

**Acceptance:** Fresh setup instructions work; targeted and full test suites
pass; documented features and solver limitations match actual behavior.

## 4. Cross-cutting quality requirements

- Keep the solver deterministic and independently unit-testable.
- Reject NaN and infinite coefficients/RHS values and guard against invalid
  dimensions before solving.
- Use explicit iteration limits and numerical tolerances; surface when either
  prevents a reliable conclusion.
- Avoid broad exception handling and success-shaped fallbacks. Handle expected
  input errors at the prompt/controller boundary; report unexpected failures
  clearly without exposing an incorrect result.
- Test mathematical outcomes against hand-computed examples and verify every
  reported solution against the original constraints.

## 5. First-release decisions

- Use a self-contained two-phase tableau simplex solver and report pivot steps
  for coursework transparency.
- Support non-negative and unrestricted variables. An unrestricted variable is
  represented as the difference of two non-negative variables.
- Do not support custom finite lower/upper bounds in the first release.
- Use a floating-point tolerance of `1e-9` and a maximum of 10,000 simplex
  pivots; report numerical failure or iteration limit instead of claiming an
  optimal solution when verification does not succeed.
- If a course requires a particular tableau notation, the pivot trace can be
  aligned with that convention in a later iteration without changing the CLI
  model or solver interface.
