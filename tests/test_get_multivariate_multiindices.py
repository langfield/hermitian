import itertools
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
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0,),),)


def test_get_multiindices_multivariate_univariate_one_dimensional_degree_one() -> None:
    """
    We have a single, scalar variable x, and we want degree up to 1.
    So we should only have x^0, x^1.
    """
    arity = 1
    dim = 1
    degree = 1
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0,), (1,)),)


def test_get_multiindices_multivariate_univariate_one_dimensional_degree_two() -> None:
    """
    We have a single, scalar variable x, and we want degree up to 0. So we
    should only have x^0, x^1, x_2.
    """
    arity = 1
    dim = 1
    degree = 2
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0,), (1,), (2,)),)


def test_get_multiindices_multivariate_univariate_two_dimensional_degree_zero() -> None:
    """
    We have a single 2-dimensional vector variable x = (x_1, x_2), and we want
    degree up to 0.  So we should only have x_1^0, x_2^0.
    """
    arity = 1
    dim = 2
    degree = 0
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0, 0),),)


def test_get_multiindices_multivariate_univariate_two_dimensional_degree_zero() -> None:
    """
    We have a single 3-dimensional vector variable x = (x_1, x_2, x_3), and we want
    degree up to 0.  So we should only have x_1^0, x_2^0, x_3^0.
    """
    arity = 1
    dim = 3
    degree = 0
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0, 0, 0),),)


def test_get_multiindices_multivariate_bivariate_one_dimensional_degree_zero() -> None:
    """
    We have two scalar variables x, y, and we want degree up to 0.
    So we should only have x^0, y^0.
    """
    arity = 2
    dim = 1
    degree = 0
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0,),), ((0,),))


def test_get_multiindices_multivariate_trivariate_one_dimensional_degree_zero() -> None:
    """
    We have three scalar variables x, y, z, and we want degree up to 0.
    So we should only have x^0, y^0, z^0.
    """
    arity = 3
    dim = 1
    degree = 0
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0,),), ((0,),), ((0,),))


def test_get_multiindices_multivariate_univariate_two_dimensional_degree_one() -> None:
    """
    We have one 2-dimensional variable x = (x_1, x_2), and we want degree up to 1.
    So we should only have x_1^0 x_2^0, x_1^0 x_2^1, x_1^1 x_2^0, x_1^1 x_2^1.
    """
    arity = 1
    dim = 2
    degree = 1
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0, 0), (0, 1), (1, 0), (1, 1)),)


def test_get_multiindices_multivariate_univariate_two_dimensional_degree_two() -> None:
    """
    We have one 2-dimensional variable x = (x_1, x_2), and we want degree up to 2.
    So we should only have
        x_1^0 x_2^0,
        x_1^0 x_2^1,
        x_1^0 x_2^2,
        x_1^1 x_2^0,
        x_1^1 x_2^1,
        x_1^1 x_2^2,
        x_1^2 x_2^0,
        x_1^2 x_2^1,
        x_1^2 x_2^2,
    """
    arity = 1
    dim = 2
    degree = 2
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (
        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
    )


def test_get_multiindices_multivariate_bivariate_two_dimensional_degree_one() -> None:
    """
    We have two 2-dimensional variables x = (x_1, x_2), y = (y_1, y_2), and we
    want degree up to 1.  So we should only have
        x_1^0 x_2^0,
        x_1^0 x_2^1,
        x_1^1 x_2^0,
        x_1^1 x_2^1,
        y_1^0 y_2^0,
        y_1^0 y_2^1,
        y_1^1 y_2^0,
        y_1^1 y_2^1,

        All possible monomials:
        x_1^0 x_2^0 y_1^0 y_2^0,
        x_1^0 x_2^1 y_1^0 y_2^0,
        x_1^1 x_2^0 y_1^0 y_2^0,
        x_1^1 x_2^1 y_1^0 y_2^0,
        x_1^0 x_2^0 y_1^1 y_2^0,
        x_1^0 x_2^1 y_1^1 y_2^0,
        x_1^1 x_2^0 y_1^1 y_2^0,
        x_1^1 x_2^1 y_1^1 y_2^0,
        x_1^0 x_2^0 y_1^1 y_2^1,
        x_1^0 x_2^1 y_1^1 y_2^1,
        x_1^1 x_2^0 y_1^1 y_2^1,
        x_1^1 x_2^1 y_1^1 y_2^1,
        x_1^0 x_2^0 y_1^0 y_2^1,
        x_1^0 x_2^1 y_1^0 y_2^1,
        x_1^1 x_2^0 y_1^0 y_2^1,
        x_1^1 x_2^1 y_1^0 y_2^1,
    """
    arity = 2
    dim = 2
    degree = 1
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (((0, 0), (0, 1), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 0), (1, 1)))


def test_get_multiindices_multivariate_trivariate_two_dimensional_degree_one() -> None:
    """
    We have three 2-dimensional variables
        x = (x_1, x_2),
        y = (y_1, y_2),
        z = (z_1, z_2),
    and we want degree up to 1.  So we should only have
        x_1^0 x_2^0,
        x_1^0 x_2^1,
        x_1^1 x_2^0,
        x_1^1 x_2^1,
        y_1^0 y_2^0,
        y_1^0 y_2^1,
        y_1^1 y_2^0,
        y_1^1 y_2^1,
        z_1^0 z_2^0,
        z_1^0 z_2^1,
        z_1^1 z_2^0,
        z_1^1 z_2^1,
    """
    arity = 3
    dim = 2
    degree = 1
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (
        ((0, 0), (0, 1), (1, 0), (1, 1)),
        ((0, 0), (0, 1), (1, 0), (1, 1)),
        ((0, 0), (0, 1), (1, 0), (1, 1)),
    )


def test_get_multiindices_multivariate_bivariate_two_dimensional_degree_two() -> None:
    """
    We have two 2-dimensional variables x = (x_1, x_2), y = (y_1, y_2), and we
    want degree up to 1.  So we should only have

        x_1^0 x_2^0,
        x_1^0 x_2^1,
        x_1^0 x_2^2,
        x_1^1 x_2^0,
        x_1^1 x_2^1,
        x_1^1 x_2^2,
        x_1^2 x_2^0,
        x_1^2 x_2^1,
        x_1^2 x_2^2,

        y_1^0 y_2^0,
        y_1^0 y_2^1,
        y_1^0 y_2^2,
        y_1^1 y_2^0,
        y_1^1 y_2^1,
        y_1^1 y_2^2,
        y_1^2 y_2^0,
        y_1^2 y_2^1,
        y_1^2 y_2^2,
    """
    arity = 2
    dim = 2
    degree = 2
    mults = get_multiindices_multivariate(arity, dim, degree)
    logger.info(f"Multiindices: {mults}")
    assert len(mults) == arity
    assert mults == (
        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
    )
