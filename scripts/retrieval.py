#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["rank_bm25"]
# ///
"""
retrieval.py — BM25-based knowledge retrieval with curriculum filtering.

Provides KnowledgeIndex class for searching knowledge atoms with:
- Unit digest: all atoms in a given unit
- Concept search: BM25 search filtered to prior units only
- Atom lookup: retrieve a single atom by ID

Usage (CLI demo):
    python scripts/retrieval.py \\
        --atoms shared/books/linear-algebra/atoms.json \\
        --query "pivot position echelon form" \\
        --current-unit "2.3" \\
        --top-k 3

Usage (as library):
    from retrieval import KnowledgeIndex
    idx = KnowledgeIndex("shared/books/linear-algebra/atoms.json")
    results = idx.search_concept("pivot position", current_unit_code="2.3")
"""

import argparse
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in text.split() if len(t) > 1]


def parse_unit_code(code: str) -> tuple[int, int]:
    """Parse '4.1' → (4, 1). Handles edge cases like '1.10'."""
    parts = code.split(".")
    if len(parts) == 2:
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return (0, 0)


class KnowledgeIndex:
    """BM25-indexed knowledge atom store with curriculum-aware search."""

    def __init__(self, atoms_json_path: str | Path):
        path = Path(atoms_json_path)
        self.atoms: list[dict] = json.loads(path.read_text())
        self._by_id: dict[str, dict] = {a["atom_id"]: a for a in self.atoms}
        self._by_unit: dict[str, list[dict]] = {}
        for a in self.atoms:
            uc = a["unit_code"]
            if uc not in self._by_unit:
                self._by_unit[uc] = []
            self._by_unit[uc].append(a)

        self._corpus_tokens: list[list[str]] = []
        for a in self.atoms:
            doc = " ".join([
                a.get("unit_title", ""),
                a.get("title", ""),
                " ".join(a.get("concept_tags", [])),
                a.get("snippet", ""),
            ])
            self._corpus_tokens.append(tokenize(doc))

        self._bm25 = BM25Okapi(self._corpus_tokens)

        self._unit_seq: dict[str, tuple[int, int]] = {}
        for a in self.atoms:
            uc = a["unit_code"]
            if uc not in self._unit_seq:
                seq = a.get("seq", [0, 0])
                self._unit_seq[uc] = (seq[0], seq[1])

    def get_unit_digest(self, unit_code: str) -> list[dict]:
        """Return all atoms belonging to the given unit."""
        return list(self._by_unit.get(unit_code, []))

    def get_atom(self, atom_id: str) -> dict | None:
        """Return a single atom by ID."""
        return self._by_id.get(atom_id)

    def search_concept(
        self,
        query: str,
        current_unit_code: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        BM25 search filtered to atoms from units strictly before current_unit_code.

        Each result dict includes:
        - All atom fields
        - 'bm25_score': float
        - 'needs_refine': bool (True if atom is from a different chapter)
        """
        current_seq = self._unit_seq.get(current_unit_code)
        if current_seq is None:
            current_seq = parse_unit_code(current_unit_code)

        current_chapter = f"ch{current_seq[0]:02d}"

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self._bm25.get_scores(query_tokens)

        scored_atoms: list[tuple[float, dict]] = []
        for i, (score, atom) in enumerate(zip(scores, self.atoms)):
            if score <= 0:
                continue
            atom_seq = self._unit_seq.get(atom["unit_code"], (0, 0))
            if atom_seq >= current_seq:
                continue
            scored_atoms.append((score, atom))

        scored_atoms.sort(key=lambda x: -x[0])

        results = []
        for score, atom in scored_atoms[:top_k]:
            result = dict(atom)
            result["bm25_score"] = round(score, 2)
            result["needs_refine"] = atom["chapter"] != current_chapter
            results.append(result)

        return results

    def list_units(self) -> list[dict]:
        """List all units with their atom counts."""
        units = []
        for uc in sorted(self._by_unit.keys(), key=lambda x: self._unit_seq.get(x, (0, 0))):
            atoms = self._by_unit[uc]
            units.append({
                "unit_code": uc,
                "unit_title": atoms[0].get("unit_title", ""),
                "atom_count": len(atoms),
                "seq": list(self._unit_seq.get(uc, (0, 0))),
            })
        return units


def main():
    parser = argparse.ArgumentParser(description="BM25 knowledge retrieval with curriculum filtering")
    parser.add_argument("--atoms", type=Path, required=True, help="Path to atoms.json")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--current-unit", type=str, help="Current unit code (e.g., '2.3')")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results")
    parser.add_argument("--digest", type=str, help="Get unit digest for this unit code")
    parser.add_argument("--atom-id", type=str, help="Get atom by ID")
    parser.add_argument("--list-units", action="store_true", help="List all units")
    args = parser.parse_args()

    idx = KnowledgeIndex(args.atoms)

    if args.list_units:
        for u in idx.list_units():
            print(f"  {u['unit_code']:8s} ({u['atom_count']:3d} atoms) {u['unit_title']}")
        return

    if args.digest:
        atoms = idx.get_unit_digest(args.digest)
        print(f"Unit {args.digest} digest: {len(atoms)} atoms\n")
        for a in atoms:
            print(f"  {a['atom_id']:40s} {a['atom_type']:15s} {a['title']}")
        return

    if args.atom_id:
        atom = idx.get_atom(args.atom_id)
        if atom:
            print(json.dumps(atom, indent=2, ensure_ascii=False))
        else:
            print(f"Atom not found: {args.atom_id}")
        return

    if args.query and args.current_unit:
        results = idx.search_concept(args.query, args.current_unit, top_k=args.top_k)
        print(f"Search: '{args.query}' at unit {args.current_unit} (top {args.top_k})\n")
        if not results:
            print("  No results found.")
        for r in results:
            refine = "needs_refine" if r["needs_refine"] else "verbatim"
            print(f"  score={r['bm25_score']:6.2f}  {r['atom_id']:40s}  unit={r['unit_code']:5s}  {refine}")
            print(f"         title: {r['title']}")
            print(f"         snippet: {r['snippet'][:100]}...")
            print()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
