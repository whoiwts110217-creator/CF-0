# SN Mathematical Symbol Atlas

> Generated from the supplied registry. Registry coverage is not proof of exhaustive coverage.

## Complex analysis and number theory

| Glyph | LaTeX | Name | Meaning | Type/domain | Arity | Example | Status | Source | Ambiguities |
|---|---|---|---|---|---|---|---|---|---|
| ζ(s) | \zeta(s) | Riemann zeta function | For Re(s)>1, the Dirichlet series sum n^(-s); elsewhere use its analytic continuation except at its pole. | Complex variable s; meromorphic function | Unary function | ζ(s)=Σ_{n≥1} n^{-s}, Re(s)>1 | standard | Standard analytic number theory notation; attach a formal reference in a production registry. | Series definition alone applies only when Re(s)>1. |

## Logic and foundations

| Glyph | LaTeX | Name | Meaning | Type/domain | Arity | Example | Status | Source | Ambiguities |
|---|---|---|---|---|---|---|---|---|---|
| ∃! | \exists! | Unique existence | There exists exactly one object satisfying a predicate, relative to a specified domain. | Predicate over domain X | Quantifier binding one variable | ∃!x∈R: x+1=2 | standard | Standard mathematical logic notation; attach a formal reference in a production registry. | The domain and predicate must be explicit. |

## SN local notation

| Glyph | LaTeX | Name | Meaning | Type/domain | Arity | Example | Status | Source | Ambiguities |
|---|---|---|---|---|---|---|---|---|---|
| 𝔖ₙ | \mathfrak{S}_n | SN state at stage n | Locally defined state tuple containing knowledge, language, operations, constraints, state space, and optional probability structure. | Typed tuple defined by this project | Indexed object | 𝔖ₙ=(Kₙ, Lₙ, Oₙ, Cₙ, Mₙ, Pₙ) | local_sn | Definition introduced by this project; not standard universal notation. | Must be defined consistently throughout the project. |