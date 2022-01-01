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
)


def test_get_vector_component_map_one_dimensional() -> None:
    dim = 1
    z_symbol = sy.MatrixSymbol("z", dim, 1)
    symbs = [z_symbol]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 1
    assert z_symbol in vector_component_map
    assert len(vector_component_map[z_symbol]) == dim


def test_get_vector_component_map_two_dimensional() -> None:
    dim = 2
    z_symbol = sy.MatrixSymbol("z", dim, 1)
    symbs = [z_symbol]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 1
    assert z_symbol in vector_component_map
    assert len(vector_component_map[z_symbol]) == dim


def test_get_vector_component_map_two_dimensional_two_symbols() -> None:
    dim = 2
    z_symbol = sy.MatrixSymbol("z", dim, 1)
    w_symbol = sy.MatrixSymbol("w", dim, 1)
    symbs = [z_symbol, w_symbol]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 2
    assert z_symbol in vector_component_map
    assert len(vector_component_map[z_symbol]) == dim


def test_get_multivariate_monomials() -> None:
    dim = 2
    degree = 1
    z_symbol = sy.MatrixSymbol("z", dim, 1)
    w_symbol = sy.MatrixSymbol("w", dim, 1)
    symbs = [z_symbol, w_symbol]
    mul_mons = get_multivariate_monomials(symbs, degree)

    z = z_symbol.as_explicit()
    w = w_symbol.as_explicit()
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
