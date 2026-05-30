# Coverage Scoring Rubric — Per SRC-N

> **Read before filling**
>
> **Coverage Perspective Rule:** Assess L2 and L4 from the STUDENT's perspective —
> what does the QUESTION + ANSWER BOX require the student to do?
> - Do NOT infer coverage from what the solution demonstrates.
> - If solution shows key idea but question does not require it → L2 score low.
> - If question exercises key idea but solution uses wrong method → Coverage PASS; route to `audit-pedagogical`.
>
> **Coupling Rule:** If L2.2 = 0 (near-copy confirmed) → set L2.1 = 0.
> A template that is a near-copy of the source fails the fundamental contract of a dynamic exercise,
> regardless of whether the key idea is technically present.

---

## SRC-{N} Scoring Rubric

### Level 2 — Key Idea [50 pts]

Score L2.2 first, then apply coupling rule before scoring L2.1.

- [ ] **L2.2** Generalization is sufficient: the template's surface realization differs enough
             from the source that it is NOT a near-copy (same canonical form, symbol swap only,
             or near-identical wording all qualify as near-copy) (20 pts)
             Score: ___/20 | Evidence: ___

- [ ] **L2.1** The QUESTION + ANSWER BOX requires the student to exercise the same core
             technique / theorem / principle as the source (30 pts)
             [**If L2.2 = 0, set this to 0** — coupling rule; a near-copy template has not
             demonstrated independent coverage of the key idea]
             Score: ___/30 | Evidence: ___

**L2 Total: ___/50**

---

### Level 4 — Assessment Intent [25 pts]

- [ ] **L4.1** The student (via question/answer box) must perform the same cognitive action
             as the source, OR a valid LMS-gradable proxy for it (15 pts)
             [Score ≤5/15 if: the source requires a multi-step sequential demonstration AND
             the template grades only the final result without a separate proxy for each
             required intermediate step]
             Score: ___/15 | Evidence: ___

- [ ] **L4.2** If a proxy is used: proxy requires genuine reasoning (construct inverse,
             select theorem, identify justification, complete linked steps) — not shallow
             guessing (single fixed choice with no required reasoning) (10 pts)
             [If the template is a **direct format** (not a proxy): mark N/A and score 10/10]
             Score: ___/10 | Evidence: ___

**L4 Total: ___/25**

---

### Level 1 — Framing [15 pts]

- [ ] **L1.1** Framing requirement of the source is preserved or acceptably adapted via
             LMS-gradable proxy
             (Examples of preserved: "if it exists" + "Enter DNE" = preserved;
             "to four decimal places" precision kept; "find all solutions" scope kept)
             (Examples of adapted: proof/explanation converted to machine-gradable multipart
             that still requires the same decision or construction) (15 pts)
             Score: ___/15 | Evidence: ___

**L1 Total: ___/15**

---

### Level 3 — Problem Type [10 pts]

- [ ] **L3.1** Answer type and cardinality match the source or are acceptably adapted to
             LMS constraints (single numeric, T/F pool, multipart, matrix entries, etc.) (10 pts)
             Score: ___/10 | Evidence: ___

**L3 Total: ___/10**

---

### Grand Total

| Level | Score |
|---|---|
| L2 Key Idea | ___/50 |
| L4 Assessment Intent | ___/25 |
| L1 Framing | ___/15 |
| L3 Problem Type | ___/10 |
| **Grand Total** | **___/100** |

> **must_cover note:** If this SRC-N has `must_cover=true` in `source_brief.xml` and Grand Total < 85,
> escalate the verdict to **FAIL** regardless of PARTIAL threshold.

### Verdict

| Score | Verdict |
|---|---|
| ≥ 85 | PASS |
| 60–84 | PARTIAL |
| < 60 | FAIL |

**SRC-{N} Verdict: ___**
