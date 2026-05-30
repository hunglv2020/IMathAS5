# Linear Algebra — XML Knowledge Base

> Book: *Linear Algebra* (Pearson / Lay, 6th ed.)
> Sections: 68 teaching units across 10 chapters + appendices
> Last rebuilt: 2026-05-16

---

## Purpose

Structured XML representation of a full university linear algebra textbook.
Primary agent use cases:
- **Content lookup** — find definitions, theorems, worked examples for a concept
- **Exercise retrieval** — find practice problems on a specific topic
- **Future-learning check** — verify a term is formally introduced before it appears in a question
- **Coverage analysis** — determine which sections treat a concept and at what depth

File scope:
- `chNN_sect_N.M.xml` — one teaching unit (preferred for targeted lookups)
- `chNN.xml` — full chapter (use for broad cross-section search)
- `xml_output/` is the working directory for all commands below

---

## XML Schema Reference

Every section file follows this skeleton:

```xml
<section_file chapter="chNN" chapter_number="N" unit_code="N.M">
  <section number="N.M" title="Section Title">
    <metadata>
      <source_pages count="N">
        <page global_index="N" type="content|exercises"/>
      </source_pages>
    </metadata>
    <content>
      <!-- instructional body -->
    </content>
    <exercises title="N.M Exercises">
      <exercise_group start="N">
        <instructions>Shared direction for the group (optional)</instructions>
        <problem number="N">
          <statement><paragraph>...</paragraph></statement>
        </problem>
      </exercise_group>
    </exercises>
  </section>
</section_file>
```

### Element reference

| Element | Key attributes | Meaning |
|---------|---------------|---------|
| `<note type="definition">` | `title` | Formal definition box |
| `<note type="theorem_key">` | `title` | Key theorem or lemma |
| `<note type="procedure">` | `title` | Step-by-step algorithm |
| `<note type="example_intro">` | — | Motivating paragraph before examples |
| `<note type="caution">` | — | Common mistake warning |
| `<note type="practice">` | — | Practice hint / Try It |
| `<note type="note">` | — | General callout box |
| `<example>` | `number` | Fully worked example with solution |
| `<exercise_group>` | `start` | Group of problems sharing instructions |
| `<instructions>` | — | Shared direction text for a problem group |
| `<problem>` | `number` | Individual exercise |
| `<statement>` | — | Problem body |
| `<math display="inline">` | — | Inline LaTeX wrapped in `$...$` |
| `<math display="block">` | — | Display LaTeX wrapped in `$$...$$` |
| `<heading>` | `level` | Section heading (1–4) |
| `<list>` | `ordered` | `true` = numbered, `false` = bulleted |
| `<figure>` | `label`, `caption` | Diagram or graph |
| `<page_break>` | `number` | Original textbook page boundary |

---

## Agent Playbook

All commands run from the `pearson-extract/` project root.

### Find where a term is formally defined

```bash
# Search definition boxes for a term (across all chapters)
grep -rn 'type="definition"' xml_output/ch*_sect_*.xml | grep -i "eigenvalue"

# Find the EARLIEST section (by book order) that defines a term
grep -rl 'type="definition"' xml_output/ch*_sect_*.xml \
  | sort -V \
  | xargs grep -li "basis" \
  | head -1
```

### Future-learning check — is term X used before it's defined?

```bash
# Step 1: find which section first formally defines the term
grep -rln 'type="definition"' xml_output/ch*_sect_*.xml \
  | sort -V | xargs grep -li "subspace" | head -1
# → e.g. xml_output/ch02_sect_2.8.xml  (order #18)

# Step 2: find ALL sections that mention the term anywhere
grep -rl "subspace" xml_output/ch*_sect_*.xml | sort -V

# Step 3: any file appearing BEFORE the definition file (by sort -V) is future learning.
# sort -V on these filenames gives exact book order:
# ch01_sect_1.1 < ch01_sect_1.2 < ... < ch01_sect_1.10 < ch02_sect_2.1 < ...

# One-liner: show sections that USE term before it's defined
DEFINED_IN="xml_output/ch02_sect_2.8.xml"
grep -rl "subspace" xml_output/ch*_sect_*.xml \
  | sort -V \
  | awk -v def="$DEFINED_IN" '$0 < def'
```

### Find exercises on a specific topic

```bash
# Exercises mentioning "Markov" anywhere in section 10.1
grep -n "Markov" xml_output/ch10_sect_10.1.xml | grep -i "statement\|instructions\|paragraph"

# Get problem numbers that mention a keyword
grep -B10 "least.square" xml_output/ch06_sect_6.5.xml | grep 'number="'

# Find problems across ALL sections mentioning a term
grep -rn "Leontief" xml_output/ch*_sect_*.xml | grep "<statement\|<instructions"
```

### Retrieve a specific exercise

```bash
# Problem 15 from section 3.2 (with surrounding context)
python3 -c "
import xml.etree.ElementTree as ET, sys
tree = ET.parse('xml_output/ch03_sect_3.2.xml')
for p in tree.iter('problem'):
    if p.get('number') == '15':
        print(ET.tostring(p, encoding='unicode'))
"
```

### Get all definitions from a section or chapter

```bash
# List definitions in section 4.1
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('xml_output/ch04_sect_4.1.xml')
for n in tree.iter('note'):
    if n.get('type') == 'definition':
        title = n.get('title', '(no title)')
        text = ' '.join(n.itertext()).split()
        print(f'DEF [{title}]: {\" \".join(text[:25])}...')
"

# Quick grep approach
grep -n 'type="definition"' xml_output/ch04_sect_4.1.xml
```

### Find all theorems in a chapter

```bash
grep -n 'type="theorem_key"' xml_output/ch05.xml
```

### Find all worked examples in a section

```bash
# List example numbers and headings
grep -n '<example\|<heading' xml_output/ch05_sect_5.1.xml | grep -A1 '<example'
```

### Count and enumerate exercises

```bash
# Problem count per section in chapter 4
for f in xml_output/ch04_sect_4.*.xml; do
  echo "$(basename $f): $(grep -c '<problem' $f) problems"
done

# All problem numbers in a section
grep -o 'number="[0-9]*"' xml_output/ch03_sect_3.1.xml | grep -v chapter | sort -t'"' -k2 -n
```

### Determine which sections cover a concept

```bash
# Which sections mention "SVD" or "singular value"?
grep -ril "singular value\|SVD" xml_output/ch*_sect_*.xml | sort -V

# Sections with formal definitions AND mentioning "orthogonal"
comm -12 \
  <(grep -rl 'type="definition"' xml_output/ch*_sect_*.xml | sort -V) \
  <(grep -rl "orthogonal" xml_output/ch*_sect_*.xml | sort -V)
```

### Check if a section covers a topic at all

```bash
# Does section 2.3 mention "eigenvalue"? (quick prerequisite check)
grep -qi "eigenvalue" xml_output/ch02_sect_2.3.xml && echo "YES" || echo "NO"
```

### Extract all math from exercises in a section

```bash
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('xml_output/ch01_sect_1.1.xml')
for ex in tree.iter('exercises'):
    for p in ex.iter('problem'):
        for m in p.iter('math'):
            print(f'[{p.get(\"number\")}] {m.text}')
" | head -20
```

---

## Knowledge Ordering Reference

**Canonical book order for future-learning checks.**
`sort -V` on filenames in `xml_output/` gives this exact order.

| # | Unit | File | Title |
|--:|------|------|-------|
| 1 | 1.1 | ch01_sect_1.1.xml | Systems of Linear Equations |
| 2 | 1.2 | ch01_sect_1.2.xml | Row Reduction and Echelon Forms |
| 3 | 1.3 | ch01_sect_1.3.xml | Vector Equations |
| 4 | 1.4 | ch01_sect_1.4.xml | The Matrix Equation Ax = b |
| 5 | 1.5 | ch01_sect_1.5.xml | Solution Sets of Linear Systems |
| 6 | 1.6 | ch01_sect_1.6.xml | Applications of Linear Systems |
| 7 | 1.7 | ch01_sect_1.7.xml | Linear Independence |
| 8 | 1.8 | ch01_sect_1.8.xml | Introduction to Linear Transformations |
| 9 | 1.9 | ch01_sect_1.9.xml | The Matrix of a Linear Transformation |
| 10 | 1.10 | ch01_sect_1.10.xml | Linear Models in Business, Science, and Engineering |
| 11 | 2.1 | ch02_sect_2.1.xml | Matrix Operations |
| 12 | 2.2 | ch02_sect_2.2.xml | The Inverse of a Matrix |
| 13 | 2.3 | ch02_sect_2.3.xml | Characterizations of Invertible Matrices |
| 14 | 2.4 | ch02_sect_2.4.xml | Partitioned Matrices |
| 15 | 2.5 | ch02_sect_2.5.xml | Matrix Factorizations |
| 16 | 2.6 | ch02_sect_2.6.xml | The Leontief Input–Output Model |
| 17 | 2.7 | ch02_sect_2.7.xml | Applications to Computer Graphics |
| 18 | 2.8 | ch02_sect_2.8.xml | Subspaces of Rⁿ |
| 19 | 2.9 | ch02_sect_2.9.xml | Dimension and Rank |
| 20 | 3.1 | ch03_sect_3.1.xml | Introduction to Determinants |
| 21 | 3.2 | ch03_sect_3.2.xml | Properties of Determinants |
| 22 | 3.3 | ch03_sect_3.3.xml | Cramer's Rule, Volume, and Linear Transformations |
| 23 | 4.1 | ch04_sect_4.1.xml | Vector Spaces and Subspaces |
| 24 | 4.2 | ch04_sect_4.2.xml | Null Spaces, Column Spaces, Row Spaces, and Linear Transformations |
| 25 | 4.3 | ch04_sect_4.3.xml | Linearly Independent Sets; Bases |
| 26 | 4.4 | ch04_sect_4.4.xml | Coordinate Systems |
| 27 | 4.5 | ch04_sect_4.5.xml | The Dimension of a Vector Space |
| 28 | 4.6 | ch04_sect_4.6.xml | Change of Basis |
| 29 | 4.7 | ch04_sect_4.7.xml | Digital Signal Processing |
| 30 | 4.8 | ch04_sect_4.8.xml | Applications to Difference Equations |
| 31 | 5.1 | ch05_sect_5.1.xml | Eigenvectors and Eigenvalues |
| 32 | 5.2 | ch05_sect_5.2.xml | The Characteristic Equation |
| 33 | 5.3 | ch05_sect_5.3.xml | Diagonalization |
| 34 | 5.4 | ch05_sect_5.4.xml | Eigenvectors and Linear Transformations |
| 35 | 5.5 | ch05_sect_5.5.xml | Complex Eigenvalues |
| 36 | 5.6 | ch05_sect_5.6.xml | Discrete Dynamical Systems |
| 37 | 5.7 | ch05_sect_5.7.xml | Applications to Differential Equations |
| 38 | 5.8 | ch05_sect_5.8.xml | Iterative Estimates for Eigenvalues |
| 39 | 5.9 | ch05_sect_5.9.xml | Applications to Markov Chains |
| 40 | 6.1 | ch06_sect_6.1.xml | Inner Product, Length, and Orthogonality |
| 41 | 6.2 | ch06_sect_6.2.xml | Orthogonal Sets |
| 42 | 6.3 | ch06_sect_6.3.xml | Orthogonal Projections |
| 43 | 6.4 | ch06_sect_6.4.xml | The Gram–Schmidt Process |
| 44 | 6.5 | ch06_sect_6.5.xml | Least-Squares Problems |
| 45 | 6.6 | ch06_sect_6.6.xml | Machine Learning and Linear Models |
| 46 | 6.7 | ch06_sect_6.7.xml | Inner Product Spaces |
| 47 | 6.8 | ch06_sect_6.8.xml | Applications of Inner Product Spaces |
| 48 | 7.1 | ch07_sect_7.1.xml | Diagonalization of Symmetric Matrices |
| 49 | 7.2 | ch07_sect_7.2.xml | Quadratic Forms |
| 50 | 7.3 | ch07_sect_7.3.xml | Constrained Optimization |
| 51 | 7.4 | ch07_sect_7.4.xml | The Singular Value Decomposition |
| 52 | 7.5 | ch07_sect_7.5.xml | Applications to Image Processing and Statistics |
| 53 | 8.1 | ch08_sect_8.1.xml | Affine Combinations |
| 54 | 8.2 | ch08_sect_8.2.xml | Affine Independence |
| 55 | 8.3 | ch08_sect_8.3.xml | Convex Combinations |
| 56 | 8.4 | ch08_sect_8.4.xml | Hyperplanes |
| 57 | 8.5 | ch08_sect_8.5.xml | Polytopes |
| 58 | 8.6 | ch08_sect_8.6.xml | Curves and Surfaces |
| 59 | 9.1 | ch09_sect_9.1.xml | Matrix Games |
| 60 | 9.2 | ch09_sect_9.2.xml | Linear Programming—Geometric Method |
| 61 | 9.3 | ch09_sect_9.3.xml | Linear Programming—Simplex Method |
| 62 | 9.4 | ch09_sect_9.4.xml | Duality |
| 63 | 10.1 | ch10_sect_10.1.xml | Introduction and Examples (Markov Chains) |
| 64 | 10.2 | ch10_sect_10.2.xml | The Steady-State Vector and Google's PageRank |
| 65 | 10.3 | ch10_sect_10.3.xml | Communication Classes |
| 66 | 10.4 | ch10_sect_10.4.xml | Classification of States and Periodicity |
| 67 | 10.5 | ch10_sect_10.5.xml | The Fundamental Matrix |
| 68 | 10.6 | ch10_sect_10.6.xml | Markov Chains and Baseball Statistics |

---

## Content Stats by Section

`Probs` = exercises · `Defs` = formal definitions · `Thms` = key theorems · `Procs` = procedures · `Exs` = worked examples

| Unit | Title | File | Probs | Defs | Thms | Procs | Exs |
|------|-------|------|------:|-----:|-----:|------:|----:|
| **Ch 1 — Linear Equations in Linear Algebra** | | | | | | | |
| 1.1 | Systems of Linear Equations | ch01_sect_1.1.xml | 44 | 0 | 2 | 0 | 3 |
| 1.2 | Row Reduction and Echelon Forms | ch01_sect_1.2.xml | 47 | 2 | 0 | 2 | 5 |
| 1.3 | Vector Equations | ch01_sect_1.3.xml | 53 | 1 | 3 | 0 | 7 |
| 1.4 | The Matrix Equation Ax = b | ch01_sect_1.4.xml | 52 | 1 | 2 | 3 | 5 |
| 1.5 | Solution Sets of Linear Systems | ch01_sect_1.5.xml | 52 | 0 | 1 | 1 | 3 |
| 1.6 | Applications of Linear Systems | ch01_sect_1.6.xml | 14 | 0 | 0 | 0 | 2 |
| 1.7 | Linear Independence | ch01_sect_1.7.xml | 50 | 1 | 2 | 3 | 6 |
| 1.8 | Introduction to Linear Transformations | ch01_sect_1.8.xml | 48 | 1 | 1 | 0 | 6 |
| 1.9 | The Matrix of a Linear Transformation | ch01_sect_1.9.xml | 48 | 2 | 0 | 3 | 5 |
| 1.10 | Linear Models | ch01_sect_1.10.xml | 18 | 0 | 0 | 0 | 3 |
| **Ch 2 — Matrix Algebra** | | | | | | | |
| 2.1 | Matrix Operations | ch02_sect_2.1.xml | 54 | 1 | 2 | 3 | 10 |
| 2.2 | The Inverse of a Matrix | ch02_sect_2.2.xml | 54 | 0 | 3 | 4 | 7 |
| 2.3 | Characterizations of Invertible Matrices | ch02_sect_2.3.xml | 57 | 0 | 1 | 2 | 2 |
| 2.4 | Partitioned Matrices | ch02_sect_2.4.xml | 31 | 0 | 0 | 1 | 5 |
| 2.5 | Matrix Factorizations | ch02_sect_2.5.xml | 34 | 0 | 0 | 0 | 3 |
| 2.6 | The Leontief Input–Output Model | ch02_sect_2.6.xml | 16 | 0 | 0 | 1 | 2 |
| 2.7 | Applications to Computer Graphics | ch02_sect_2.7.xml | 25 | 0 | 0 | 0 | 8 |
| 2.8 | Subspaces of Rⁿ | ch02_sect_2.8.xml | 46 | 4 | 0 | 2 | 8 |
| 2.9 | Dimension and Rank | ch02_sect_2.9.xml | 38 | 3 | 0 | 3 | 3 |
| **Ch 3 — Determinants** | | | | | | | |
| 3.1 | Introduction to Determinants | ch03_sect_3.1.xml | 53 | 1 | 0 | 2 | 3 |
| 3.2 | Properties of Determinants | ch03_sect_3.2.xml | 54 | 0 | 2 | 4 | 5 |
| 3.3 | Cramer's Rule, Volume, and Linear Transformations | ch03_sect_3.3.xml | 42 | 0 | 2 | 4 | 5 |
| **Ch 4 — Vector Spaces** | | | | | | | |
| 4.1 | Vector Spaces and Subspaces | ch04_sect_4.1.xml | 54 | 2 | 1 | 1 | 13 |
| 4.2 | Null Spaces, Column Spaces, Row Spaces, and Linear Transformations | ch04_sect_4.2.xml | 58 | 3 | 1 | 2 | 11 |
| 4.3 | Linearly Independent Sets; Bases | ch04_sect_4.3.xml | 50 | 1 | 0 | 4 | 11 |
| 4.4 | Coordinate Systems | ch04_sect_4.4.xml | 42 | 1 | 0 | 2 | 7 |
| 4.5 | The Dimension of a Vector Space | ch04_sect_4.5.xml | 59 | 2 | 1 | 6 | 8 |
| 4.6 | Change of Basis | ch04_sect_4.6.xml | 26 | 0 | 0 | 1 | 3 |
| 4.7 | Digital Signal Processing | ch04_sect_4.7.xml | 32 | 1 | 0 | 3 | 4 |
| 4.8 | Applications to Difference Equations | ch04_sect_4.8.xml | 43 | 0 | 0 | 2 | 6 |
| **Ch 5 — Eigenvalues and Eigenvectors** | | | | | | | |
| 5.1 | Eigenvectors and Eigenvalues | ch05_sect_5.1.xml | 48 | 2 | 0 | 2 | 5 |
| 5.2 | The Characteristic Equation | ch05_sect_5.2.xml | 35 | 0 | 1 | 3 | 5 |
| 5.3 | Diagonalization | ch05_sect_5.3.xml | 42 | 0 | 0 | 3 | 6 |
| 5.4 | Eigenvectors and Linear Transformations | ch05_sect_5.4.xml | 37 | 1 | 1 | 1 | 5 |
| 5.5 | Complex Eigenvalues | ch05_sect_5.5.xml | 33 | 0 | 0 | 1 | 9 |
| 5.6 | Discrete Dynamical Systems | ch05_sect_5.6.xml | 18 | 0 | 0 | 0 | 7 |
| 5.7 | Applications to Differential Equations | ch05_sect_5.7.xml | 22 | 0 | 0 | 0 | 3 |
| 5.8 | Iterative Estimates for Eigenvalues | ch05_sect_5.8.xml | 21 | 0 | 0 | 0 | 3 |
| 5.9 | Applications to Markov Chains | ch05_sect_5.9.xml | 33 | 1 | 0 | 2 | 6 |
| **Ch 6 — Orthogonality and Least Squares** | | | | | | | |
| 6.1 | Inner Product, Length, and Orthogonality | ch06_sect_6.1.xml | 45 | 3 | 1 | 3 | 6 |
| 6.2 | Orthogonal Sets | ch06_sect_6.2.xml | 25 | 1 | 0 | 4 | 7 |
| 6.3 | Orthogonal Projections | ch06_sect_6.3.xml | 38 | 0 | 0 | 3 | 5 |
| 6.4 | The Gram–Schmidt Process | ch06_sect_6.4.xml | 31 | 0 | 0 | 2 | 4 |
| 6.5 | Least-Squares Problems | ch06_sect_6.5.xml | 36 | 1 | 0 | 3 | 5 |
| 6.6 | Machine Learning and Linear Models | ch06_sect_6.6.xml | 40 | 0 | 0 | 0 | 5 |
| 6.7 | Inner Product Spaces | ch06_sect_6.7.xml | 34 | 1 | 0 | 2 | 8 |
| 6.8 | Applications of Inner Product Spaces | ch06_sect_6.8.xml | 19 | 0 | 0 | 0 | 4 |
| **Ch 7 — Symmetric Matrices and Quadratic Forms** | | | | | | | |
| 7.1 | Diagonalization of Symmetric Matrices | ch07_sect_7.1.xml | 46 | 0 | 1 | 3 | 4 |
| 7.2 | Quadratic Forms | ch07_sect_7.2.xml | 37 | 1 | 0 | 2 | 6 |
| 7.3 | Constrained Optimization | ch07_sect_7.3.xml | 17 | 0 | 0 | 3 | 6 |
| 7.4 | The Singular Value Decomposition | ch07_sect_7.4.xml | 29 | 0 | 0 | 3 | 8 |
| 7.5 | Applications to Image Processing and Statistics | ch07_sect_7.5.xml | 15 | 0 | 0 | 0 | 5 |
| **Ch 8 — The Geometry of Vector Spaces** | | | | | | | |
| 8.1 | Affine Combinations | ch08_sect_8.1.xml | 36 | 4 | 0 | 4 | 4 |
| 8.2 | Affine Independence | ch08_sect_8.2.xml | 38 | 2 | 0 | 2 | 6 |
| 8.3 | Convex Combinations | ch08_sect_8.3.xml | 32 | 2 | 0 | 4 | 4 |
| 8.4 | Hyperplanes | ch08_sect_8.4.xml | 36 | 2 | 0 | 3 | 8 |
| 8.5 | Polytopes | ch08_sect_8.5.xml | 28 | 3 | 0 | 3 | 5 |
| 8.6 | Curves and Surfaces | ch08_sect_8.6.xml | 31 | 0 | 0 | 0 | 2 |
| **Ch 9 — Optimization** | | | | | | | |
| 9.1 | Matrix Games | ch09_sect_9.1.xml | 34 | 5 | 0 | 5 | 6 |
| 9.2 | Linear Programming—Geometric Method | ch09_sect_9.2.xml | 22 | 1 | 0 | 1 | 6 |
| 9.3 | Linear Programming—Simplex Method | ch09_sect_9.3.xml | 26 | 1 | 0 | 0 | 8 |
| 9.4 | Duality | ch09_sect_9.4.xml | 30 | 0 | 0 | 2 | 5 |
| **Ch 10 — Markov Chains** | | | | | | | |
| 10.1 | Introduction and Examples | ch10_sect_10.1.xml | 58 | 0 | 0 | 0 | 7 |
| 10.2 | The Steady-State Vector and Google's PageRank | ch10_sect_10.2.xml | 48 | 2 | 0 | 1 | 5 |
| 10.3 | Communication Classes | ch10_sect_10.3.xml | 47 | 3 | 0 | 2 | 4 |
| 10.4 | Classification of States and Periodicity | ch10_sect_10.4.xml | 40 | 3 | 0 | 2 | 9 |
| 10.5 | The Fundamental Matrix | ch10_sect_10.5.xml | 54 | 0 | 0 | 2 | 4 |
| 10.6 | Markov Chains and Baseball Statistics | ch10_sect_10.6.xml | 23 | 0 | 0 | 0 | 4 |

---

## Back Matter

| File | Contents |
|------|----------|
| `unclassified_appendix_a.xml` | Appendix A: Uniqueness of the Reduced Echelon Form (proof) |
| `unclassified_appendix_b.xml` | Appendix B: Complex Numbers |
| `unclassified_appendix_1.xml` | Appendix 1: Proof of Theorem 1 |
| `unclassified_appendix_2.xml` | Appendix 2: Probability |
| `unclassified_glossary.xml` | Glossary of all key terms |
| `unclassified_index.xml` | Book index (term → page references) |
| `ch*_sect_supplementary.xml` | Chapter supplementary exercises |
| `ch*_sect_projects.xml` | Chapter projects (open-ended) |

```bash
# Search the glossary for a term definition
grep -A5 "eigenvalue" xml_output/unclassified_glossary.xml

# Find appendix proof content
grep -n "echelon" xml_output/unclassified_appendix_a.xml
```
