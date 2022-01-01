#!/usr/bin/env python3
import sys
from loguru import logger
from beartype import beartype

import sympy as sy

from hermitian.aliases import Tuple
from hermitian.functional import (
    sprint,
    is_in_SU_AB,
    get_primitive_pth_roots_of_unity,
    get_type_iii_gamma,
    get_phi_gamma_z,
    get_phi_gamma_z_w_polarized,
    get_phi_gamma_z_w_polarized_no_bar,
    get_theta_x_from_phi_gamma,
    is_hermitian_symmetric_polynomial,
    is_hermitian_symmetric_matrix,
    run_experiment_with_fuzzed_parameters_a_b_p_q,
    get_matrix_of_coefficients,
)


@beartype
def check_type_iii_gamma_is_subset_of_SU_AB(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> None:
    """
    Check that type III gamma groups are always subgroups of SU(A,B) for
    appropriate values of A, B.
    """
    primitive_roots = get_primitive_pth_roots_of_unity(p)
    logger.info(f"Checking n={a + b}, a={a}, b={b}, p={p}, q={q}")
    for omega in primitive_roots:
        group = get_type_iii_gamma(a, b, p, q, omega)
        for gamma in group:
            assert is_in_SU_AB(gamma, a, b)
        logger.info(f"Gamma_{{{p};{q}}}:")
        sprint(sy.FiniteSet(*group))

        # Only ever try one primitive root because they're all equivalent.
        break


@beartype
def check_phi_is_hermitian_symmetric(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> None:
    r"""Experiment to check that \Phi_\Gamma is Hermitian symmetric."""
    # Get the polynomial in terms of (z, w).
    phi_gamma, z, w, z_symbol, w_symbol = get_phi_gamma_z_w_polarized(a, b, p, q)
    logger.info("Phi(z,bar{w}):")
    sprint(phi_gamma)
    phi_gamma, z, w, z_symbol, w_symbol = get_phi_gamma_z_w_polarized_no_bar(a, b, p, q)
    logger.info("Phi(z,w):")
    sprint(phi_gamma)
    get_matrix_of_coefficients(phi_gamma)
    sys.exit()

    assert is_hermitian_symmetric_polynomial(phi_gamma, z_symbol, w_symbol)
    # assert is_hermitian_symmetric_matrix(c_alpha_beta)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
