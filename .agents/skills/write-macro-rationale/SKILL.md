---
name: write-macro-rationale
description: Write reusable IMathAS macro rationales for Odoo Text fields, based on the current session context, current workspace files, and current template discussion. Use when the user wants rationale blocks for one or more macros in any template or session, especially for golden macro reuse through write-imathas-x. Output one block per macro, tie the explanation tightly to the current implementation, include a concrete bad case when available, and prefer rendered-seed evidence over abstract prose.
---

# Skill: write-macro-rationale

Use this skill when the user wants reusable rationale text for one or more IMathAS macros in any IMathAS template.

The output is meant to be copied into a plain Odoo `rationale` Text field, so it must be:

- reusable
- macro-centric
- tightly tied to the current implementation
- concise, but concrete

## What to read first

1. Read the current `questions/qt-{id}/imathas/control.php` or the equivalent control logic in the active package.
2. Read any relevant question and solution text that consume the macro output.
3. Read the current discussion to recover any explicit bad case or rejected pattern.
4. If needed, render one representative seed to prove the display/grading effect in the final output.

Prefer using current-session evidence over generic explanation.

## Required output shape

Return one block per macro.

Each block should use this compact structure:

```md
### `<macro>`

<one concise paragraph>
```

The paragraph should naturally cover:

- what the macro is doing here
- how it is used in the current implementation
- one concrete rendered effect if relevant
- one concrete bad case if available
- why the refined macro-based pattern is better

## Content rules

For each macro block:

- Tie the explanation to the actual variables and lines in the current implementation.
- Mention the real control variables if they matter, for example `$diffeqraw`, `$diffeqdisp`, `$auxpoly`, `$root2,$root3`.
- Explain how the macro affects the injected question or solution content, but refer to them as `question` and `solution`, not file extensions.
- If a rendered seed shows the effect clearly, include one short before/after example from that seed.
- If there is a real bad case in the session history or current code evolution, include it explicitly.
- The bad case can be small, but it must be concrete.
- Do not invent a bad case if none exists; omit it rather than padding.

## Style rules

- Write in English unless the user explicitly requests another language.
- Avoid generic macro definitions unless they are needed to explain the choice.
- Default to one paragraph per macro.
- Target 4 to 6 sentences per block.
- Avoid long prose paragraphs that drift away from the current implementation.
- Prefer concrete evidence:
  - actual variable names
  - actual raw string forms
  - actual rendered cleanup
  - actual rejected branch-heavy or manual patterns
- Do not mention Odoo, XML, lookup scripts, or “this session” inside the rationale blocks.
- Do not mention ZONE numbers; structure may shift and the rationale should stay reusable.
- Do not use subsection headings such as `Purpose`, `Bad case`, or `Rendered effect` in the final output unless the user explicitly asks for the longer form.

## Common rationale framework

For every requested macro, think through the same framework internally:

1. **Purpose**
   State the narrow authoring problem the macro is solving in this implementation.

2. **Actual usage**
   Identify the concrete control variables or expressions that use the macro.

3. **Downstream effect**
   Explain how the macro’s output becomes visible in question, solution, display quality, grading stability, or control organization.

4. **Rendered evidence**
   If the effect is visible in final output, include one short rendered before/after or one rendered example from a representative seed.

5. **Bad case**
   Recover one weaker alternative from the current context when possible, such as:
   - branch-heavy formatting logic
   - manual string assembly
   - repeated randomization plus filtering
   - hand-built math formatting
   - duplicated logic across multiple display targets

6. **Refined pattern**
   Explain why the current macro-based pattern is better in this implementation.

If one of these elements is not available, do not invent content. Just keep the paragraph tighter.

## Default working method

For each requested macro:

1. Locate the macro usage in `control.php`.
   If the package uses a different control filename or structure, inspect the equivalent source instead.
2. Identify the downstream variables consumed by the question or solution.
3. Recover one concrete bad case from:
   - prior discussion
   - nearby rejected code pattern
   - an obviously weaker alternative replaced by the current code
4. Render one seed if the macro effect is primarily visible in final display.
5. Write one self-contained rationale block for that macro as a short paragraph.

If the user requests multiple macros, produce one block per macro.

Do not merge multiple macros into a single block unless the user explicitly asks for a combined rationale.

## Generality requirement

This skill must remain reusable across different templates, topics, and sessions.

- Do not assume a specific math topic.
- Do not assume the package has the same variables as previous runs.
- Do not assume the same macros are always present.
- Recompute the rationale from the current context each time.
- Treat old examples only as pattern hints, never as fixed content to reuse blindly.
