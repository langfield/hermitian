#!/usr/bin/env python3
import pprint
import sympy as sy
from loguru import logger
from hermitian.functional import get_complex_polynomial, get_polynomial_in_terms_of_re_im_components, sprint, katex, polarize


def test_get_complex_polynomial() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly = get_complex_polynomial(arity, dim, degree)
    re, im = poly.as_real_imag()
    # katex(re)
    assert False


def test_get_complex_polynomial_in_terms_of_re_im_components() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly, _, _ = get_polynomial_in_terms_of_re_im_components(arity, dim, degree)
    re, im = poly.as_real_imag()
    result = sy.solve([sy.im(poly)])
    logger.info(f"Result: {result}")
    katex(result)
    assert False


def test_polarize() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly, _, im_symbs = get_polynomial_in_terms_of_re_im_components(arity, dim, degree)
    polarized_poly = polarize(poly, im_symbs)
    katex(polarized_poly)
    assert len(polarized_poly.free_symbols) == dim
