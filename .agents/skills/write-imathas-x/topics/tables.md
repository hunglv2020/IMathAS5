---
name: tables
description: Creation of accessible, dynamic HTML tables in IMathAS using showarrays, showrecttable, and horizshowarrays. Includes Answerbox tag embedding and result summary patterns.
---

# Reference: IMathAS Dynamic Tables (Accessible & Responsive)

Covers the generation of HTML tables using IMathAS core macros. Tables are the premium way to present multi-part data, compare extrema, or summarize results.

## 1. Math Formatting in Tables (CRITICAL)

All mathematical content (variables, expressions, even simple years or labels) MUST be wrapped in backticks (<code>\`...\`</code>) inside the PHP arrays. If values are dynamic, pass them through `makexxpretty`.

### 🛠️ Example: Formatting dynamic cells
```php
$A = 1; $B = -3;
$f_cell = makexxpretty("{$A} x^2 + {$B}"); // Returns "x^2 - 3"
$year = 2021;

$col1 = array("`x`.", "`$year`.");
$col2 = array("`$f_cell`.", "`100`.");
```

---

## 2. Vertical Tables: `showarrays($headers, $columnArrays)`

`showarrays` is the primary macro for vertical tables (headers are on the first row).

### 🛠️ Syntax
```php
$headers = array("Category", "Value");
$col1 = array("`A`.", "`B`.", "`C`.");
$col2 = array("`10`.", "`20`.", "`30`.");
$table = showarrays($headers, array($col1, $col2));
```

### 💎 Creating "Answerbox Groups"
To create a column of input boxes, use `[ABi]` tags.
```php
$col2 = array("[AB0]", "[AB1]", "[AB2]");
$table_display = showarrays($headers, array($col1, $col2));
```

---

## 3. Horizontal Tables: `horizshowarrays(hdr1, data1, hdr2, data2, ..., [opts])`

`horizshowarrays` is used for horizontal tables (headers are on the first column).

### 🛠️ Syntax
Notice that this macro takes **pairs** of (Label, Array) instead of a list of arrays.
```php
$years = array("`2021`.", "`2022`.");
$profit = array("`$10k`.", "`$15k`.");
$table = horizshowarrays("Year.", $years, "Profit.", $profit, "A horizontal summary.");
```

---

## 4. Grid/Matrix Display: `showrecttable($matrix, $colLabels, $rowLabels, [$opts])`

Use this for 2D grids (like matrices or contingency tables).

### 🛠️ Syntax
⚠️ **Note:** The second parameter is **Column Labels** and the third is **Row Labels**.
```php
$matrix = array( array("`1`","`2`"), array("`3`","`4`") );
$cols = array("`X`.", "`Y`.");
$rows = array("`Row A`.", "`Row B`.");
$grid = showrecttable($matrix, $cols, $rows, "A matrix table.");
```

---

## 5. DESIGN BEST PRACTICES

1.  **Uniform Backticks:** Even static labels like `` `x` `` or `` `2024` `` should be backticked for consistent typography.
2.  **Sentence Case & Periods:** Use Sentence case for all headers and labels. Always end headers or qualitative strings in table cells with a period (`.`).
3.  **Result Summaries ($table_ans):** Always create a companion variable (e.g., `$table_ans`) that replaces `[ABi]` tags with actual calculated values (`$answer[i]`). Use this in the `solution.txt`.
4.  **No `*` in Tables:** In display strings, use spaces for implicit multiplication as per textbook conventions.

---

## 6. EXAMPLE: FULL TABLE TEST WITH `makexxpretty`

### `control.php`
```php
// Dynamic cell
$expr = makexxpretty("1x^2 + -5"); // "x^2-5"
$headers = array("Expression", "Input");
$col1 = array("`$expr`.", "`y`.");
$col2 = array("[AB0]", "[AB1]");
$table_display = showarrays($headers, array($col1, $col2));

// Matrix
$matrix = array( array("`1`","`2`"), array("`3`","`4`") );
$cols = array("`X`.", "`Y`.");
$rows = array("`R1`.", "`R2`.");
$table_matrix = showrecttable($matrix, $cols, $rows);
```
