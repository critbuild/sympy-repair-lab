# Reference answers and review notes

The executable reference answer for each task is the production patch named in
`tasks.json`, applied to its pinned baseline (and seed, for case03). Expected
observable outputs are exported to `tasks/<case>/expected_behavior.json` from
the passing pretrial reference runs. The grader accepts behavior, not a textual
match to the reference patch.

| Case | Why the reference is correct for the declared scope |
|---|---|
| 01 | Unknown foreign operands return `NotImplemented`, enabling Python reflection. Relevant inequality implementations and downstream direct-call consumers are adapted so the sentinel is not accidentally converted to a false inequality. Ordinary unequal objects and geometry consumers retain their prior behavior. The upstream patch contains additional comparison fixes; candidates are judged only by declared behavior. |
| 02 | Upstream reflection fixes distinguish strict and inclusive order. Additional evaluator-authored sign checks use the symbolic difference for known real numeric operands, avoiding a premature floating-point round trip near pi. Exact Fraction/Machin bounds independently establish that the reported rational is above pi and the binary float is below. Undecidable symbolic relations remain symbolic. |
| 03 | `return not self == o` invokes Python's operator dispatch before negation, restoring inequality with unsupported objects while retaining the foreign-equality repair. An alternative implementation that explicitly propagates `NotImplemented` also passes. |
| 04 | Expression-domain truth testing consults the expression's zero property, so algebraically zero coefficients can be stripped during denominator clearing. Nonzero and unresolved coefficients are retained. A different, earlier model repair normalizing the local polynomial operation also passes. Construction-time recognition of the original unsimplified expression is outside this prompt. |
| 05 | Finite Cartesian products can be checked element by element against the explicit finite set. Equality uses mutual subset relationships with fuzzy truth logic, preserving unknown membership. Relational simplification avoids arithmetic subtraction of non-expression set objects. The declared stale-test choice accepts either its previous undecided result or a justified false result. |
| 06 | The Bareiss determinant algorithm uses reasonable pivot selection with an expanded-product zero test instead of treating an unsimplified symbolic zero as a usable pivot. For entries `i + a*j`, every row lies in the span of the index vector and the all-ones vector, so rank is at most two. Determinants of size at least three are zero. Nonzero examples and a separately computed integer determinant check preservation. |
| 07 | The extension factorization's square-free norm step receives the original polynomial `F` rather than the intermediate `f`. The tested square-free multivariate outputs preserve all factors and the coefficient; normal rational factoring and univariate multiplicity are preserved. Multivariate repeated factors were excluded before model runs because the upstream repair does not validate that broader scope. |

The exact arithmetic verification scripts and records are under `validation/`.
The determinant's initial unexecuted draft value was corrected from 109 to 115
before model calls. The near-pi reference was strengthened before launch after
the upstream patch alone failed the correct boundary values. These authoring
corrections are disclosed in `validation/PREFLIGHT.json`.

Reference passes do not prove total mathematical correctness for every possible
input. They establish attainable correct behavior on the stated finite task
contracts. A human reviewer still needs to check that those contracts and
expected behaviors are appropriate.
