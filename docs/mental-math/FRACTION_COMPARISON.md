# Fraction Comparison Mental Models

This is the first canonical mental-math study pack in StudySyndicate.

The goal is not to replace exact arithmetic. The goal is to **notice structure before calculating** so that most comparisons collapse into a small, intuitive decision.

## Core doctrine: cheapest insight first

For two fractions, do not cross-multiply automatically. Walk down this ladder and stop as soon as a cheaper exact comparison settles the problem:

1. **Same denominator** — larger numerator wins.
2. **Same numerator** — smaller denominator wins.
3. **Benchmark against 1/2** — if the fractions land on opposite sides, the answer is immediate.
4. **Benchmark against another friendly landmark** — try values such as 1/3, 2/3, 3/4, or 1 when the numbers suggest them.
5. **Gap from 1** — compare what each fraction is missing from a whole.
6. **Landmark residual** — if both fractions are near the same landmark, compare their small signed errors from it.
7. **Common-numerator scaling** — when the tops are friendly, make them equal and let the transformed denominators expose the comparison.
8. **Cross multiplication** — the guaranteed exact fallback when no cheaper structure helps.

The sequence is a fallback ladder, not a requirement to perform every step.

## 1. Same denominator

For

\[
\frac{a}{d} \quad\text{and}\quad \frac{c}{d},
\]

the pieces are the same size, so compare only the numerators.

Example:

\[
\frac{5}{12}<\frac{7}{12}.
\]

## 2. Same numerator

For

\[
\frac{n}{b} \quad\text{and}\quad \frac{n}{d},
\]

the fraction with the **smaller denominator is larger** because the same number of pieces are being taken from larger pieces.

Example:

\[
\frac{5}{8}>\frac{5}{9}.
\]

## 3. Benchmark against one-half

For a fraction \(a/b\), compare \(2a\) with \(b\).

- \(2a>b\): above \(1/2\)
- \(2a=b\): exactly \(1/2\)
- \(2a<b\): below \(1/2\)

Example:

\[
\frac{7}{13}>\frac12,\qquad \frac{8}{17}<\frac12,
\]

so

\[
\frac{7}{13}>\frac{8}{17}.
\]

This is often the cheapest useful test for unrelated proper fractions.

## 4. Benchmark against another landmark

For a friendly landmark \(p/q\), compare

\[
qa \quad\text{with}\quad pb.
\]

The sign of

\[
qa-pb
\]

tells whether \(a/b\) is above, equal to, or below \(p/q\).

Useful landmarks include:

\[
\frac13,\quad \frac12,\quad \frac23,\quad \frac34,\quad 1.
\]

## 5. Gap from one

Rewrite

\[
\frac{a}{b}=1-\frac{b-a}{b}.
\]

Instead of comparing the original fractions, compare what each one is **missing**. The fraction with the smaller missing proportion is larger.

### Original example: \(3/8\) vs. \(4/9\)

First try \(1/2\):

- \(3/8<1/2\)
- \(4/9<1/2\)

That benchmark does not separate them, so fall back.

Their gaps from one are:

\[
1-\frac38=\frac58
\]

and

\[
1-\frac49=\frac59.
\]

Because

\[
\frac59<\frac58,
\]

\(4/9\) is missing less from a whole:

\[
\boxed{\frac49>\frac38}.
\]

## 6. Landmark residual

The gap-from-one idea generalizes to any landmark.

For \(a/b\) relative to \(p/q\),

\[
\frac{a}{b}-\frac{p}{q}
=
\frac{qa-pb}{qb}.
\]

The small integer

\[
qa-pb
\]

is the **residual**.

Example:

\[
\frac{667}{1000}
\quad\text{vs}\quad
\frac{671}{1006}.
\]

Both are near \(2/3\).

\[
3(667)-2(1000)=1
\]

and

\[
3(671)-2(1006)=1.
\]

So their excesses above \(2/3\) are

\[
\frac{1}{3000}
\quad\text{and}\quad
\frac{1}{3018}.
\]

Since \(1/3000>1/3018\),

\[
\boxed{\frac{667}{1000}>\frac{671}{1006}}.
\]

Large-number comparison became a comparison of tiny residuals.

## 7. Common-numerator scaling

This is especially useful when the numerators are small but the denominators are awkward.

Compare:

\[
\frac{3}{34}
\quad\text{and}\quad
\frac{2}{23}.
\]

The numerators have an easy common multiple: 6.

\[
\frac{3}{34}=\frac{6}{68}
\]

and

\[
\frac{2}{23}=\frac{6}{69}.
\]

Now the numerators match. The smaller denominator gives the larger fraction:

\[
\frac{6}{68}>\frac{6}{69}.
\]

Therefore:

\[
\boxed{\frac{3}{34}>\frac{2}{23}}.
\]

The transformation is exact, not an estimate.

Another example:

\[
\frac{5}{47}
\quad\text{vs}\quad
\frac{2}{19}
\]

becomes

\[
\frac{10}{94}
\quad\text{vs}\quad
\frac{10}{95},
\]

so

\[
\frac{5}{47}>\frac{2}{19}.
\]

## 8. Cross-multiplication fallback

When the earlier structures do not simplify the comparison, use the exact fallback.

For

\[
\frac{a}{b}\quad\text{vs}\quad\frac{c}{d},
\]

compare

\[
ad \quad\text{with}\quad cb.
\]

Example:

\[
\frac{17}{43}\quad\text{vs}\quad\frac{19}{48}.
\]

\[
17(48)=816,\qquad 19(43)=817,
\]

so

\[
\frac{17}{43}<\frac{19}{48}.
\]

Cross multiplication is not a failure. It is the **proof floor** when no cleaner mental structure presents itself.

## Mental model

A useful sentence to remember is:

> **Anchor → shrink the problem → compare the leftovers → fall back only when necessary.**

Common denominator thinking asks:

> How many equal-size pieces do I have?

Common numerator thinking asks:

> If I force the same amount of pieces, which denominator must be smaller?

Landmark thinking asks:

> How far is each fraction from something I already understand?

These are different views of the same exact arithmetic.

## Flashcards and practice problems

Machine-readable study material lives at:

`content/mental-math/fraction-comparison.v1.json`

The seed currently contains:

- 8 comparison principles in fallback order
- 12 flashcards
- 24 exact practice problems
- explicit strategy paths so a future study engine can distinguish the first attempted benchmark from the fallback that actually settles the problem
- worked explanations and answer keys

The seed is intentionally independent of a UI. When the local study engine is implemented, the importer should map:

- principles → `concept` actors
- flashcard fronts → `prompt` actors
- flashcard backs → `response` actors
- practice questions → `prompt` actors
- worked explanations → `response` actors
- strategy links → `tests`, `explains`, and `depends-on` relationships as appropriate

This preserves the factored domain model instead of creating a special-case mental-math database.

## Content validation

Run:

```bash
python scripts/validate-mental-math-content.py
```

The validator checks the schema, required strategy ladder, unique identifiers, strategy references, fraction validity, strategy-specific invariants, and every stored answer against Python's exact rational arithmetic.
