#!/usr/bin/env python3
import pprint
import sympy as sy
from loguru import logger
from hermitian.functional import get_polynomial_in_terms_of_re_im_components, sprint, katex, polarize, is_hermitian_form



def test_get_complex_polynomial_in_terms_of_re_im_components() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly, _ = get_polynomial_in_terms_of_re_im_components(arity, dim, degree)
    re, im = poly.as_real_imag()
    # result = sy.solve([sy.im(poly)])
    # logger.info(f"Result: {result}")
    # katex(result)
    assert False


def test_polarize() -> None:
    arity = 2
    dim = 2
    degree = 1
    poly, symbol_map = get_polynomial_in_terms_of_re_im_components(arity, dim, degree)
    polarized_poly = polarize(poly, symbol_map)
    katex([poly, polarized_poly])
    # result = sy.solve([sy.im(polarized_poly)])
    # assert len(polarized_poly.free_symbols) == dim
    assert False


def test_polarize_one_dimensional() -> None:
    arity = 2
    dim = 1
    degree = 1
    poly, symbol_map = get_polynomial_in_terms_of_re_im_components(arity, dim, degree)
    polarized_poly = polarize(poly, symbol_map)
    im = sy.im(polarized_poly)
    result: List[Dict[sy.Expr, sy.Expr]] = sy.solve([sy.im(polarized_poly)], dict=True)
    for sol in result:
        real_polarized_poly = polarized_poly.subs(list(sol.items()))
        simple_real_polarized_poly = sy.simplify(real_polarized_poly)
        logger.info(f"Symbol map keys: {list(symbol_map.keys())}")
        # is_hermitian_form(simple_real_polarized_poly, symbol_map)
        is_hermitian_form(real_polarized_poly, symbol_map)
        katex([poly, polarized_poly, im, result, real_polarized_poly, simple_real_polarized_poly])
        # assert len(polarized_poly.free_symbols) == dim
    assert False
