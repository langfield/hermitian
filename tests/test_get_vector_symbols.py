#!/usr/bin/env python3
from hermitian.functional import get_complex_vector_symbols, sprint


def test_get_complex_vector_symbols() -> None:
    arity = 3
    dim = 3
    symbols = get_complex_vector_symbols(arity, dim)
    assert len(symbols) == arity
    assert len(symbols[0]) == dim
