# Retrieval Policy — build-solution-artifact

## Escalation order

1. **Current-unit digest** — always loaded, zero extra cost
2. **BM25 search on prior units** — only when gaps are detected in draft
3. **Manual unit XML read** — only when BM25 results are insufficient and the agent
   needs worked-example context from a specific prior unit

Do NOT:
- Load the full chapter XML by default
- Pre-load broad textbook context before gaps are detected
- Use semantic/dense vector retrieval (BM25 is sufficient for this corpus)

## BM25 search parameters

- Corpus: `atoms.json` per book (title + concept_tags + snippet)
- Curriculum filter: only atoms where `seq < current_unit_seq` (strictly before)
- Default `top_k`: 3 results per gap query
- Scoring: BM25Okapi with whitespace tokenization

## needs_refine classification

- Same chapter as current unit → `needs_refine = False` → use atom verbatim
- Different chapter → `needs_refine = True` → must generate concept bridge

Rationale: same-chapter content was learned recently (student likely remembers).
Different-chapter content may be weeks or months old in the student's experience.

## When to escalate beyond BM25

If BM25 returns no results for a gap query:
1. Try rephrasing the query using concept names from the unit digest
2. Try broadening the query to more general terms
3. If still no results: log as `unresolved_gap` — do not hallucinate an atom

## Token budget

- Unit digest: ~50-200 tokens per atom × ~5-15 atoms per unit = ~250-3000 tokens
- BM25 results: ~3 atoms × ~300 tokens = ~900 tokens
- Bridge generation: ~200 tokens per bridge
- Total retrieval overhead per solution: ~1000-5000 tokens
