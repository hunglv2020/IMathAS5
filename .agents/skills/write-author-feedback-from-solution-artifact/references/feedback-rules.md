# Feedback Rules

## Core intent

This skill writes guidance for the original IMathAS author so they can improve the explanation in
the current solution template.

The goal is not to rewrite the solution and not to ask the author to copy the reviewed artifact.

## What to prioritize

- Missing justification before a method begins
- Prior knowledge mentioned only by name, without a short restatement
- Definitions the student needs but the solution skips
- Verification that relies on external tools or vague assurance
- Conclusions that do not explicitly connect back to the method
- Places where injected math strings are present but the surrounding prose is too weak
- Concrete missing computation or transition steps when the explanation jumps too far
- Specific sentence replacements when one opaque line is doing too much work

## What to avoid

- Generic comments such as `make it clearer`
- Feedback about artifact-only policies unless the same issue appears in the IMathAS solution
- Broad review of `control.php` structure, randomization, or answer config
- Requests to copy wording from the artifact
- Coverage, pedagogical, or accuracy findings that are not actually evidenced by the compared texts
- Internal filenames, workflow labels, or audit jargon in the final author-facing bullets

## Preferred bullet shape

Each bullet should ideally do three things in one short move:

1. state the current issue
2. cite a short quote if that helps locate the issue
3. state the explanation improvement the author should make

Example shape:

- Please define the mathematical idea before the procedural command. The line "Set the derivative
  equal to zero" should first explain what counts as a critical number.

When the evidence is stronger, a bullet may also preserve a concrete target such as:

- Please split the current jump from the derivative to the interval conclusion into two steps:
  first show the sign test on each interval, then state the increasing/decreasing conclusion.

## Quote policy

- Quotes should be short.
- Use double quotes.
- Quote only text that actually appears in the current IMathAS explanation or rendered snapshot.
- Do not quote large passages.

## Translation policy

- Write the English bullets first.
- The Vietnamese section must preserve the same issues and the same level of directness.
- Do not add new findings in Vietnamese.
