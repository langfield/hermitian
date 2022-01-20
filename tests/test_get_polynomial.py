#!/usr/bin/env python3
import pprint
import sympy as sy
from hermitian.functional import get_polynomial, sprint, katex


def test_get_polynomial() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly = get_polynomial(arity, dim, degree)
    katex(poly)
    assert False
