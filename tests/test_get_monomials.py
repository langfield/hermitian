#!/usr/bin/env python3
import pprint
import sympy as sy
from hermitian.functional import get_monomials, sprint

def test_get_monomials() -> None:
    arity = 2
    dim = 2
    degree = 2
    monoms = get_monomials(arity, dim, degree)
    assert len(monoms) == ((degree + 1) ** arity) ** dim
    sprint(monoms)
    pprint.pprint(monoms)
