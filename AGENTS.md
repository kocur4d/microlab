# AGENTS.md

## Git workflow

Make code changes freely, but never create Git commits, merge branches, or push branches. The user handles all Git commits, merges, and pushes manually.

## Goal

Write code that is easy to change, easy to read, and easy to test — in that priority order.

## Engineering journal

- Keep learning-session notes in `docs/journal/YYYY-MM-DD-short-topic.md`, following [the journal format](docs/journal/README.md). Create entries only when the user explicitly asks (for example, "add a journal note" or "journal this"), never automatically after a task.
- On request, review the current session's work and discussion and existing entries. Create a separate file for each learning session, or update its existing entry when extending the same session; avoid duplicate notes.
- Record the work, lessons, important decisions and their reasoning, what worked or failed, unresolved questions, and the next concrete step. Clearly distinguish verified results from assumptions and planned work; do not invent missing details.
- Keep entries concise, technical, and easy to scan, using short sections, bullets, and code snippets only where useful. Capture meaningful lessons and decisions rather than a transcript.
- When the user asks to resume, read the latest dated journal entry to establish where work stopped and check the current project state before relying on its recorded status.

## General design principles

**Single responsibility.** Each function does one thing. A function that validates _and_ renders is two functions. A function that transforms data _and_ formats strings is two functions.

**Separate concerns explicitly:**

- _Validation_ — at the entry point. Throw on bad input; never silently return null for data that should not be absent. In Python, raise an appropriate exception for invalid input or violated invariants.
- _Computation_ — pure functions that take data in and return data out, with no side effects. These are easy to test in isolation. Where mutation or side effects are appropriate (including efficient array operations), keep them explicit and separate from validation and presentation.
- _Presentation_ — string or UI rendering should be the final step, separated from the logic that produced the data.

**Compose from small pieces.** Build complex behaviour by composing small, named, testable functions. A caller should read the entry-point function as a sequence of named steps, not a single monolithic block.

**Small modules with clear responsibilities.** Keep files focused and group related files by concern. In TypeScript, prefer one public export per file, supported by at most a few small private helpers; when a file grows beyond this, split it and group related files with a barrel `index.ts`. In Python, treat one public concept per module as a useful default, not a strict rule: keep closely related functions and types together when that makes the module easier to understand. In either language, group helpers by concern rather than interleaving unrelated code.

**Check before writing.** Before implementing a utility, search the codebase for an equivalent. Before defining a new type, check whether an equivalent already exists. Prefer existing shared helpers over fresh inline equivalents.

**No redundant derived fields.** Before adding a field to a type or object, check whether it is derivable from a field already present — for example, a count alongside a list, a boolean alongside a nullable value, or a formatted string alongside raw data. Avoid storing both unless there is a concrete reason.

**Don't create thin wrappers.** A function that only renames a single expression, without adding logic, validation, or a meaningful abstraction, removes information rather than adding it. Inline the expression instead: a caller reading `query.findValue(val, i)?.string()` understands the API; reading `resolveString(val, i)` does not.

**Name identifiers after the concept, not the data structure.** When a concept changes during development or refactoring — for example, a table rendering becomes a list rendering — update every associated name: types, variables, and functions. A variable called `rows` that holds rendered lines, or a type called `DamageTable` that now represents a flat list, misleads future readers. Rename before the PR.

**Assert invariant violations.** When a condition must be true for code to be correct, make the failure explicit and include useful context; do not silently return null or otherwise hide the bug. Use the language-appropriate exception or assertion. This does not mean converting expected operational or domain failures into invariant exceptions: represent those explicitly at the relevant boundary.

## TypeScript conventions

**Guard clauses over nesting.** Prefer early returns over nested `if`/`else`. Each guard removes one level of indentation and makes the happy path obvious.

**Check noteworthy cases first.** When a function has one special/error case and one common/default case, check for the special case and return it immediately; put the common case last. Don't invert the condition to dispatch on the common case first and let the special case fall through to the end — a reader scanning top-to-bottom expects the interesting case up front.

```ts
// Prefer: special case first, default falls through to the end
const validate = (x: Thing): Error[] => {
  if (isBroken(x)) return [{ message: "..." }];
  return [];
};
// Avoid: common case first, special case buried at the end
const validate = (x: Thing): Error[] => {
  if (!isBroken(x)) return [];
  return [{ message: "..." }];
};
```

**Prefer functional transforms over imperative accumulation.** Use `map`, `filter`, and `flatMap` rather than `for` loops that push into an array. Express data transformations as pipeline steps, not imperative assembly. Reserve `for` loops for side effects or cases where early exit genuinely simplifies the code.

**Avoid inline type predicates in filters.** Prefer named helpers instead:

- To filter out `null | undefined`, use a named `isDefined` helper (define it once in a shared utils module) rather than writing `(x): x is T => x != null` inline each time.
- To combine a map and a filter in one pass, `flatMap(x => condition ? [value] : [])` is a readable alternative.
- When discriminating a union, trust TypeScript's narrowing: `.filter(a => a.type === 'critical')` narrows the array type automatically in TS 5.5+ — never write an explicit `(a): a is T =>` predicate for a simple discriminant check.
- Before writing any `(x): x is T =>` predicate in a filter, verify the array element type actually includes non-`T` values — check the type it was declared with. If the array is already `T[]`, a plain arrow function is correct and the predicate is misleading.

**Extract type guards for repeated casts.** When you cast the same union variant in more than one place, extract a named type guard instead. Duplicated casts are silent divergence points if the shape changes:

```ts
// Instead of casting the same shape twice:
build.modifiers as { type: "buff"; sourceSkillIds: string[] };
// Extract once:
type BuffModifier = { type: "buff"; sourceSkillIds: string[] };
function isBuffModifier(m): m is BuffModifier {
  return m.type === "buff";
}
```

**Name multi-field return types — when there's something to check them against.** For functions with branching bodies or explicit `return` statements, define a named `type <FunctionName>Result` above the function and use it as the return-type annotation; drafting the contract first has real value when there's logic to verify against it. For a single-expression function that just assembles an object literal from already-typed sub-expressions (`map`/`reduce`/`flatMap` over helpers that already have their own return types), skip the annotation — TypeScript already infers the exact shape, and a named type would only duplicate what's already checked.

```ts
// Multi-statement body: name the type, draft the contract up front
type ApplyModifiersResult = { total: DamageTotal; skippedModifierIds: string[] };
function applyModifiers(base: DamageTotal, modifiers: Modifier[]): ApplyModifiersResult { ... }
// Single expression, already inferred from typed helpers: no annotation needed
const defineModifierSet = (build: Build, selected: SelectedModifier[]) => ({
  modifiers: selected.map(convertModifier), // convertModifier(): Modifier
  errors: selected.flatMap(m => validateModifier(build, m)), // : ValidationError[]
});
```

Use TypeScript naming and formatting conventions consistently, and retain useful static types rather than bypassing them with repeated casts.

## Python conventions

Use `snake_case` for functions and variables and `PascalCase` for classes. Add type annotations to public interfaces and non-obvious function contracts. Use docstrings for public modules, classes, and functions when they clarify purpose, inputs, outputs, units, or non-obvious behavior; use comments for non-obvious implementation constraints rather than restating the code.

Prefer guard clauses when they clarify control flow. Use comprehensions, NumPy operations, and other functional transforms when they make a transformation clearer, but use ordinary loops and local mutation when they are the clearest or most efficient expression. Do not force a functional style that obscures numerical algorithms or creates unnecessary temporary arrays.

Validate external input at API and data boundaries. Raise an appropriate exception for invalid input or violated internal invariants; represent expected domain outcomes explicitly rather than using `None` to hide errors or missing required data. Keep API validation models and internal scientific data structures distinct when that improves clarity, but do not add layers without a concrete need.

Prefer the standard library and existing project helpers for common behavior. Follow established project formatting, linting, and testing tools rather than adding conventions that conflict with them.

## Comments and documentation

Documentation is for users of the code; implementation comments are for maintainers:

- In TypeScript, use `/** JSDoc */` on exported symbols as user-facing documentation. Do not use JSDoc on private functions.
- In Python, use docstrings on public symbols when documentation is useful to callers. Do not require docstrings on every private helper.
- Use implementation comments only when the _why_ is non-obvious: a constraint, workaround, or subtle invariant. Never restate what the code already says. Avoid referencing callers or usage sites ("used by X", "passed to Y", "rendered in the Z section"), a parallel implementation ("same as X does it"), or the specific bug/incident that motivated the code; those details belong in the PR and can become stale.
- A tunable numeric constant or default (a floor, threshold, or other magic number) should document _why that value_, not just what it configures — for example, why `0.25` and not `0.1`.
- Don't name specific external systems, services, or products in a comment when a neutral description reads just as well (for example, "the backend returns null here"). Comments outlive internal naming and branding.
- JSDoc on an exported TypeScript symbol whose transformation isn't obvious from its name and types alone (for example, a math- or algorithm-heavy utility) should include an `@example`. Cross-reference another documented symbol with `{@link otherSymbol}`, not a backtick mention, so IDEs can resolve the link.
- Avoid section-banner comments such as `// --------`. Structure the code to be self-explanatory.

## Testing

**Assert exact output for narrow functions, not fragments.** When a function has one public export and a bounded set of inputs (a render/format function, for example), test it with a full equality assertion against the exact expected output — not a series of `toContain` checks. Fragment assertions are only justified when the test is forced through a broader composition function that drags in irrelevant filler just to reach the part under test; treat that as a signal to extract the narrow piece into its own module, not as a reason to settle for weaker assertions.

**Expected values must be independent literals, not derived from the test's own input.** Writing `` `- ${quantity} x ${item.name}` `` in an expected string encodes how the code is wired into the test itself, rather than asserting a concrete expectation — a reader has to trace back to the input to know what's being checked, and a bug in how that field gets placed can slip through unnoticed. Use a literal value instead.

**When an expected value's exact formatting isn't known with confidence, verify it once — don't keep recomputing it with the same utility the code under test calls.** For values with real transformation logic (rounding, unit formatting, sigfig rules), write a throwaway assertion against a placeholder, read the actual value off the failure diff, then hardcode that verified literal and delete the scratch test.

For floating-point and numerical algorithms, do not require bitwise or exact equality when rounding and representation make that inappropriate. Assert with explicit, justified absolute and/or relative tolerances, and cover meaningful edge cases. Keep exact assertions for discrete values, shapes, labels, and deterministic formatting where exactness is appropriate.

## Scientific-computing conventions

- **Precision:** Choose array and scalar dtypes deliberately; avoid implicit or lossy conversions. Keep rounding for display separate from stored/computed values. Numerical comparisons must use explicit, justified absolute and/or relative tolerances; consider scale and units. Handle NaN, infinity, overflow, and division by zero intentionally.
- **Reproducibility:** Use explicit, local random-number generators and record the seed for stochastic work. Keep the parameters and algorithm choices needed to repeat an analysis accessible; record package or environment versions when they materially affect results. Do not build elaborate provenance systems before the project needs them.
- **Coordinates and units:** For initial image processing, use a top-left origin, x increasing right, and y increasing down. State coordinate order and axes explicitly at interfaces. NumPy image arrays are indexed `[row, column]`, corresponding to `[y, x]`; do not confuse array indexing with geometric `(x, y)` coordinates. Make transforms between image coordinates and visualization coordinates explicit and test them with known landmarks. Physical units require explicit calibration; do not infer physical scale from pixel indices.
- **Image arrays:** Document array shape and axis order when data crosses a module or API boundary, including the location of any channel dimension. Carry pixel/voxel spacing and origin where relevant, and avoid silently dropping them during processing. Support additional microscopy dimensions or metadata only when a concrete input requires them.

## Before starting any non-trivial feature

1. Read the spec — flowchart, requirements doc, or design decision.
2. Map the decision tree or data flow in pseudocode before writing implementation code.
3. Identify where validation ends and computation/rendering begins.
4. Draft the entry-point signature and return contract in the implementation language.
5. List utilities and types needed — verify they do not already exist.
6. Agree on the approach before writing implementation code.
