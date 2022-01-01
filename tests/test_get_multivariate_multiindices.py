from loguru import logger
from hermitian.aliases import List, Tuple, Dict, Any, Callable, Optional
from hermitian.functional import (
    get_multiindices_multivariate,
)


def test_get_multiindices_multivariate_univariate_one_dimensional_degree_zero() -> None:
    """
    We have a single, scalar variable x, and we want degree up to 0.
    So we should only have x^0.
    """
    arity = 1
    dim = 1
    degree = 0
    mults: Tuple[Tuple[int]] = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == {((0,),)}


def test_get_multiindices_multivariate_univariate_one_dimensional_degree_one() -> None:
    """
    We have a single, scalar variable x, and we want degree up to 1.
    So we should only have x^0, x^1.
    """
    arity = 1
    dim = 1
    degree = 1
    mults: Tuple[Tuple[int]] = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == {((0,), (1,))}


def test_get_multiindices_multivariate_univariate_one_dimensional_degree_two() -> None:
    """
    We have a single, scalar variable x, and we want degree up to 0. So we
    should only have x^0, x^1, x_2.
    """
    arity = 1
    dim = 1
    degree = 2
    mults: Tuple[Tuple[int]] = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == {((0,), (1,), (2,))}


def test_get_multiindices_multivariate_univariate_two_dimensional_degree_zero() -> None:
    """
    We have a single 2-dimensional vector variable x = (x_1, x_2), and we want
    degree up to 0.  So we should only have x_1^0, x_2^0.
    """
    arity = 1
    dim = 2
    degree = 0
