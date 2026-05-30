# Applied Calculus for the Managerial, Life, and Social Sciences — XML Knowledge Base

> Book: *Applied Calculus for the Managerial, Life, and Social Sciences* (Cengage / Tan)
> Sections: 66 teaching units across 12 chapters
> Last rebuilt: 2026-05-15

---

## Purpose

Structured XML representation of a full applied calculus textbook targeting business, life, and social science students.
Primary agent use cases:
- **Content lookup** — find definitions, rules, worked examples for a concept
- **Exercise retrieval** — find practice problems on a specific topic
- **Future-learning check** — verify a term is formally introduced before it appears in a question
- **Coverage analysis** — determine which sections treat a concept and at what depth

File scope:
- `chNN_sectMM.xml` — one teaching unit (preferred for targeted lookups)
- `chNN.xml` — full chapter (use for broad cross-section search)
- This directory is the working directory for all commands below

---

## XML Schema Reference

### Section file root element

```xml
<section_file chapter="ch01" chapter_number="1" section="sect_01" section_number="1">
  <section number="1.1" title="Precalculus Review I">
    <content>
      <!-- conceptual intro text -->
    </content>
  </section>
  <subsection title="The Real Number Line">
    <!-- sub-topic narrative: paragraphs, notes, examples, figures, tables -->
  </subsection>
  <!-- ... more subsections ... -->
  <subsection number="1.1" title="Self-Check Exercises">
    <exercises><exercise_group><problem number="1">...</problem></exercise_group></exercises>
  </subsection>
  <subsection number="1.1" title="Concept Questions">
    <exercises>...</exercises>
  </subsection>
  <subsection number="1.1" title="Exercises">
    <exercises>
      <exercise_group>
        <instructions>Optional shared direction text for the group</instructions>
        <problem number="1"><statement><paragraph>...</paragraph></statement></problem>
      </exercise_group>
    </exercises>
  </subsection>
</section_file>
```

### Chapter file root element

```xml
<chapter id="ch01" number="1">
  <opener>
    <subsection title="Introduction">...</subsection>
  </opener>
  <section number="1.1" title="...">...</section>
  <!-- all sections inline, no separate exercises grouping -->
</chapter>
```

### Element reference

| Element | Key attributes | Meaning |
|---------|---------------|---------|
| `<note>` | `title` | Callout box — heterogeneous; see note title patterns below |
| `<example>` | `number` | Fully worked example with solution steps |
| `<subsection>` | `title`, `number` | Content sub-topic or exercise category |
| `<exercises>` | — | Container for `<exercise_group>` elements |
| `<exercise_group>` | — | Group of problems, may share `<instructions>` |
| `<instructions>` | — | Shared direction text for a problem group |
| `<problem>` | `number` | Individual exercise |
| `<statement>` | — | Problem body |
| `<term>` | — | Key vocabulary term (inline, appears bold) |
| `<math display="inline">` | — | Inline LaTeX wrapped in `$$...$$` |
| `<math display="block">` | — | Display LaTeX wrapped in `$$...$$` |
| `<figure>` | `number`, `caption` | Diagram, graph, or photo with `<alt_text>` child |
| `<table>` | — | Tabular data with `<thead>/<tbody>/<row>/<cell header="true">` |
| `<heading>` | `level` | Section heading |
| `<paragraph>` | — | Body text |
| `<list>` | `ordered` | `true` = numbered list, `false` = bulleted |
| `<opener>` | — | Chapter introduction (chapter files only) |

### Note title patterns — key for filtering by content type

| Title pattern | Content type |
|---|---|
| `Rule N: ...` | Formal differentiation or integration rule |
| Named concept: `Function`, `Absolute Value`, `Distance Formula`, … | Formal definition |
| `Theorem N` | Named theorem |
| `Applied Example N. ...` | Business/life-science worked example in a box |
| `Exploring with Technology` | Graphing calculator or CAS exploration |
| `Explore and Discuss` | Open discussion/reflection prompt |
| `Note` / `Notes` | General informational callout |

---

## Agent Playbook

All commands run from inside this directory (`Applied Calculus for the Managerial, Life, and Social Sciences/`).

### Find where a concept is defined

```bash
# Search note boxes for a term (definitions, rules, named theorems)
grep -rn '<note' ch*_sect_*.xml | grep -i "derivative"

# Find the EARLIEST section (book order) that defines a term
grep -rl '<note' ch*_sect_*.xml \
  | sort \
  | xargs grep -li "continuity" \
  | head -1

# Find uses of <term> tag (key vocabulary explicitly marked)
grep -rn '<term>' ch*_sect_*.xml | grep -i "integral"
```

### Future-learning check — is term X used before it's formally introduced?

```bash
# Step 1: find which section first mentions the term in a note title
grep -rln '<note' ch*_sect_*.xml \
  | sort | xargs grep -li "derivative" | head -1
# → e.g. ch02_sect_06.xml  (section 2.6, order #10)

# Step 2: find ALL sections that mention the term anywhere
grep -rl "derivative" ch*_sect_*.xml | sort

# Step 3: any file appearing BEFORE the definition file (by sort) is future learning.
# Plain sort gives correct book order — files use zero-padded two-digit numbers:
# ch01_sect_01 < ch01_sect_02 < ... < ch02_sect_01 < ... < ch12_sect_04

# One-liner: show sections that USE term before it's formally introduced
DEFINED_IN="ch02_sect_06.xml"
grep -rl "derivative" ch*_sect_*.xml \
  | sort \
  | awk -v def="$DEFINED_IN" '$0 < def'
```

### Find exercises on a specific topic

```bash
# Exercises mentioning "profit" in section 3.4 (main Exercises subsection)
grep -n "profit" ch03_sect_04.xml | grep -i "statement\|problem\|instructions"

# Get problem numbers that mention a keyword across all sections
grep -rn "elasticity" ch*_sect_*.xml | grep 'number="'

# Find problems mentioning a business term anywhere
grep -rn "consumer surplus\|producer surplus" ch*_sect_*.xml \
  | grep "<statement\|<instructions"
```

### Retrieve a specific exercise

```bash
# Problem 25 from section 4.1 (main Exercises subsection only)
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('ch04_sect_01.xml')
for sub in tree.iter('subsection'):
    if sub.get('title') == 'Exercises':
        for p in sub.iter('problem'):
            if p.get('number') == '25':
                print(ET.tostring(p, encoding='unicode'))
"
```

### Get all named definitions and rules from a section

```bash
# List all note boxes in section 5.4
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('ch05_sect_04.xml')
for n in tree.iter('note'):
    title = n.get('title', '(untitled)')
    text = ' '.join(n.itertext()).split()
    print(f'NOTE [{title}]: {\" \".join(text[:20])}...')
"

# Quick grep for note titles
grep -n '<note' ch05_sect_04.xml
```

### Find all worked examples in a section

```bash
# List example numbers in section 6.2
grep -n '<example' ch06_sect_02.xml

# Extract a specific example with full solution
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('ch06_sect_02.xml')
for e in tree.iter('example'):
    if e.get('number') == '3':
        print(ET.tostring(e, encoding='unicode'))
"
```

### Count and enumerate exercises (the three subsection types)

```bash
# Count problems in each exercise category for a section
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('ch04_sect_02.xml')
for sub in tree.iter('subsection'):
    t = sub.get('title','')
    if t in ('Self-Check Exercises', 'Concept Questions', 'Exercises'):
        count = len(list(sub.iter('problem')))
        print(f'{t}: {count} problems')
"

# All problem numbers in the main Exercises subsection
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('ch03_sect_02.xml')
for sub in tree.iter('subsection'):
    if sub.get('title') == 'Exercises':
        for p in sub.iter('problem'):
            print(p.get('number','?'))
"

# Main exercise count per section in chapter 6
for f in ch06_sect_*.xml; do
  n=$(python3 -c "
import xml.etree.ElementTree as ET, sys
tree = ET.parse('$f')
for sub in tree.iter('subsection'):
    if sub.get('title') == 'Exercises':
        print(len(list(sub.iter('problem')))); sys.exit()
print(0)")
  echo "$f: $n problems"
done
```

### Determine which sections cover a concept

```bash
# Which sections mention "Lagrange multiplier"?
grep -ril "lagrange" ch*_sect_*.xml | sort

# Sections with formal note AND mentioning "exponential"
comm -12 \
  <(grep -rl '<note' ch*_sect_*.xml | sort) \
  <(grep -rl "exponential" ch*_sect_*.xml | sort)
```

### Check if a section covers a topic

```bash
# Does section 3.3 mention "chain rule"?
grep -qi "chain rule" ch03_sect_03.xml && echo "YES" || echo "NO"
```

### Find applied business examples

```bash
# All applied examples across the book on a topic
grep -rn 'Applied Example' ch*_sect_*.xml | grep -i "profit\|revenue\|cost"

# Applied examples in a specific chapter
grep -n 'Applied Example' ch05_sect_04.xml
```

### Extract all math from exercises in a section

```bash
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('ch02_sect_04.xml')
for sub in tree.iter('subsection'):
    if sub.get('title') == 'Exercises':
        for p in sub.iter('problem'):
            for m in p.iter('math'):
                print(f'[{p.get(\"number\")}] {m.text}')
" | head -20
```

---

## Knowledge Ordering Reference

**Canonical book order for future-learning checks.**
Plain `sort` on filenames gives this exact order (zero-padded two-digit section numbers).

| # | Unit | File | Title |
|--:|------|------|-------|
| **Ch 1 — Preliminaries** | | | |
| 1 | 1.1 | ch01_sect_01.xml | Precalculus Review I |
| 2 | 1.2 | ch01_sect_02.xml | Precalculus Review II |
| 3 | 1.3 | ch01_sect_03.xml | The Cartesian Coordinate System |
| 4 | 1.4 | ch01_sect_04.xml | Straight Lines |
| **Ch 2 — Functions, Limits, and the Derivative** | | | |
| 5 | 2.1 | ch02_sect_01.xml | Functions and Their Graphs |
| 6 | 2.2 | ch02_sect_02.xml | The Algebra of Functions |
| 7 | 2.3 | ch02_sect_03.xml | Functions and Mathematical Models |
| 8 | 2.4 | ch02_sect_04.xml | Limits |
| 9 | 2.5 | ch02_sect_05.xml | One-Sided Limits and Continuity |
| 10 | 2.6 | ch02_sect_06.xml | The Derivative |
| **Ch 3 — Differentiation** | | | |
| 11 | 3.1 | ch03_sect_01.xml | Basic Rules of Differentiation |
| 12 | 3.2 | ch03_sect_02.xml | The Product and Quotient Rules |
| 13 | 3.3 | ch03_sect_03.xml | The Chain Rule |
| 14 | 3.4 | ch03_sect_04.xml | Marginal Functions in Economics |
| 15 | 3.5 | ch03_sect_05.xml | Higher-Order Derivatives |
| 16 | 3.6 | ch03_sect_06.xml | Implicit Differentiation and Related Rates |
| 17 | 3.7 | ch03_sect_07.xml | Differentials |
| **Ch 4 — Applications of the Derivative** | | | |
| 18 | 4.1 | ch04_sect_01.xml | Applications of the First Derivative |
| 19 | 4.2 | ch04_sect_02.xml | Applications of the Second Derivative |
| 20 | 4.3 | ch04_sect_03.xml | Curve Sketching |
| 21 | 4.4 | ch04_sect_04.xml | Optimization I |
| 22 | 4.5 | ch04_sect_05.xml | Optimization II |
| **Ch 5 — Exponential and Logarithmic Functions** | | | |
| 23 | 5.1 | ch05_sect_01.xml | Exponential Functions |
| 24 | 5.2 | ch05_sect_02.xml | Logarithmic Functions |
| 25 | 5.3 | ch05_sect_03.xml | Compound Interest |
| 26 | 5.4 | ch05_sect_04.xml | Differentiation of Exponential Functions |
| 27 | 5.5 | ch05_sect_05.xml | Differentiation of Logarithmic Functions |
| 28 | 5.6 | ch05_sect_06.xml | Exponential Functions as Mathematical Models |
| **Ch 6 — Integration** | | | |
| 29 | 6.1 | ch06_sect_01.xml | Antiderivatives and the Rules of Integration |
| 30 | 6.2 | ch06_sect_02.xml | Integration by Substitution |
| 31 | 6.3 | ch06_sect_03.xml | Area and the Definite Integral |
| 32 | 6.4 | ch06_sect_04.xml | The Fundamental Theorem of Calculus |
| 33 | 6.5 | ch06_sect_05.xml | Evaluating Definite Integrals |
| 34 | 6.6 | ch06_sect_06.xml | Area Between Two Curves |
| 35 | 6.7 | ch06_sect_07.xml | Applications of the Definite Integral to Business and Economics |
| **Ch 7 — Additional Topics in Integration** | | | |
| 36 | 7.1 | ch07_sect_01.xml | Integration by Parts |
| 37 | 7.2 | ch07_sect_02.xml | Integration Using Tables of Integrals |
| 38 | 7.3 | ch07_sect_03.xml | Numerical Integration |
| 39 | 7.4 | ch07_sect_04.xml | Improper Integrals |
| 40 | 7.5 | ch07_sect_05.xml | Volumes of Solids of Revolution |
| **Ch 8 — Calculus of Several Variables** | | | |
| 41 | 8.1 | ch08_sect_01.xml | Functions of Several Variables |
| 42 | 8.2 | ch08_sect_02.xml | Partial Derivatives |
| 43 | 8.3 | ch08_sect_03.xml | Maxima and Minima of Functions of Several Variables |
| 44 | 8.4 | ch08_sect_04.xml | The Method of Least Squares |
| 45 | 8.5 | ch08_sect_05.xml | Constrained Maxima and Minima and the Method of Lagrange Multipliers |
| 46 | 8.6 | ch08_sect_06.xml | Total Differentials |
| 47 | 8.7 | ch08_sect_07.xml | Double Integrals |
| 48 | 8.8 | ch08_sect_08.xml | Applications of Double Integrals |
| **Ch 9 — Differential Equations** | | | |
| 49 | 9.1 | ch09_sect_01.xml | Differential Equations |
| 50 | 9.2 | ch09_sect_02.xml | Separation of Variables |
| 51 | 9.3 | ch09_sect_03.xml | Applications of Separable Differential Equations |
| 52 | 9.4 | ch09_sect_04.xml | Approximate Solutions of Differential Equations |
| **Ch 10 — Probability and Calculus** | | | |
| 53 | 10.1 | ch10_sect_01.xml | Probability Distributions of Random Variables |
| 54 | 10.2 | ch10_sect_02.xml | Expected Value and Standard Deviation |
| 55 | 10.3 | ch10_sect_03.xml | Normal Distributions |
| **Ch 11 — Taylor Polynomials and Infinite Series** | | | |
| 56 | 11.1 | ch11_sect_01.xml | Taylor Polynomials |
| 57 | 11.2 | ch11_sect_02.xml | Infinite Sequences |
| 58 | 11.3 | ch11_sect_03.xml | Infinite Series |
| 59 | 11.4 | ch11_sect_04.xml | Series with Positive Terms |
| 60 | 11.5 | ch11_sect_05.xml | Power Series and Taylor Series |
| 61 | 11.6 | ch11_sect_06.xml | More on Taylor Series |
| 62 | 11.7 | ch11_sect_07.xml | Newton's Method |
| **Ch 12 — Trigonometric Functions** | | | |
| 63 | 12.1 | ch12_sect_01.xml | Measurement of Angles |
| 64 | 12.2 | ch12_sect_02.xml | The Trigonometric Functions and Their Graphs |
| 65 | 12.3 | ch12_sect_03.xml | Differentiation of Trigonometric Functions |
| 66 | 12.4 | ch12_sect_04.xml | Integration of Trigonometric Functions |

---

## Content Stats by Section

`Probs` = exercises in main **Exercises** subsection (excludes Self-Check and Concept Questions) · `Notes` = all `<note>` boxes (definitions, rules, applied examples, technology) · `Exs` = fully worked `<example>` elements

| Unit | Title | File | Probs | Notes | Exs |
|------|-------|------|------:|------:|----:|
| **Ch 1 — Preliminaries** | | | | | |
| 1.1 | Precalculus Review I | ch01_sect_01.xml | 148 | 1 | 11 |
| 1.2 | Precalculus Review II | ch01_sect_02.xml | 102 | 4 | 13 |
| 1.3 | The Cartesian Coordinate System | ch01_sect_03.xml | 52 | 6 | 3 |
| 1.4 | Straight Lines | ch01_sect_04.xml | 90 | 15 | 10 |
| **Ch 2 — Functions, Limits, and the Derivative** | | | | | |
| 2.1 | Functions and Their Graphs | ch02_sect_01.xml | 98 | 7 | 7 |
| 2.2 | The Algebra of Functions | ch02_sect_02.xml | 78 | 5 | 2 |
| 2.3 | Functions and Mathematical Models | ch02_sect_03.xml | 88 | 12 | 0 |
| 2.4 | Limits | ch02_sect_04.xml | 98 | 13 | 10 |
| 2.5 | One-Sided Limits and Continuity | ch02_sect_05.xml | 102 | 10 | 6 |
| 2.6 | The Derivative | ch02_sect_06.xml | 62 | 13 | 6 |
| **Ch 3 — Differentiation** | | | | | |
| 3.1 | Basic Rules of Differentiation | ch03_sect_01.xml | 78 | 8 | 6 |
| 3.2 | The Product and Quotient Rules | ch03_sect_02.xml | 74 | 7 | 5 |
| 3.3 | The Chain Rule | ch03_sect_03.xml | 90 | 8 | 6 |
| 3.4 | Marginal Functions in Economics | ch03_sect_04.xml | 42 | 16 | 0 |
| 3.5 | Higher-Order Derivatives | ch03_sect_05.xml | 50 | 4 | 3 |
| 3.6 | Implicit Differentiation and Related Rates | ch03_sect_06.xml | 74 | 11 | 5 |
| 3.7 | Differentials | ch03_sect_07.xml | 50 | 7 | 4 |
| **Ch 4 — Applications of the Derivative** | | | | | |
| 4.1 | Applications of the First Derivative | ch04_sect_01.xml | 106 | 17 | 10 |
| 4.2 | Applications of the Second Derivative | ch04_sect_02.xml | 102 | 11 | 7 |
| 4.3 | Curve Sketching | ch04_sect_03.xml | 74 | 8 | 6 |
| 4.4 | Optimization I | ch04_sect_04.xml | 88 | 12 | 4 |
| 4.5 | Optimization II | ch04_sect_05.xml | 36 | 8 | 0 |
| **Ch 5 — Exponential and Logarithmic Functions** | | | | | |
| 5.1 | Exponential Functions | ch05_sect_01.xml | 54 | 4 | 7 |
| 5.2 | Logarithmic Functions | ch05_sect_02.xml | 68 | 8 | 8 |
| 5.3 | Compound Interest | ch05_sect_03.xml | 64 | 10 | 10 |
| 5.4 | Differentiation of Exponential Functions | ch05_sect_04.xml | 92 | 5 | 6 |
| 5.5 | Differentiation of Logarithmic Functions | ch05_sect_05.xml | 100 | 6 | 6 |
| 5.6 | Exponential Functions as Mathematical Models | ch05_sect_06.xml | 38 | 9 | 0 |
| **Ch 6 — Integration** | | | | | |
| 6.1 | Antiderivatives and the Rules of Integration | ch06_sect_01.xml | 100 | 9 | 10 |
| 6.2 | Integration by Substitution | ch06_sect_02.xml | 72 | 6 | 6 |
| 6.3 | Area and the Definite Integral | ch06_sect_03.xml | 20 | 7 | 2 |
| 6.4 | The Fundamental Theorem of Calculus | ch06_sect_04.xml | 64 | 11 | 5 |
| 6.5 | Evaluating Definite Integrals | ch06_sect_05.xml | 86 | 4 | 5 |
| 6.6 | Area Between Two Curves | ch06_sect_06.xml | 59 | 4 | 6 |
| 6.7 | Applications of the Definite Integral to Business and Economics | ch06_sect_07.xml | 34 | 15 | 1 |
| **Ch 7 — Additional Topics in Integration** | | | | | |
| 7.1 | Integration by Parts | ch07_sect_01.xml | 62 | 5 | 5 |
| 7.2 | Integration Using Tables of Integrals | ch07_sect_02.xml | 47 | 3 | 5 |
| 7.3 | Numerical Integration | ch07_sect_03.xml | 54 | 10 | 3 |
| 7.4 | Improper Integrals | ch07_sect_04.xml | 60 | 7 | 5 |
| 7.5 | Volumes of Solids of Revolution | ch07_sect_05.xml | 33 | 2 | 4 |
| **Ch 8 — Calculus of Several Variables** | | | | | |
| 8.1 | Functions of Several Variables | ch08_sect_01.xml | 64 | 5 | 4 |
| 8.2 | Partial Derivatives | ch08_sect_02.xml | 72 | 8 | 6 |
| 8.3 | Maxima and Minima of Functions of Several Variables | ch08_sect_03.xml | 42 | 8 | 3 |
| 8.4 | The Method of Least Squares | ch08_sect_04.xml | 30 | 4 | 2 |
| 8.5 | Constrained Maxima and Minima and the Method of Lagrange Multipliers | ch08_sect_05.xml | 42 | 5 | 3 |
| 8.6 | Total Differentials | ch08_sect_06.xml | 48 | 5 | 2 |
| 8.7 | Double Integrals | ch08_sect_07.xml | 27 | 4 | 4 |
| 8.8 | Applications of Double Integrals | ch08_sect_08.xml | 29 | 6 | 2 |
| **Ch 9 — Differential Equations** | | | | | |
| 9.1 | Differential Equations | ch09_sect_01.xml | 32 | 1 | 3 |
| 9.2 | Separation of Variables | ch09_sect_02.xml | 42 | 2 | 4 |
| 9.3 | Applications of Separable Differential Equations | ch09_sect_03.xml | 32 | 8 | 0 |
| 9.4 | Approximate Solutions of Differential Equations | ch09_sect_04.xml | 16 | 2 | 2 |
| **Ch 10 — Probability and Calculus** | | | | | |
| 10.1 | Probability Distributions of Random Variables | ch10_sect_01.xml | 66 | 11 | 6 |
| 10.2 | Expected Value and Standard Deviation | ch10_sect_02.xml | 36 | 18 | 4 |
| 10.3 | Normal Distributions | ch10_sect_03.xml | 34 | 5 | 3 |
| **Ch 11 — Taylor Polynomials and Infinite Series** | | | | | |
| 11.1 | Taylor Polynomials | ch11_sect_01.xml | 46 | 8 | 4 |
| 11.2 | Infinite Sequences | ch11_sect_02.xml | 52 | 7 | 5 |
| 11.3 | Infinite Series | ch11_sect_03.xml | 48 | 7 | 4 |
| 11.4 | Series with Positive Terms | ch11_sect_04.xml | 60 | 8 | 8 |
| 11.5 | Power Series and Taylor Series | ch11_sect_05.xml | 36 | 8 | 5 |
| 11.6 | More on Taylor Series | ch11_sect_06.xml | 32 | 2 | 4 |
| 11.7 | Newton's Method | ch11_sect_07.xml | 41 | 6 | 2 |
| **Ch 12 — Trigonometric Functions** | | | | | |
| 12.1 | Measurement of Angles | ch12_sect_01.xml | 30 | 1 | 2 |
| 12.2 | The Trigonometric Functions and Their Graphs | ch12_sect_02.xml | 58 | 6 | 4 |
| 12.3 | Differentiation of Trigonometric Functions | ch12_sect_03.xml | 76 | 10 | 6 |
| 12.4 | Integration of Trigonometric Functions | ch12_sect_04.xml | 58 | 5 | 5 |
