# Context Authoring

Guide for inventing or evaluating a real-world context in `question.txt` before it reaches `audit-pedagogical`.

---

## Goal

Use a context that sounds like a quantity a person could plausibly track, graph, estimate, or differentiate.
The context should support the mathematics without introducing a misleading technical meaning.

This guide is about **student-facing realism**, not curriculum coverage and not mathematical correctness.

---

## Preferred Quantity Types

Prefer quantities with clear semantics, especially when the formula is only a stylized model.

Good default families:
- capacity
- population
- revenue
- concentration
- demand
- adoption index
- production index
- output index
- inventory level
- enrollment

These are usually easier to pair with:
- time-based rates
- growth or decay models
- rounded numeric answers
- generic synthetic "index" interpretations

---

## Labels to Treat Carefully

Use extra care with labels that carry a technical meaning.

Common risky labels:
- efficiency index
- stability score
- optimization rate
- performance coefficient
- resilience factor

These are not forbidden, but they need explicit meaning. If the label is vague, ornamental, or implies a technical definition that the problem does not support, rewrite it.

If you use `index`:
- treat it as a synthetic tracked quantity
- keep the wording consistent with that interpretation
- avoid pairing it with language that implies a physically measured engineering property unless the problem really means that

---

## Authoring Rules

1. The intro sentence must support the exact quantity named in the formula.
2. Avoid filler framing that does not help the student interpret the quantity.
3. The quantity label and visible rate/unit wording must fit each other.
4. If the quantity is synthetic, say so naturally through words like `index`, `adoption index`, or `production index`, rather than implying a precise engineering metric.
5. If the context is not helping, prefer a simpler but believable applied context over a dramatic one.

---

## Preflight Checklist

Before finalizing `question.txt`, check:

- Is this a thing people would actually track?
- Does the named domain support the function shape and the interpretation?
- If the problem asks for a rate of change, does that rate sound like a meaningful rate for the named quantity?
- If the prompt uses an `index`, does the rest of the wording stay consistent with an index rather than a physical property?
- Can the intro be paraphrased briefly without becoming vague or decorative?

If any answer is "no" or "not really", rewrite the context before shipping it.

---

## Examples

### Good

- `The installed solar capacity index for Spain from 2010 to 2020 is modeled by ...`
- `The renewable energy adoption index for Spain from 2010 to 2020 is modeled by ...`
- `The concentration of a medication in the bloodstream t hours after injection is modeled by ...`

Why these work:
- the quantity is easy to imagine tracking
- the rate of change language sounds natural
- the label does not overpromise a technical meaning the model does not define

### Borderline but Acceptable

- `The grid modernization index for a region is modeled by ...`
- `The production readiness score for a factory network is modeled by ...`

These can work, but only if the surrounding wording stays generic and does not imply a sharper scientific definition than the problem provides.

### Artificial or Should Rewrite

- `Across progressive nations, the solar efficiency index for Spain is modeled by ...`
- `The optimization rate of the energy system is modeled by ...`
- `The stability score of the market is modeled by ...`

Why these are weak:
- the label is vague or ornamental
- the domain intro reads like filler
- the quantity sounds like it should have a technical definition that the problem never gives

---

## Fast Rewrite Pattern

When a context sounds artificial, rewrite in this order:

1. Keep the domain only if it helps
2. Replace the quantity with a trackable one
3. Make the rate wording match that quantity

Example:

- Weak: `solar efficiency index`
- Better: `renewable energy adoption index`
- Better when the quantity should sound more concrete: `installed solar capacity index`

---

## Relationship to Audits

- Coverage asks whether the template preserves source intent.
- Accuracy asks whether the mathematics is correct.
- Pedagogical asks whether the wording and context are believable and student-safe.

If a context sounds artificial but the math is fine, expect a `P3` pedagogical note.
If the context wording makes the student misunderstand what quantity or unit is being modeled, expect a `P2` pedagogical issue.
