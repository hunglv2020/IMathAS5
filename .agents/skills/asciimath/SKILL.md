---
name: asciimath
description: AsciiMath helper skill for syntax lookup and LaTeX-to-AsciiMath conversion. Keeps local conversion guidance close to the converter scripts and reference file.
---

# Skill: asciimath

## Purpose

Handle AsciiMath syntax lookup and LaTeX-to-AsciiMath conversion for IMathAS text artifacts.

## Scope

In scope:
- AsciiMath syntax reference
- conversion of static LaTeX text before parameterization
- spot-checking or correcting a single expression

Out of scope:
- IMathAS control authoring
- audit decisions
- macro or answerbox logic

## Read First

1. required policy: `p-text`
2. `references/asciimath-reference.md`

## Retrieval Expansion Triggers

Open conversion script details only when:
- the task is actual LaTeX conversion
- a converted expression needs spot-checking

## Validator-First Steps

- If the source contains PHP/IMathAS `$vars`, do not run bulk LaTeX conversion over that file.
- Use expression mode for spot checks before manual edits.

## Local References and Tools

- Syntax reference: `references/asciimath-reference.md`
- Bulk/file conversion:
  - `uv run python .agents/skills/asciimath/scripts/cli.py <input> <output>`
- Stdin conversion:
  - `uv run python .agents/skills/asciimath/scripts/cli.py --stdin`
- Expression mode:
  - `uv run python .agents/skills/asciimath/scripts/cli.py -e '<latex expression>'`

## Stop / Escalate Conditions

- Escalate to the user only if the source material is structurally incompatible with the converter and manual normalization would materially rewrite content
