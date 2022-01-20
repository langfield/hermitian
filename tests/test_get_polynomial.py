#!/usr/bin/env python3
import pprint
import sympy as sy
from hermitian.functional import get_complex_polynomial, sprint, katex


def test_get_complex_polynomial() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly = get_complex_polynomial(arity, dim, degree)
    katex(poly)
    assert False
