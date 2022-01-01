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
from hermitian.functional import get_vector_component_map


def test_get_vector_component_map_one_dimensional() -> None:
    n = 1
    z_symbol = sy.MatrixSymbol("z", n, 1)
    symbs = [z_symbol]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 1
    assert z_symbol in vector_component_map
    assert len(vector_component_map[z_symbol]) == n


def test_get_vector_component_map_two_dimensional() -> None:
    n = 2
    z_symbol = sy.MatrixSymbol("z", n, 1)
    symbs = [z_symbol]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 1
    assert z_symbol in vector_component_map
    assert len(vector_component_map[z_symbol]) == n


def test_get_vector_component_map_two_dimensional_two_symbols() -> None:
    n = 2
    z_symbol = sy.MatrixSymbol("z", n, 1)
    w_symbol = sy.MatrixSymbol("w", n, 1)
    symbs = [z_symbol, w_symbol]
    vector_component_map = get_vector_component_map(symbs)
    assert len(vector_component_map) == 2
    assert z_symbol in vector_component_map
    assert len(vector_component_map[z_symbol]) == n
