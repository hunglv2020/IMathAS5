---
topic: "draw"
tags: ["draw", "graph", "plot", "drawing", "answerbox"]
---

# Type: `"draw"` — Graph Drawing

Student draws one or more curves, lines, or dots on a coordinate plane. The engine compares the drawn shape against the correct answer function or coordinates.

---

## Required Variables

```php
$anstypes[i]  = "draw";
$answers[i]   = array("x^2 + 3");            // PLURAL — array of curve/dot expressions
$answerformat[i] = "twopoint";               // RECOMMENDED: modern drawing toolset
```

> **Use `$answers[i]` (PLURAL)** — an array of answer elements (each curve or dot is one entry).

---

## Answer Expression Formats (inside `$answers[i]` array)

| Shape | Expression format | Example |
|---|---|---|
| Curve (function of x) | `"f(x)"` | `"x^2 - 3"` |
| Line segment / ray | `"f(x), xmin, xmax"` | `"2*x+1, -oo, 3"` |
| Vertical line | `"x=n"` | `"x=4"` |
| Closed dot | `"x, y"` | `"2, 3"` |
| Open dot | `"x, y, open"` | `"-1, 0, open"` |
| Circle | `"circle, cx, cy, r"` | `"circle, 0, 0, 3"` |
| Horizontal parabola | `"x=f(y)"` | `"x=2*(y-1)^2-3"` |

---

## Patterns

### A — Single curve (twopoint toolset)
```php
$anstypes[0]   = "draw";
$answers[0]    = array("x^2 - 3");
$answerformat[0] = "twopoint";
$grid[0]       = "-5,5,-5,5,1,1,300,300";
```

### B — Line with open/closed endpoints
```php
$anstypes[1]   = "draw";
$answers[1]    = array("2*x+1, -3, 4", "-3, -5, open", "4, 9");
$answerformat[1] = "twopoint,lineseg,dot,opendot";
```

### C — Multiple curves (piecewise)
```php
$anstypes[2]   = "draw";
$answers[2]    = array("x^2, -oo, 0", "2*x, 0, oo", "0, 0");   // curve + dot
$answerformat[2] = "twopoint";
```

### D — Inequality shading
```php
$anstypes[3]   = "draw";
$answers[3]    = array(">=2*x+1");   // shade above the line y = 2x+1
$answerformat[3] = "inequality";
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$answerformat[i]` | `"twopoint"` (recommended modern tools), `"inequality"`, `"numberline"`, or comma-separated tool list: `"twopoint,line,dot,parab,circle"` |
| `$grid[i]` | `"xmin,xmax,ymin,ymax,xscl,yscl,w,h"` — defaults to `"-5,5,-5,5,1,1,300,300"` |
| `$background[i]` | Background graph or SVG — e.g. `"x^2,red"` for a red reference curve |
| `$snaptogrid[i]` | Grid snapping step — `1` snaps to integers, `0.5` to half-integers |
| `$reltolerance[i]` | Grading tolerance scale (default 1; set 2 for more lenient) |
| `$partweights[i]` | Weight per element in `$answers[i]` |
| `$scoremethod[i]` | `"direction"` or `"relativelength"` (for vectors) |

---

## ⚠️ Pitfalls

- `$answers[i]` is PLURAL and an **array** — each element is one drawable object.
- `$answerformat[i] = "twopoint"` is the modern toolset. The older `"line,dot,opendot"` tools are still valid but should not be used for new questions.
- The question_gen tag `[ANSWERBOX:draw:...]` provides a reference expression only — the agent writing `control.php` must determine the correct `$answerformat[i]` and `$grid[i]` from the question context.
- `$reltolerance[i]` scales leniency, not an absolute error bound — `reltolerance=2` doubles tolerance.
