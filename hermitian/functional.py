#!/usr/bin/env python3
import math
import copy
import pprint
import itertools
from functools import wraps

from loguru import logger
from beartype import beartype

import sympy
from sympy import (
    latex,
    expand,
    conjugate,
    prime,
    simplify,
    init_printing,
    abc,
    symbols,
    shape,
    eye,
    pi,
    I,
    Expr,
    Integer,
    Number,
    FiniteSet,
    Symbol,
)
from sympy.matrices import (
    Matrix,
    ImmutableMatrix,
    BlockMatrix,
    ZeroMatrix,
    Identity,
    MatrixSymbol,
    MatrixExpr,
)
from sympy.functions import exp
from sympy.physics.quantum.dagger import Dagger
from sympy.printing.pretty.pretty import pprint as spprint

from hermitian.aliases import List, Tuple, Dict, Any, Callable, Optional

USE_UNICODE = True


def sprint(obj: Expr) -> None:
    spprint(obj, use_unicode=USE_UNICODE)


@beartype
def get_omega(p: int) -> Expr:
    return exp((2 * pi * I) / p)


@beartype
def get_primitive_pth_roots_of_unity(p: int) -> List[Expr]:
    omegas: List[Expr] = []
    for k in get_coprime_set(p):
        omegas.append(exp((2 * k * pi * I) / p))
    return omegas


# Stolen from: https://stackoverflow.com/a/40190938
@beartype
def get_coprime_set(modulo: int) -> List[int]:
    return [num for num in range(1, modulo) if math.gcd(num, modulo) == 1]


@beartype
def get_type_iii_gamma(
    a: int, b: int, p: int, q: Tuple[int, ...], omega: Expr
) -> List[ImmutableMatrix]:
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

    s = ImmutableMatrix(Matrix(rows))
    assert s.is_square

    elements: List[Matrix] = []
    for j in range(p):
        gamma = s ** j
        elements.append(gamma)
    return elements


@beartype
def is_in_SU_AB(matrix: ImmutableMatrix, a: int, b: int) -> bool:
    """Check if a matrix is in SU(a,b)."""
    if not matrix.is_square:
        return False

    n = shape(matrix)[0]
    if not n == a + b:
        return False

    I_ab = get_I_ab(a, b)
    A_dagger_I_ab_A = Dagger(matrix) * I_ab * matrix
    return A_dagger_I_ab_A == I_ab


@beartype
def get_I_ab(a: int, b: int) -> ImmutableMatrix:
    """Compute the generalized identity matrix I_{a,b}."""
    n = a + b
    assert n > 0
    if a == 0:
        return Identity(b).as_explicit()
    if b == 0:
        return Identity(a).as_explicit()
    I_ab = BlockMatrix(
        [[Identity(a), ZeroMatrix(a, b)], [ZeroMatrix(b, a), -Identity(b)]]
    )
    return I_ab.as_explicit()


@beartype
def get_hyperquadric_hermitian_inner_product(
    z: Matrix, w: Matrix, a: int, b: int
) -> Expr:
    r"""Compute \langle z, w \rangle_{a,b}."""
    # Check that z, w are column vectors.
    if not (len(shape(z)) == 2 and len(shape(w)) == 2):
        raise ValueError(
            f"Shapes should be length 2: shape(z): {shape(z)}| shape(w): {shape(w)}"
        )
    assert shape(z) == shape(w)
    assert shape(z)[1] == 1

    n = shape(z)[0]
    assert n == a + b

    # DEBUG
    z = Matrix(z)
    w = Matrix(w)

    result = Integer(0)
    for j in range(a):
        entries: List[Expr] = (z.row(j) * conjugate(w.row(j))).values()
        assert len(entries) == 1

        summand = entries[0]
        result += summand
    for j in range(a, a + b):
        entries: List[Expr] = (z.row(j) * conjugate(w.row(j))).values()
        assert len(entries) == 1

        summand = entries[0]
        result -= summand

    return result


@beartype
def get_phi_gamma_product(
    z: Matrix, group: List[ImmutableMatrix], a: int, b: int
) -> Expr:
    p = len(group)
    assert p > 0

    e = group[0]
    assert len(shape(e)) == 2
    assert shape(e)[0] == shape(e)[1]

    n = shape(e)[0]
    assert n == a + b

    result = Integer(1)
    for gamma in group:
        result *= 1 - get_hyperquadric_hermitian_inner_product(gamma * z, z, a, b)
    return result


@beartype
def get_phi_gamma_product_polarized(
    z: Matrix, w: Matrix, group: List[ImmutableMatrix], a: int, b: int
) -> Expr:
    p = len(group)
    assert p > 0

    e = group[0]
    assert len(shape(e)) == 2
    assert shape(e)[0] == shape(e)[1]

    n = shape(e)[0]
    assert n == a + b

    result = Integer(1)
    for gamma in group:
        result *= 1 - get_hyperquadric_hermitian_inner_product(gamma * z, w, a, b)
    return result


@beartype
def get_theta_x_from_phi_gamma(
    phi_gamma: Expr, z: Matrix, z_symbol: Expr, a: int, b: int
) -> Expr:
    x = symbols(f"x0:{a + b}")
    phi_gamma_x = copy.deepcopy(phi_gamma)
    for j, x_j in enumerate(x):
        assert z_symbol in phi_gamma_x.free_symbols
        phi_gamma_x = phi_gamma_x.subs(conjugate(z[j, 0]) * z[j, 0], x_j)

    assert z_symbol not in phi_gamma_x.free_symbols
    return phi_gamma_x


@beartype
def get_theta_x(a: int, b: int, p: int, q: Tuple[int, ...]) -> Expr:
    phi_gamma, z, z_symbol = get_phi_gamma_z(a, b, p, q)
    return get_theta_x_from_phi_gamma(phi_gamma, z, z_symbol, a, b)


@beartype
def get_phi_gamma_z(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[Expr, Matrix, Expr]:
    z_symbol = MatrixSymbol("z", a + b, 1)
    z = Matrix(z_symbol)

    primitive_roots = get_primitive_pth_roots_of_unity(p)
    assert len(primitive_roots) > 0

    omega = primitive_roots[0]
    group = get_type_iii_gamma(a, b, p, q, omega)
    phi_gamma: Expr = get_phi_gamma_product(z, group, a, b)

    return phi_gamma, z, z_symbol


@beartype
def get_phi_gamma_z_w_polarized(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> Tuple[Expr, Matrix, Matrix, Expr, Expr]:
    z_symbol = MatrixSymbol("z", a + b, 1)
    w_symbol = MatrixSymbol("w", a + b, 1)
    z = Matrix(z_symbol)
    w = Matrix(w_symbol)

    primitive_roots = get_primitive_pth_roots_of_unity(p)
    assert len(primitive_roots) > 0

    omega = primitive_roots[0]
    group = get_type_iii_gamma(a, b, p, q, omega)
    phi_gamma: Expr = get_phi_gamma_product_polarized(z, w, group, a, b)

    return phi_gamma, z, w, z_symbol, w_symbol


@beartype
def is_hermitian_symmetric(f: Expr, z: MatrixSymbol, w: MatrixSymbol) -> bool:
    """
    Check whether a function of two complex vector variables is Hermitian symmetric.
    """
    assert shape(z) == shape(w)
    assert len(shape(z)) == 2
    assert shape(z)[1] == 1
    n = shape(z)[0]

    # Instantiate a dummy variable for the swap.
    w_prime = MatrixSymbol("w'", n, 1)

    # Swap (z, w).
    f_w_z_bar = f.subs(z, w_prime)
    f_w_z_bar = f_w_z_bar.subs(w, z)
    f_w_z_bar = f_w_z_bar.subs(w_prime, w)

    # Complex-conjugate the whole thing.
    f_w_z_bar_conjugate = conjugate(f_w_z_bar)

    # Return truth value of whether the polynomial is Hermitian symmetric.
    return f == f_w_z_bar_conjugate


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