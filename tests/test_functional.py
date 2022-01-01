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

from hermitian.aliases import List, Tuple, Dict, Any, Callable, Optional
from hermitian.functional import (
    get_vector_component_map,
    get_multivariate_monomials,
    sprint,
    get_polynomial_in_z_z_bar,
    get_multiindices_multivariate,
)


def test_get_vector_component_map_one_dimensional() -> None:
    dim = 1
    z_sym = sy.MatrixSymbol("z", dim, 1)
    symbs = [z_sym]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 1
    assert z_sym in vector_component_map
    assert len(vector_component_map[z_sym]) == dim


def test_get_vector_component_map_two_dimensional() -> None:
    dim = 2
    z_sym = sy.MatrixSymbol("z", dim, 1)
    symbs = [z_sym]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 1
    assert z_sym in vector_component_map
    assert len(vector_component_map[z_sym]) == dim


def test_get_vector_component_map_two_dimensional_bivariate() -> None:
    dim = 2
    z_sym = sy.MatrixSymbol("z", dim, 1)
    w_sym = sy.MatrixSymbol("w", dim, 1)
    symbs = [z_sym, w_sym]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 2
    assert z_sym in vector_component_map
    assert len(vector_component_map[z_sym]) == dim


def test_get_multivariate_monomials_two_dimensional_bivariate_degree_one() -> None:
    dim = 2
    degree = 1
    z_sym = sy.MatrixSymbol("z", dim, 1)
    w_sym = sy.MatrixSymbol("w", dim, 1)
    symbs = [z_sym, w_sym]
    mul_mons = get_multivariate_monomials(symbs, degree)

    z = z_sym.as_explicit()
    w = w_sym.as_explicit()
    actual_mons = {
        1,
        w[0, 0],
        w[1, 0],
        z[0, 0],
        z[1, 0],
        w[0, 0] * w[1, 0],
        w[0, 0] * z[0, 0],
        w[0, 0] * z[1, 0],
        w[1, 0] * z[0, 0],
        w[1, 0] * z[1, 0],
        z[0, 0] * z[1, 0],
        w[0, 0] * w[1, 0] * z[0, 0],
        w[0, 0] * w[1, 0] * z[1, 0],
        w[0, 0] * z[0, 0] * z[1, 0],
        w[1, 0] * z[0, 0] * z[1, 0],
        w[0, 0] * w[1, 0] * z[0, 0] * z[1, 0],
    }
    assert mul_mons == actual_mons


def test_get_polynomial_in_z_z_bar_one_dimensional_degree_one() -> None:
    dim = 1
    degree = 1
    z_sym = sy.MatrixSymbol("z", dim, 1)
    poly = get_polynomial_in_z_z_bar(z_sym, degree)
    z = z_sym.as_explicit()
    actual_poly = sy.conjugate(z[0, 0]) * z[0, 0] + sy.conjugate(z[0, 0]) + z[0, 0] + 1
    assert poly == actual_poly


def test_get_polynomial_in_z_z_bar_one_dimensional_degree_two() -> None:
    dim = 1
    degree = 2
    z_sym = sy.MatrixSymbol("z", dim, 1)
    poly = get_polynomial_in_z_z_bar(z_sym, degree)
    z = z_sym.as_explicit()
    actual_poly = sy.conjugate(z[0, 0]) * z[0, 0] + sy.conjugate(z[0, 0]) + z[0, 0] + 1
    sprint(poly)
    assert poly == actual_poly
