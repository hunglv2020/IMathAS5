# -*- coding: utf-8 -*-

import re
from typing import Dict, List


class LatexToAsciiMathConverter:
    """Lightweight converter from LaTeX math snippets to AsciiMath (IMathAS flavored)."""

    def __init__(self):
        self.symbol_mappings = {
            # Greek letters (lowercase)
            '\\alpha': 'alpha', '\\beta': 'beta', '\\gamma': 'gamma', '\\delta': 'delta',
            '\\epsilon': 'epsilon', '\\varepsilon': 'varepsilon', '\\zeta': 'zeta', '\\eta': 'eta',
            '\\theta': 'theta', '\\vartheta': 'vartheta', '\\iota': 'iota', '\\kappa': 'kappa',
            '\\lambda': 'lambda', '\\mu': 'mu', '\\nu': 'nu', '\\xi': 'xi', '\\omicron': 'omicron',
            '\\pi': 'pi', '\\varpi': 'varpi', '\\rho': 'rho', '\\varrho': 'varrho',
            '\\sigma': 'sigma', '\\varsigma': 'varsigma', '\\tau': 'tau', '\\upsilon': 'upsilon',
            '\\phi': 'phi', '\\varphi': 'varphi', '\\chi': 'chi', '\\psi': 'psi', '\\omega': 'omega',
            # Greek letters (uppercase)
            '\\Alpha': 'Alpha', '\\Beta': 'Beta', '\\Gamma': 'Gamma', '\\Delta': 'Delta',
            '\\Epsilon': 'Epsilon', '\\Zeta': 'Zeta', '\\Eta': 'Eta', '\\Theta': 'Theta',
            '\\Iota': 'Iota', '\\Kappa': 'Kappa', '\\Lambda': 'Lambda', '\\Mu': 'Mu',
            '\\Nu': 'Nu', '\\Xi': 'Xi', '\\Omicron': 'Omicron', '\\Pi': 'Pi',
            '\\Rho': 'Rho', '\\Sigma': 'Sigma', '\\Tau': 'Tau', '\\Upsilon': 'Upsilon',
            '\\Phi': 'Phi', '\\Chi': 'Chi', '\\Psi': 'Psi', '\\Omega': 'Omega',
            # Binary operations
            '\\times': 'xx', '\\cdot': '*', '\\div': '-:', '\\pm': '+-', '\\mp': '-+',
            '\\ast': '**', '\\star': '***', '\\circ': '@', '\\bullet': 'o+',
            '\\cap': 'cap', '\\cup': 'cup', '\\wedge': '^^', '\\vee': 'vv',
            '\\oplus': 'o+', '\\ominus': 'o-', '\\otimes': 'ox', '\\odot': 'o.',
            '\\bigcap': '^^^', '\\bigcup': 'vvv',
            # Relations
            '\\leq': '<=', '\\le': '<=', '\\geq': '>=', '\\ge': '>=',
            '\\neq': '!=', '\\ne': '!=', '\\approx': '~~', '\\equiv': '-=',
            '\\cong': '~=', '\\sim': '~', '\\simeq': '~=', '\\propto': 'prop',
            '\\prec': '-<', '\\succ': '>-', '\\preceq': '-<=', '\\succeq': '>=-',
            '\\ll': '<<', '\\gg': '>>',
            # Set theory
            '\\in': 'in', '\\notin': 'notin', '\\ni': 'ni', '\\subset': 'sub', '\\supset': 'sup',
            '\\subseteq': 'sube', '\\supseteq': 'supe', '\\subsetneq': 'sub!=', '\\supsetneq': 'sup!=',
            '\\emptyset': 'O/', '\\varnothing': 'O/',
            # Logic
            '\\land': '^^', '\\lor': 'vv', '\\lnot': 'not', '\\neg': 'not',
            '\\implies': '=>', '\\impliedby': '<=', '\\iff': '<=>',
            '\\Rightarrow': '=>', '\\Leftarrow': '<=', '\\Leftrightarrow': '<=>',
            '\\exists': 'EE', '\\forall': 'AA', '\\nexists': '!EE',
            # Arrows
            '\\rightarrow': '->', '\\to': '->', '\\leftarrow': '<-', '\\gets': '<-',
            '\\leftrightarrow': '<->', '\\uparrow': 'uarr', '\\downarrow': 'darr',
            '\\updownarrow': 'updownarr', '\\Uparrow': 'uArr', '\\Downarrow': 'dArr',
            '\\Updownarrow': 'updownArr', '\\nearrow': 'nearr', '\\searrow': 'searr',
            '\\nwarrow': 'nwarr', '\\swarrow': 'swarr', '\\mapsto': '|->',
            '\\longmapsto': '|-->', '\\hookleftarrow': 'hooklarr', '\\hookrightarrow': 'hookrarr',
            # Functions
            '\\sin': 'sin', '\\cos': 'cos', '\\tan': 'tan', '\\cot': 'cot',
            '\\sec': 'sec', '\\csc': 'csc', '\\sinh': 'sinh', '\\cosh': 'cosh',
            '\\tanh': 'tanh', '\\coth': 'coth', '\\arcsin': 'arcsin', '\\arccos': 'arccos',
            '\\arctan': 'arctan', '\\arccot': 'arccot', '\\arcsec': 'arcsec', '\\arccsc': 'arccsc',
            '\\log': 'log', '\\ln': 'ln', '\\lg': 'log', '\\exp': 'exp',
            '\\det': 'det', '\\dim': 'dim', '\\ker': 'ker', '\\deg': 'deg',
            '\\gcd': 'gcd', '\\lcm': 'lcm', '\\min': 'min', '\\max': 'max',
            '\\inf': 'inf', '\\sup': 'sup', '\\lim': 'lim', '\\limsup': 'limsup', '\\liminf': 'liminf',
            # Special symbols
            '\\infty': 'oo', '\\partial': 'del', '\\nabla': 'grad', '\\sum': 'sum', '\\prod': 'prod',
            '\\int': 'int', '\\sqrt': 'sqrt', '\\angle': '/_', '\\triangle': 'triangle',
            '\\iint': 'int int', '\\iiint': 'int int int',
            '\\square': 'square', '\\diamond': 'diamond', '\\clubsuit': 'club',
            '\\diamondsuit': 'diamond', '\\heartsuit': 'heart', '\\spadesuit': 'spade',
            '\\aleph': 'aleph', '\\hbar': 'hbar', '\\imath': 'imath', '\\jmath': 'jmath', '\\bar': 'bar',
            '\\ell': 'ell', '\\wp': 'wp', '\\Re': 'Re', '\\Im': 'Im',
            '\\top': 'TT', '\\bot': '_|_', '\\perp': '_|_', '\\parallel': '||',
            '\\surd': 'sqrt', '\\mid': '|',
            # Dots
            '\\ldots': '...', '\\cdots': '***', '\\vdots': 'vdots', '\\ddots': 'ddots',
            # Number sets
            '\\mathbb{N}': 'NN', '\\mathbb{Z}': 'ZZ', '\\mathbb{Q}': 'QQ', 
            '\\mathbb{R}': 'RR', '\\mathbb{C}': 'CC', '\\mathbb{P}': 'PP',
            # Text formatting
            '\\mathbf': 'bb', '\\mathbb': 'bb', '\\mathcal': 'cc', '\\mathfrak': 'fr',
            '\\mathit': '', '\\mathsf': 'sf', '\\mathtt': 'tt', '\\mathrm': '',
            # Delimiters / brackets
            '\\langle': '(:', '\\rangle': ':)',
        }

        def _superscript_repl(m):
            inner = m.group(1).strip()
            if '/' in inner and inner.count('/') == 1:
                p1, p2 = inner.split('/')
                return f"^(({p1.strip()})/({p2.strip()}))"
            return f"^({inner})"

        def _subscript_repl(m):
            inner = m.group(1).strip()
            if '/' in inner and inner.count('/') == 1:
                p1, p2 = inner.split('/')
                return f"_(({p1.strip()})/({p2.strip()}))"
            return f"_({inner})"

        self.patterns = [
            (r'\\operatorname\{([^{}]+)\}', r'text(\1)'),
            # Common in solutions: \text{div}, \text{Flux}, etc.
            (r'\\text\{([^{}]+)\}', r'text(\1)'),
            (r'\^\{([^{}]+)\}', _superscript_repl),
            (r'_\{([^{}]+)\}', _subscript_repl),
            (r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)'),
            (r'\\left\(', '('), (r'\\right\)', ')'),
            (r'\\left\[', '['), (r'\\right\]', ']'),
            (r'\\left\|', 'abs('), (r'\\right\|', ')'),
            (r'\\left', ''), (r'\\right', ''),
        ]

    def convert(self, latex: str) -> str:
        """Convert LaTeX fragment to AsciiMath wrapped with backticks."""
        result = latex.strip()
        result = re.sub(r'\$\$\$\$(.*?)\$\$\$\$', r'`\1`', result)
        result = re.sub(r'\$\$(.*?)\$\$', r'`\1`', result)
        result = re.sub(r'\$(.*?)\$', r'`\1`', result)

        result = _replace_frac_balanced(result)
        result = _replace_matrices(result)

        for pattern, replacement in self.patterns:
            result = re.sub(pattern, replacement, result)

        sorted_mappings = sorted(self.symbol_mappings.items(), key=lambda x: len(x[0]), reverse=True)
        for latex_cmd, asciimath in sorted_mappings:
            result = result.replace(latex_cmd, asciimath)

        return re.sub(r'\s+', ' ', result).strip()


def convert_latex_to_asciimath(text: str) -> str:
    """Convert multiline LaTeX to AsciiMath, preserving line breaks."""
    text = _normalize_aligned_blocks(text)
    converter = LatexToAsciiMathConverter()
    lines = (text or "").splitlines()
    converted = []
    for line in lines:
        if line.strip():
            converted.append(_post_process_asciimath(converter.convert(line)))
        else:
            converted.append("")
    result = "\n".join(converted)
    return _convert_line_breaks(result)


def _post_process_asciimath(text: str) -> str:
    """Apply extra conventions for AsciiMath output."""
    if not text:
        return text

    # Replace \| ... \| with abs(...)
    text = re.sub(r"\\\|\s*(.*?)\s*\\\|", r"abs(\1)", text)

    # Strip markdown bold/italics markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.*?)\*(?!\w)", r"\1", text)

    # Remove LaTeX thin spaces
    text = text.replace(r"\,", "")

    # Strip leftover sizing markers
    text = text.replace(r"\left", "").replace(r"\right", "")

    # Add space after differential d (dx -> d x, dtheta -> d theta)
    # First handle Greek letters and other multi-character symbols
    greek_letters = [
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon', 'zeta', 'eta',
        'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron',
        'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon',
        'phi', 'varphi', 'chi', 'psi', 'omega',
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta',
        'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi',
        'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega'
    ]
    
    # Sort by length (longest first) to avoid partial matches
    for greek in sorted(greek_letters, key=len, reverse=True):
        text = re.sub(rf"(?<!\w)d({re.escape(greek)})\b", rf"d \1", text)
    
    # Then handle single Latin letters
    text = re.sub(r"(?<!\w)d([A-Za-z])\b", r"d \1", text)

    # Handle differentials followed by AsciiMath font wrappers.
    # The converter can emit "dbb{S}" from "d\\mathbf{S}", which breaks parsing.
    text = re.sub(r"(?<!\w)d(bb|cc|fr|sf|tt)\{", r"d \1{", text)

    # Remove heading markers (one or more # + space) at line start
    text = re.sub(r"^\s*#+\s+", "", text)

    # Remove leading bullet markers like "* " at line start
    text = re.sub(r"^\s*\*\s+", "", text)

    return text


def _convert_line_breaks(text: str) -> str:
    """Replace single newlines with <br/>, keep blank lines intact."""
    if not text:
        return text
    # Replace newline not adjacent to another newline with <br/>\n (preserve the newline)
    return re.sub(r"(?<!\n)\n(?!\n)", "<br/>\n", text)


def _replace_frac_balanced(text: str) -> str:
    """Replace \\frac{...}{...} with (num)/(den), allowing nested braces."""
    def parse_braced(s: str, start: int):
        if start >= len(s) or s[start] != "{":
            return None
        depth = 0
        i = start
        while i < len(s):
            ch = s[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start + 1 : i], i + 1
            i += 1
        return None

    out: List[str] = []
    i = 0
    while i < len(text):
        if text.startswith(r"\frac{", i):
            num_den_start = i + len(r"\frac")
            parsed_num = parse_braced(text, num_den_start)
            if not parsed_num:
                out.append(text[i])
                i += 1
                continue
            num, after_num = parsed_num
            parsed_den = parse_braced(text, after_num)
            if not parsed_den:
                out.append(text[i])
                i += 1
                continue
            den, after_den = parsed_den
            out.append(f"({_replace_frac_balanced(num)})/({_replace_frac_balanced(den)})")
            i = after_den
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _normalize_aligned_blocks(text: str) -> str:
    """Handle \\begin{aligned} blocks by flattening and removing & alignment."""
    if not text:
        return text

    def _handle_aligned_body(body: str) -> str:
        """Flatten aligned content into one expression per line wrapped in $..$."""
        body = body.replace("\\\\", "\n")
        body = re.sub(r"^\s*&\s*", "", body, flags=re.MULTILINE)
        body = re.sub(r"\s*&\s*", " ", body)
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        return "\n".join(f"${line}$" for line in lines)

    # Replace aligned blocks wrapped in $$ ... $$
    text = re.sub(
        r"\$\$\s*\\begin\{aligned\}(.*?)\\end\{aligned\}\s*\$\$",
        lambda m: _handle_aligned_body(m.group(1)),
        text,
        flags=re.DOTALL,
    )
    # Replace bare aligned blocks (without $$ wrappers)
    text = re.sub(
        r"\\begin\{aligned\}(.*?)\\end\{aligned\}",
        lambda m: _handle_aligned_body(m.group(1)),
        text,
        flags=re.DOTALL,
    )
    return text


def _replace_matrices(text: str) -> str:
    """Replace LaTeX matrix environments with AsciiMath equivalents."""
    if not text:
        return text

    def matrix_repl(m: re.Match) -> str:
        mat_type = m.group(1)
        content = m.group(2)
        
        # Split by LaTeX newline \\
        rows_str = [r.strip() for r in content.split(r'\\') if r.strip()]
        out_rows = []
        for row in rows_str:
            cols = [c.strip() for c in row.split('&')]
            out_rows.append("(" + " , ".join(cols) + ")")
        
        inner = " , ".join(out_rows)
        if mat_type == 'vmatrix':
            return f"abs( {inner} )"
        elif mat_type == 'bmatrix':
            return f"[ {inner} ]"
        else:  # pmatrix or matrix
            return f"( {inner} )"

    # Match non-greedily across newlines
    return re.sub(
        r'\\begin\{(vmatrix|pmatrix|bmatrix|matrix)\}(.*?)\\end\{\1\}', 
        matrix_repl, 
        text, 
        flags=re.DOTALL
    )
