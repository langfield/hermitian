import itertools
import numpy as np
from loguru import logger
from hermitian.aliases import List, Tuple, Dict, Any, Callable, Optional
from hermitian.functional import (
    get_multiindex_combinations,
)


def test_get_multiindex_combinations_univariate_one_dimensional_degree_zero() -> None:
    """We have one 1-dimensional variable up to degree 0."""
    arity = 1
    dim = 1
    degree = 0
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    assert multiindex_combs == (((0,),),)


def test_get_multiindex_combinations_univariate_one_dimensional_degree_one() -> None:
    """
    We have one 1-dimensional variable up to degree 1.

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. ???
        3. dim
    """
    arity = 1
    dim = 1
    degree = 1
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert multiindex_combs == (((0,),), ((1,),))


def test_get_multiindex_combinations_univariate_one_dimensional_degree_two() -> None:
    """
    We have one 1-dimensional variable up to degree 2.

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. ???
        3. dim
    """
    arity = 1
    dim = 1
    degree = 2
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert multiindex_combs == (((0,),), ((1,),), ((2,),))


def test_get_multiindex_combinations_univariate_two_dimensional_degree_zero() -> None:
    """
    We have one 2-dimensional variable up to degree 0.

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. ???
        3. dim
    """
    arity = 1
    dim = 2
    degree = 0
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert multiindex_combs == (((0, 0),),)


def test_get_multiindex_combinations_bivariate_one_dimensional_degree_zero() -> None:
    """
    We have two 1-dimensional variables up to degree 0.

    So the only monomial is:
        x^0 y^0 == 1

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. ???
        3. dim
    """
    arity = 2
    dim = 1
    degree = 0
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert multiindex_combs == (((0,), (0,)),)


def test_get_multiindex_combinations_trivariate_one_dimensional_degree_zero() -> None:
    """
    We have three 1-dimensional variables up to degree 0.

    So the only monomial is:
        x^0 y^0 z^0 == 1

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. arity??
        3. dim
    """
    arity = 3
    dim = 1
    degree = 0
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert multiindex_combs == (((0,), (0,), (0,)),)


def test_get_multiindex_combinations_bivariate_one_dimensional_degree_one() -> None:
    """
    We have two 1-dimensional variables up to degree 1.

    So the only monomials are:
        x^0 y^0 == 1
        x^0 y^1
        x^1 y^0
        x^1 y^1

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. arity??
        3. dim
    """
    arity = 2
    dim = 1
    degree = 1
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert len(tensor.shape) == 3
    assert tensor.shape[0] == arity ** (degree + 1)
    assert tensor.shape[1] == arity
    assert tensor.shape[2] == dim
    assert multiindex_combs == (
        ((0,), (0,)),
        ((0,), (1,)),
        ((1,), (0,)),
        ((1,), (1,)),
    )


def test_get_multiindex_combinations_bivariate_one_dimensional_degree_two() -> None:
    """
    We have two 1-dimensional variables up to degree 2.

    So the only monomials are:
        x^0 y^0
        x^0 y^1
        x^0 y^2
        x^1 y^0
        x^1 y^1
        x^1 y^2
        x^2 y^0
        x^2 y^1
        x^2 y^2

    The tensor ``multiindex_combs`` has three dimensions:
        1. combinations of multiindices (unique monomials)
        2. arity
        3. dim
    """
    arity = 2
    dim = 1
    degree = 2
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert len(tensor.shape) == 3
    assert tensor.shape[0] == (degree + 1) ** arity
    assert tensor.shape[1] == arity
    assert tensor.shape[2] == dim
    assert multiindex_combs == (
        ((0,), (0,)),
        ((0,), (1,)),
        ((0,), (2,)),
        ((1,), (0,)),
        ((1,), (1,)),
        ((1,), (2,)),
        ((2,), (0,)),
        ((2,), (1,)),
        ((2,), (2,)),
    )

def test_get_multiindex_combinations_trivariate_one_dimensional_degree_two() -> None:
    """
    We have three 1-dimensional variables up to degree 2.

    So the only monomials are:
        x^0 y^0
        x^0 y^1
        x^1 y^0
        x^1 y^1

    The tensor ``multiindex_combs`` has three dimensions:
        1. Number of unique monomials
        2. Arity (number of vector variables per monomial)
        3. dim (number of multiindex components for each vector variable)
    """
    arity = 3
    dim = 1
    degree = 2
    multiindex_combs = get_multiindex_combinations(arity, dim, degree)
    tensor = np.array(multiindex_combs)
    logger.info(f"Multiindex combination tensor (shape): {tensor.shape}")
    assert len(tensor.shape) == 3
    assert tensor.shape[0] == (degree + 1) ** arity
    assert tensor.shape[1] == arity
    assert tensor.shape[2] == dim
