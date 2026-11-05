# Caveman Focus — RH Research Run 008
**Date:** 2026-11-02  
**Research attribution:** Kiara Lynn Rose Smith's Caveman Focus.  
**Target:** Research whether a proof or refutation of RH has an unavoidable, civilization-exceeding physical verification cost. Use real RH arithmetic structure rather than an arbitrary oracle problem.  
**Verdict:** RH-specific arithmetic *semantic* invariant isolated and an elementary analytic barrier independently derived. This is existing mathematical theory, **not** a new theorem proving RH, RH independence, or physical unprovability. Computations are exploratory only.

## 1. Distinguish what is invariant
Prior Run 007 demonstrated that proof costs depend on the deductive rules. It is unsafe to call a semantic property an invariant of *proof cost*. For this run, study a genuine RH-specific semantic property and test whether it constrains proof resources.

Let the von Mangoldt function Λ(n)=log p if n=p^k (k≥1), otherwise 0. Define the right-continuous Chebyshev sum and discrepancy

    psi(x) = Σ_{n≤x} Λ(n);     E(x)=psi(x)-x,  for real x≥1.

Define the growth index

    alpha = inf{ a∈R : E(x)=O(x^a) as x→∞ }.

The feasibility set is upwards-closed; the infimum need not be achieved. The prime number theorem gives E(x)=o(x), so alpha≤1; in fact alpha≥1/2 by the existence of nontrivial zeta zeros on the critical line and the analytic barrier derived below.

**Classical equivalence:** RH if and only if alpha=1/2. This is a familiar reformulation of prime number theorem error bounds, NOT novel.

## 2. Proven analytic barrier, with its dependencies
For Re(s)>1, the Euler product yields the absolutely convergent Dirichlet series

    -ζ'(s)/ζ(s) = Σ_{n≥1} Λ(n)n^(−s) = s ∫_1^∞ psi(x)x^(−s−1) dx.

Subtract the integral of x:

    -ζ'(s)/ζ(s) = s/(s−1) + s ∫_1^∞ E(x)x^(−s−1) dx.

If an exponent a<1 satisfies |E(x)|≤C x^a for x≥X_0, the last integral converges absolutely and locally uniformly for Re(s)>a. It is therefore analytic there. The meromorphic continuation of the left side has poles at the zeta zeros and at s=1 (the latter is explained by s/(s−1)); thus **ζ has no zeros in Re(s)>a**. The argument uses standard meromorphic continuation and the Euler-product Dirichlet series, not RH.

Hence for every nontrivial zero ρ,

    alpha ≥ Re(ρ).

A zero with Re ρ>1/2 would force alpha>1/2. By the functional equation symmetry, RH fails exactly when some zero has Re>1/2.

Conversely, classical RH error estimates supply E(x)=O(x^(1/2)(log x)^2), which implies alpha≤1/2. Since critical-line zeros are known to exist, alpha≥1/2. Therefore

    RH ⇔ alpha=1/2.

**Contrapositive with arbitrarily late failure:** If ζ has a zero with real part β>a, then for every C>0 and every X≥1, there exists x≥X with |E(x)|>C x^a. Otherwise E=O(x^a) and the analytic barrier would prohibit that zero. This says *where* unbounded discrepancies must eventually manifest if the conjecture is false, not *when* a human can discover a witness.

## 3. Numerical experiment: E(x) over a finite million-point interval
Companion script `rh_run008_prime_error_experiment.py` stamps Λ(n) on prime powers and accumulates ψ(n) for all integers 1≤n≤1,000,000. Separate prime enumeration independently reproduces ψ at caps 10, 100, 1,000, and 10,000 within floating-point errors ≤6e−12.

| integer n | ψ(n) approximately | E(n) approximately | |E(n)|/(√n log²n) |
|---:|---:|---:|---:|
| 10 | 7.83201418 | −2.16798582 | 0.1293079003 |
| 100 | 94.04531123 | −5.95468877 | 0.0280780989 |
| 1,000 | 996.68091225 | −3.31908775 | 0.0021996058 |
| 10,000 | 10013.39669326 | +13.39669326 | 0.0015792332 |
| 100,000 | 100051.56402566 | +51.56402566 | 0.0012301992 |
| 1,000,000 | 999586.59749563 | −413.40250437 | 0.0021659041 |

For integers 10≤n≤1,000,000 the largest *observed* normalized ratio is approximately 0.1293079003 at n=10. All results are floating-point diagnostics: there is no numerical rigor/interval certificate, and finite evidence cannot establish alpha=1/2.

## 4. A deliberately misleading arithmetic twin (extension of Run 005)
Let q be a prime larger than the entire observation range X, choose β with 1/2<β<1, and put

    F_q(s)=ζ(s)(1+q^(β−s)).

Its Dirichlet-series coefficients match ζ(s) exactly for every n<q, and its coefficients are positive. It still has an Euler product with a modified q-factor, and meromorphic continuation. It also has explicitly off-critical zeros

    s=β+(2k+1)πi/log(q), k∈Z.

The exact perturbation to its logarithmic derivative is

    -F'_q(s)/F_q(s) + ζ'(s)/ζ(s)
      = (log q) Σ_{k≥1} (-1)^(k−1) q^(kβ) q^(−ks),  Re(s)>max(1,β).

Consequently **all weighted prime-power coefficients up to n<q match**, while the first altered coefficient occurs at q. At x=q^m the cumulative alteration is exactly

    D_m = (log q) Σ_{k=1}^m (-1)^(k−1) q^(kβ)
        = (log q) q^β (1−(−q^β)^m)/(1+q^β),

which has magnitude asymptotically proportional to (q^m)^β. Thus finite initial arithmetic records can conceal an off-line zero and pronounced later prime-power fluctuations in this enlarged function class.

For q=1009, β=3/4, X=1000, the first altered coefficient is at n=1009 and the factor has a zero at 0.75+0.4542029914988724i. The extra log-derivative coefficients at q, q², q³, q⁴ alternate signs with rapidly increasing sizes. This twin is **not ζ**: it does not satisfy ζ's exact functional equation and its modified log-derivative coefficients need not remain nonnegative. Therefore this is a theorem about an enlarged class, not a way to alter RH or a proof that actual prime arithmetic requires unbounded work.

## 5. A no-go concerning 'all proof methods' without axiom costs
Fix any sound arithmetical base theory T. For any definite sentence P, exactly one of P and ¬P is true in the standard model. The corresponding extension T+{true side} remains sound and proves that side as an axiom in one line.

Therefore a proposal to lower-bound the length of *every* proof in *every sound extension* without charging the costs of identifying/justifying added axioms is false, for RH just as for other sentences. The existence of the extension does **not** mean a human knows which one is sound. A physical-cost model must declare its independently justified axioms, proof-verification interface, and how it prices new principles. This is an elementary existing observation, not a new impossibility result for RH.

**What we learned:** Even the exact RH semantic invariant alpha is not itself a lower bound on shortest proof length. A globally valid analytic inequality could certify alpha=1/2 with a short proof and no prime-by-prime enumeration. Conversely, a computation that samples many prime powers without a global argument cannot establish it.

## 6. New research guess (CONJECTURE; not verified originality)
The useful RH-specific research object may be the *certification cost of a global analytic continuation estimate*, not a large list of prime powers. Concretely, fix an independently justified weak base theory T and a normal form for allowed analytic certificates. Investigate whether any T-derivation of either

    for every epsilon>0, |psi(x)-x| = O(x^(1/2+epsilon))

or the existence of a violating x (via an exact finite-counterexample criterion) must exceed a demonstrable resource budget B.

The branch must test alternative methods: spectral positivity, arithmetic inequalities, direct zero-free regions, and computation. A lower bound only for one restricted certificate family is not a bound on *every* valid RH proof.

**Discovery audit:** The analytic barrier, error-growth equivalence, and proof-system relativity are established mathematics. The additional model perturbation is a transparent extension of the preceding Run 005 construction, not claimed novel. The candidate all-representation certification benchmark has not been demonstrated and has not been vetted for priority. No RH proof, disproof, independence or human-extinction bound has been established.

## 7. Next precise obligation (RH-009)
1. Define an *explicit* bounded family of honest analytic certificate formats (e.g. rational interval inequalities for a Mellin-transform remainder, with machine-verifiable rational checkers).
2. Prove a nonvacuous lower bound for at least one family while tracking the computational cost of checking imported assumptions.
3. Attempt to construct shorter certificates through a different representation and actively try to falsify the lower bound.
4. Keep RH-specific semantics and resource-bounded proof complexity in separate columns, then investigate whether a valid theorem links them.

## Sources
- Wolfram MathWorld, *Mangoldt Summatory Function*, classical equivalence of RH and ψ(x)=x+O(√x log²x), https://mathworld.wolfram.com/MangoldtSummatoryFunction.html
- Lee and Nosal (2023/2024), RH-conditional explicit ψ estimate, https://arxiv.org/abs/2312.05628
- Lagarias (2000), *An Elementary Problem Equivalent to the Riemann Hypothesis*, https://arxiv.org/abs/math/0008177
- Louis-Paul Hayoun, *Epistemic Horizon Theory* (user-provided preprint, November 2026), pp. 76–78, 104–108; conceptual accessibility framework, not an RH impossibility proof.
- Caveman Focus RH Runs 005–007, previously archived, on arithmetic impostors, oracle lower bounds, and formal proof-system speed-ups.