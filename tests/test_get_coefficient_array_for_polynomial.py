#!/usr/bin/env python3

import sympy as sy
from hermitian.functional import sprint, get_coefficient_array_for_polynomial

def test_get_coefficient_array_for_polynomial() -> None:
    arity = 3
    dim = 2
    degree = 1
    coeffs = get_coefficient_array_for_polynomial(arity, dim, degree)
    print(sy.latex(coeffs))
    print(f"Length: {len(coeffs)}")
