#!/usr/bin/env python3
import os
import sys
import math
import copy
import pprint
import pathlib
import tempfile
import itertools
import functools
import subprocess

import numpy as np
import sympy as sy
from loguru import logger
from beartype import beartype

from hermitian.aliases import List, Tuple, Dict, Set, Any, Callable, Optional

USE_UNICODE = True
REAL_MACRO_NAME = "mathfrak"
COMPLEX_MACRO_NAME = "mathfrak"
LETTERS = {
        f"\\{COMPLEX_MACRO_NAME}{{z}}": ("x", "y"),
        f"\\{COMPLEX_MACRO_NAME}{{w}}": ("r", "s"),
        f"\\{COMPLEX_MACRO_NAME}{{u}}": ("u", "v"),
        f"\\{COMPLEX_MACRO_NAME}{{p}}": ("p", "q"),
        f"\\{COMPLEX_MACRO_NAME}{{m}}": ("m", "n"),
        f"\\{COMPLEX_MACRO_NAME}{{m}}": ("m", "n"),
        f"\\{COMPLEX_MACRO_NAME}{{c}}": ("a", "b"),
        f"\\{COMPLEX_MACRO_NAME}{{j}}": ("j", "k"),
}
COMPONENT_COMPLEX_NUMBER_MAP = {val: key for key, val in LETTERS.items()}


def sprint(obj: sy.Expr) -> None:
    sy.pprint(obj, use_unicode=USE_UNICODE)


@beartype
def get_omega(p: int) -> sy.Expr:
    return sy.exp((2 * sy.pi * sy.I) / p)


@beartype
def get_primitive_pth_roots_of_unity(p: int) -> List[sy.Expr]:
    omegas: List[sy.Expr] = []
    for k in get_coprime_set(p):
        omegas.append(sy.exp((2 * k * sy.pi * sy.I) / p))
    return omegas


# Stolen from: https://stackoverflow.com/a/40190938
@beartype
def get_coprime_set(modulo: int) -> List[int]:
    return [num for num in range(1, modulo) if math.gcd(num, modulo) == 1]


@beartype
def get_type_iii_gamma(
    a: int, b: int, p: int, q: Tuple[int, ...], omega: sy.Expr
) -> List[sy.ImmutableMatrix]:
    """
    Compute the elements of gamma, the matrix subgroup of U(a, b) generated by
    (p, q). See p. 395 in ``Spherical space forms, CR mappings, and proper maps
    between balls`` by D'Angelo and Lichtblau.
    """
    assert a + b == len(q)
    n = a + b

    # Generate rows.
    rows: List[List[int]] = []
    for j in range(n):
        row = [0 for _ in range(n)]
        row[j] = omega ** q[j]
        rows.append(row)

    s = sy.ImmutableMatrix(sy.Matrix(rows))
    assert s.is_square

    elements: List[sy.Matrix] = []
    for j in range(p):
        gamma = s ** j
        elements.append(gamma)
    return elements


@beartype
def is_in_SU_AB(matrix: sy.ImmutableMatrix, a: int, b: int) -> bool:
    """Check if a matrix is in SU(a,b)."""
    if not matrix.is_square:
        return False

    n = sy.shape(matrix)[0]
    if not n == a + b:
        return False

    I_ab = get_I_ab(a, b)
    A_dagger_I_ab_A = sy.physics.quantum.dagger.Dagger(matrix) * I_ab * matrix
    return A_dagger_I_ab_A == I_ab


@beartype
def get_I_ab(a: int, b: int) -> sy.ImmutableMatrix:
    """Compute the generalized identity matrix I_{a,b}."""
    n = a + b
    assert n > 0
    if a == 0:
        return sy.Identity(b).as_explicit()
    if b == 0:
        return sy.Identity(a).as_explicit()
    I_ab = sy.BlockMatrix(
        [[sy.Identity(a), sy.ZeroMatrix(a, b)], [sy.ZeroMatrix(b, a), -sy.Identity(b)]]
    )
    return I_ab.as_explicit()


@beartype
def get_hyperquadric_hermitian_inner_product(
    z: sy.Matrix, w: sy.Matrix, a: int, b: int
) -> sy.Expr:
    r"""Compute \langle z, w \rangle_{a,b}."""
    # Check that z, w are column vectors.
    if not (len(sy.shape(z)) == 2 and len(sy.shape(w)) == 2):
        raise ValueError(
            "Shapes should be length 2: shape(z): "
            f"{sy.shape(z)}| shape(w): {sy.shape(w)}"
        )
    assert sy.shape(z) == sy.shape(w)
    assert sy.shape(z)[1] == 1

    n = sy.shape(z)[0]
    assert n == a + b

    result = sy.Integer(0)
    for j in range(a):
        entries: List[sy.Expr] = (z.row(j) * sy.conjugate(w.row(j))).values()
        assert len(entries) == 1

        summand = entries[0]
        result += summand
    for j in range(a, a + b):
        entries: List[sy.Expr] = (z.row(j) * sy.conjugate(w.row(j))).values()
        assert len(entries) == 1

        summand = entries[0]
        result -= summand

    return result


@beartype
def get_phi_gamma_product(
    z: sy.Matrix, group: List[sy.ImmutableMatrix], a: int, b: int
) -> sy.Expr:
    p = len(group)
    assert p > 0

    e = group[0]
    assert len(sy.shape(e)) == 2
    assert sy.shape(e)[0] == sy.shape(e)[1]

    n = sy.shape(e)[0]
    assert n == a + b

    result = sy.Integer(1)
    for gamma in group:
        result *= 1 - get_hyperquadric_hermitian_inner_product(gamma * z, z, a, b)
    return result


@beartype
def get_phi_gamma_product_polarized(
    z: sy.Matrix, w: sy.Matrix, group: List[sy.ImmutableMatrix], a: int, b: int
) -> sy.Expr:
    # Group should be nonempty.
    p = len(group)
    assert p > 0

    # Check that the first element is a square matrix.
    e = group[0]
    assert len(sy.shape(e)) == 2
    assert sy.shape(e)[0] == sy.shape(e)[1]

    # Check that the group consists of (a + b) x (a + b) matrices.
    n = sy.shape(e)[0]
    assert n == a + b

    # Compute the indexed product.
    result = sy.Integer(1)
    for gamma in group:
        result *= 1 - get_hyperquadric_hermitian_inner_product(gamma * z, w, a, b)
    return result


@beartype
def get_theta_x_from_phi_gamma(
    phi_gamma: sy.Expr, z: sy.Matrix, z_sym: sy.Expr, a: int, b: int
) -> sy.Expr:
    x = sy.symbols(f"x0:{a + b}")
    phi_gamma_x = copy.deepcopy(phi_gamma)
    for j, x_j in enumerate(x):
        assert z_sym in phi_gamma_x.free_symbols
        phi_gamma_x = phi_gamma_x.subs(sy.conjugate(z[j, 0]) * z[j, 0], x_j)

    assert z_sym not in phi_gamma_x.free_symbols
    return phi_gamma_x


@beartype
def get_theta_x(a: int, b: int, p: int, q: Tuple[int, ...]) -> sy.Expr:
    phi_gamma, z, z_sym = get_phi_gamma_z(a, b, p, q)
    return get_theta_x_from_phi_gamma(phi_gamma, z, z_sym, a, b)


@beartype
def get_phi_gamma_z(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[sy.Expr, sy.Matrix, sy.Expr]:
    z_sym = sy.MatrixSymbol("z", a + b, 1)
    z = sy.Matrix(z_sym)

    primitive_roots = get_primitive_pth_roots_of_unity(p)
    assert len(primitive_roots) > 0

    omega = primitive_roots[0]
    group = get_type_iii_gamma(a, b, p, q, omega)
    phi_gamma: sy.Expr = get_phi_gamma_product(z, group, a, b)

    return phi_gamma, z, z_sym


@beartype
def get_phi_gamma_z_w_polarized(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[sy.Expr, sy.Matrix, sy.Matrix, sy.Expr, sy.Expr]:
    """Treat bar{z} as an independent variable bar{w}."""
    z_sym = sy.MatrixSymbol("z", a + b, 1)
    w_sym = sy.MatrixSymbol("w", a + b, 1)
    z = sy.Matrix(z_sym)
    w = sy.Matrix(w_sym)

    primitive_roots = get_primitive_pth_roots_of_unity(p)
    assert len(primitive_roots) > 0

    omega = primitive_roots[0]
    group = get_type_iii_gamma(a, b, p, q, omega)
    phi_gamma: sy.Expr = get_phi_gamma_product_polarized(z, w, group, a, b)

    return sy.simplify(phi_gamma), z, w, z_sym, w_sym


@beartype
def get_phi_gamma_z_w_polarized_no_bar(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[sy.Expr, sy.Matrix, sy.Matrix, sy.Expr, sy.Expr]:
    """Treat bar{z} as an independent variable w."""
    phi_gamma, z, w, z_sym, w_sym = get_phi_gamma_z_w_polarized(a, b, p, q)

    return (
        sy.simplify(phi_gamma.subs(w_sym, sy.conjugate(w_sym))),
        z,
        w,
        z_sym,
        w_sym,
    )


@beartype
def is_hermitian_symmetric_polynomial(
    f: sy.Expr, z: sy.MatrixSymbol, w: sy.MatrixSymbol
) -> bool:
    """
    Check whether a function of two complex vector variables is Hermitian symmetric.
    """
    assert sy.shape(z) == sy.shape(w)
    assert len(sy.shape(z)) == 2
    assert sy.shape(z)[1] == 1

    # Swap (z, w).
    f_w_z_bar = f.subs([(z, w), (w, z)])

    # Complex-conjugate the whole thing.
    f_w_z_bar_conjugate = sy.conjugate(f_w_z_bar)

    # Return truth value of whether the polynomial is Hermitian symmetric.
    return f == f_w_z_bar_conjugate


@beartype
def is_hermitian_symmetric_matrix(A: sy.MatrixExpr) -> bool:
    """
    Check whether a matrix is Hermitian symmetric.
    """
    return A.is_symmetric() and A.is_hermitian


@beartype
def get_vector_component_map(
    symbs: List[sy.MatrixExpr],
) -> Dict[sy.MatrixExpr, List[sy.Symbol]]:
    """Maps vector (sy.Matrix) symbols to lists of their components."""
    assert len(symbs) > 0
    dim = 0
    vector_component_map: Dict[sy.Expr, List[sy.Expr]] = {}
    for symb in symbs:
        components: List[sy.Expr] = []
        m = symb.as_explicit()

        # Make sure dims of all vector arguments are identical.
        dim = len(m) if dim == 0 else dim
        assert dim == len(m)

        for entry in m:
            components.append(entry)
        vector_component_map[symb] = components
    return vector_component_map


@beartype
def get_multivariate_monomials(symbs: List[sy.MatrixExpr], degree: int) -> Set[sy.Expr]:
    assert len(symbs) > 0

    # Map sy.Matrix symbols to lists of components.
    vector_component_map = get_vector_component_map(symbs)
    dim = len(list(vector_component_map.values())[0])

    # Compute all multiindices.
    multiindices = list(itertools.product(range(0, degree + 1), repeat=dim))

    # Map sy.MatrixSymbols to sets of all possible univariate monomials.
    symbol_monomials_map: Dict[sy.Expr, Set[sy.Expr]] = {}
    for symb, components in vector_component_map.items():
        monomials = set()
        for multiindex in multiindices:
            assert len(multiindex) == len(components)
            monomial = sy.Integer(1)
            for index, component in zip(multiindex, components):
                monomial *= component ** index
            monomials.add(monomial)
        symbol_monomials_map[symb] = monomials

    # Get all multivariate monomials.
    multivariate_tuples: List[Tuple[sy.Expr]] = list(
        itertools.product(*symbol_monomials_map.values())
    )

    multivariate_monomials: Set[sy.Expr] = set()
    for multivariate_tuple in multivariate_tuples:
        multivariate_monomial = sy.Integer(1)
        for univariate_monomial in multivariate_tuple:
            multivariate_monomial *= univariate_monomial
            multivariate_monomials.add(multivariate_monomial)

    return multivariate_monomials


@beartype
def get_matrix_of_coefficients(f: sy.Expr) -> sy.MatrixExpr:
    """Get the matrix of coefficients for a polynomial in terms of the given variables."""
    # Get free symbols in the polynomial.
    symbs = f.free_symbols

    # Get all powers of these things.
    max_degree = max(sy.degree_list(f))

    # Get monomials.
    multivariate_monomials = get_multivariate_monomials(symbs, max_degree)

    f = f.as_poly()
    coeffs = f.all_coeffs()
    sprint(coeffs)
    sys.exit()
    f = sy.expand(sy.collect(sy.expand(f), multivariate_monomials))

    logger.info("Collected f:")
    sprint(f)
    for mon in multivariate_monomials:
        coeff = f.coeff(mon)
        logger.info(f"coeff of {mon}: {coeff}")
    raise NotImplementedError


@beartype
def get_multiindices_multivariate(
    arity: int, dim: int, degree: int
) -> Tuple[Tuple[Tuple[int, ...], ...], ...]:
    """Returns ``arity`` tuples of multiindices, one for each variable."""
    multivariate_multiindices: List[Tuple[Tuple[int, ...], ...]] = []
    for _ in range(arity):
        univariate_multiindices = tuple(
            itertools.product(range(0, degree + 1), repeat=dim)
        )
        multivariate_multiindices.append(univariate_multiindices)
    logger.info(f"Length of mults: {len(multivariate_multiindices)}")
    return tuple(multivariate_multiindices)


@beartype
def get_multiindex_combinations(
    arity: int, dim: int, degree: int
) -> Tuple[Tuple[Tuple[int, ...], ...], ...]:
    """
    Returns multiindex combinations, one for each possible monomial.

    The "tensor" returned has shape ``(monoms, arity, dim)``,
    where ``monoms == ((degree + 1) ** (arity)) ** dim``.
    """
    multivariate_multiindices = get_multiindices_multivariate(arity, dim, degree)
    return tuple(itertools.product(*multivariate_multiindices))

@beartype
def get_complex_vector_symbols(arity: int, dim: int) -> Tuple[List[List[sy.Expr]], Dict[sy.Symbol, sy.Expr]]:
    """Get up to 8 vector symbols."""
    # Meta-options: lowercase, uppercase (scalar, vector).
    # Options: math, bf, tt, sf, cal (uppercase-only), frak
    # math : real
    # frak : complex
    # Consider making real variables sf or tt, since then we can use math for other stuff.
    assert arity < len(LETTERS)
    re_tokens = [f"{re}_{{1:{dim + 1}}}" for _, (re, _) in list(LETTERS.items())[:arity]]
    im_tokens = [f"{im}_{{1:{dim + 1}}}" for _, (_, im) in list(LETTERS.items())[:arity]]
    complex_tokens = [f"{complex}_{{1:{dim + 1}}}" for complex in list(LETTERS.keys())[:arity]]
    flat_re_symbols = sy.symbols(" ".join(re_tokens), real=True)
    flat_im_symbols = sy.symbols(" ".join(im_tokens), real=True)
    flat_complex_symbols = sy.symbols(" ".join(complex_tokens))
    flat_symbols = np.array([re + sy.I * im for re, im in zip(flat_re_symbols, flat_im_symbols)])
    complex_map = {expansion: z for z, expansion in zip(flat_complex_symbols, flat_symbols)}
    return flat_symbols.reshape(arity, dim).tolist(), complex_map


@beartype
def get_monomials(arity: int, dim: int, degree: int) -> Tuple[Dict[tuple, sy.Expr], Dict[sy.Symbol, sy.Expr]]:
    """Generate a tuple of monomials for an arbitrary polynomial."""
    multiindex_combinations = get_multiindex_combinations(arity, dim, degree)
    symbols, complex_map = get_complex_vector_symbols(arity, dim)
    monomials = {}
    for monom_multiindices in multiindex_combinations:
        assert len(monom_multiindices) == len(symbols)
        monomial = sy.Integer(1)
        for j, multiindex in enumerate(monom_multiindices):
            vector = symbols[j]
            univariate_monomial = sy.Integer(1)
            for k, index in enumerate(multiindex):
                univariate_monomial *= vector[k] ** index
            monomial *= univariate_monomial
        monomials[monom_multiindices] = monomial
    return monomials, complex_map


@beartype
def get_coefficient_array_for_polynomial(
    arity: int, dim: int, degree: int
) -> Dict[Tuple[Tuple[int, ...], ...], sy.Symbol]:
    """ Complex-valued by default. """
    multiindex_combinations = get_multiindex_combinations(arity, dim, degree)
    coeffs = {}
    for monom_multiindices in multiindex_combinations:
        symbol_subscript_constructor = r"{"
        multiindex_constructors = []
        for multiindex in monom_multiindices:
            escaped_multiindex = str(multiindex).replace(", ", r"\,")
            multiindex_constructors.append(rf"{escaped_multiindex}")
        symbol_subscript_constructor += r"\,".join(multiindex_constructors) + "}"
        re_symbol_constructor = f"a_{symbol_subscript_constructor}"
        im_symbol_constructor = f"b_{symbol_subscript_constructor}"
        re_symbol = sy.symbols(re_symbol_constructor, real=True)
        im_symbol = sy.symbols(im_symbol_constructor, real=True)
        symbol = re_symbol + sy.I * im_symbol
        coeffs[monom_multiindices] = symbol

    return coeffs


@beartype
def get_polynomial_in_terms_of_re_im_components(arity: int, dim: int, degree: int) -> Tuple[sy.Expr, Dict[sy.Symbol, sy.Expr]]:
    coeffs = get_coefficient_array_for_polynomial(arity, dim, degree)
    monoms, complex_map = get_monomials(arity, dim, degree)
    assert len(coeffs) == len(monoms)
    poly = sy.Integer(1)
    for monom_multiindices, monomial in monoms.items():
        assert monom_multiindices in coeffs
        coeff = coeffs[monom_multiindices]
        term = monomial * coeff
        poly += term
    return poly, complex_map

@beartype
def get_complex_polynomial(arity: int, dim: int, degree: int) -> sy.Expr:
    poly, complex_map = get_polynomial_in_terms_of_re_im_components(arity, dim, degree)
    complex_symbol_substitution_list = [(key, val) for key, val in complex_map.items()]
    logger.info(complex_symbol_substitution_list)
    complex_poly = poly.subs(complex_symbol_substitution_list)
    return complex_poly


@beartype
def get_polynomial_in_z_z_bar(z_sym: sy.MatrixExpr, degree: int) -> sy.Expr:
    z_bar_sym = sy.conjugate(z_sym)
    symbs = [z_sym, z_bar_sym]

    vector_component_map = get_vector_component_map(symbs)
    mons = get_multivariate_monomials(symbs, degree)
    poly = functools.reduce(lambda x, y: x + y, mons)
    return poly


@beartype
def run_experiment_with_fuzzed_parameters_a_b_p_q(
    experiment: Callable[[int, int, int, Tuple[int, ...]], None],
    max_n: int,
    max_p: int,
    min_a: int = 0,
    min_b: int = 0,
) -> None:
    """Run an experiment for many values of a,b,p,q."""
    assert max_n - 1 <= max_p

    for n in range(1, max_n + 1):
        for a in range(min_a, n + 1 - min_b):
            b = n - a
            for p in range(n + 1, max_p + 1):
                assert n <= p - 1
                for q in itertools.combinations(range(1, p), n):
                    experiment(a, b, p, q)

@beartype
def katex(s: sy.Expr) -> None:
    docname = "expression"
    tmpdir = tempfile.mkdtemp()
    tempfile_path = os.path.join(tmpdir, f"{docname}.txt")
    latex_pkgs = ["breqn", "amsmath", "amsthm", "amssymb"]
    with open(tempfile_path, "w") as tmp:
        pkgs = "\n" + "\n".join([f"\\usepackage{{{pkg}}}" for pkg in latex_pkgs]) + "\n"
        header = "\\documentclass{article}[12pt]\n\\usepackage[margin=0.25in]{geometry}" + pkgs + "\\begin{document}\n\\begin{dmath}\n"
        footer = "\n\\end{dmath}\n\\end{document}\n"
        tmp.write(header + sy.latex(s) + footer)
    repo = pathlib.Path(__file__).parent.parent.resolve()
    outdir = os.path.join(repo, "out")
    out = os.path.join(repo, "out.html")
    logger.info(f"tmp.name: {tempfile_path}")
    with open(tempfile_path) as fin:
        s = fin.read()
        print(s)
    p = subprocess.run(["npx", "katex", "-d", "-i", f"{tempfile_path}", "-o", f"{out}"], capture_output=True)
    args = ["cp", f"{tempfile_path}", f"{outdir}", "&&", "cd", f"{outdir}", "&&", "pdflatex", f"{docname}.txt"]
    logger.info(f"Cmd: {' '.join(args)}")
    p = subprocess.run(["cp", f"{tempfile_path}", f"{outdir}/"], capture_output=True)
    logger.info(f"katex stdout: {p.stdout}")
    logger.info(f"katex stderr {p.stderr}")
    # p = subprocess.run(["cd", f"{outdir}"], capture_output=True)
    logger.info(f"katex stdout: {p.stdout}")
    logger.info(f"katex stderr {p.stderr}")
    p = subprocess.run(["pdflatex", "--output-directory", f"{outdir}", f"{docname}.txt"], capture_output=True)
    logger.info(f"katex stdout: {p.stdout}")
    logger.info(f"katex stderr {p.stderr}")
    pdf_path = os.path.join(outdir, f"{docname}.pdf")
    # p = subprocess.run(["xdg-open", f"{pdf_path}"], capture_output=True)
