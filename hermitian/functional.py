#!/usr/bin/env python3
import sys
import math
import copy
import pprint
import itertools
from functools import wraps

from loguru import logger
from beartype import beartype

import sympy as sy

from hermitian.aliases import List, Tuple, Dict, Set, Any, Callable, Optional

USE_UNICODE = True


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
    phi_gamma: sy.Expr, z: sy.Matrix, z_symbol: sy.Expr, a: int, b: int
) -> sy.Expr:
    x = sy.symbols(f"x0:{a + b}")
    phi_gamma_x = copy.deepcopy(phi_gamma)
    for j, x_j in enumerate(x):
        assert z_symbol in phi_gamma_x.free_symbols
        phi_gamma_x = phi_gamma_x.subs(sy.conjugate(z[j, 0]) * z[j, 0], x_j)

    assert z_symbol not in phi_gamma_x.free_symbols
    return phi_gamma_x


@beartype
def get_theta_x(a: int, b: int, p: int, q: Tuple[int, ...]) -> sy.Expr:
    phi_gamma, z, z_symbol = get_phi_gamma_z(a, b, p, q)
    return get_theta_x_from_phi_gamma(phi_gamma, z, z_symbol, a, b)


@beartype
def get_phi_gamma_z(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[sy.Expr, sy.Matrix, sy.Expr]:
    z_symbol = sy.MatrixSymbol("z", a + b, 1)
    z = sy.Matrix(z_symbol)

    primitive_roots = get_primitive_pth_roots_of_unity(p)
    assert len(primitive_roots) > 0

    omega = primitive_roots[0]
    group = get_type_iii_gamma(a, b, p, q, omega)
    phi_gamma: sy.Expr = get_phi_gamma_product(z, group, a, b)

    return phi_gamma, z, z_symbol


@beartype
def get_phi_gamma_z_w_polarized(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[sy.Expr, sy.Matrix, sy.Matrix, sy.Expr, sy.Expr]:
    """Treat bar{z} as an independent variable bar{w}."""
    z_symbol = sy.MatrixSymbol("z", a + b, 1)
    w_symbol = sy.MatrixSymbol("w", a + b, 1)
    z = sy.Matrix(z_symbol)
    w = sy.Matrix(w_symbol)

    primitive_roots = get_primitive_pth_roots_of_unity(p)
    assert len(primitive_roots) > 0

    omega = primitive_roots[0]
    group = get_type_iii_gamma(a, b, p, q, omega)
    phi_gamma: sy.Expr = get_phi_gamma_product_polarized(z, w, group, a, b)

    return sy.simplify(phi_gamma), z, w, z_symbol, w_symbol


@beartype
def get_phi_gamma_z_w_polarized_no_bar(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[sy.Expr, sy.Matrix, sy.Matrix, sy.Expr, sy.Expr]:
    """Treat bar{z} as an independent variable w."""
    phi_gamma, z, w, z_symbol, w_symbol = get_phi_gamma_z_w_polarized(a, b, p, q)

    return (
        sy.simplify(phi_gamma.subs(w_symbol, sy.conjugate(w_symbol))),
        z,
        w,
        z_symbol,
        w_symbol,
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
def get_vector_component_map(symbs: List[sy.MatrixSymbol]) -> Dict[sy.MatrixSymbol, List[sy.Symbol]]:
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
def get_multivariate_monomials(symbs: List[sy.MatrixSymbol], degree: int) -> Set[sy.Expr]:
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
        sys.exit()


@beartype
def get_polynomial_in_z_z_bar(n: int, degree: int) -> sy.Expr:
    z_symbol = sy.MatrixSymbol("z", n, 1)
    z = sy.Matrix(z_symbol)
    symbs = [z_symbol, sy.conjugate(z_symbol)]

    vector_component_map = get_vector_component_map(symbs)
    n = len(list(vector_component_map.values())[0])

    multiindices = list(itertools.product(range(0, degree + 1), repeat=n))
    for multiindex in multiindices:
        assert len(multiindex) == len(z)
        for index, component in zip(multiindex, z):
            pass


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
