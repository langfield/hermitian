#!/usr/bin/env python3
from loguru import logger
from beartype import beartype

from sympy import expand, latex, symbols, conjugate, FiniteSet, MatrixSymbol, Matrix, Expr

from hermitian.aliases import Tuple
from hermitian.functional import (
    sprint,
    is_in_SU_AB,
    get_primitive_pth_roots_of_unity,
    get_type_iii_gamma,
    get_phi_gamma_z,
    get_phi_gamma_z_w_polarized,
    get_theta_x_from_phi_gamma,
    run_experiment_with_fuzzed_parameters_a_b_p_q,
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
        sprint(FiniteSet(*group))

        # Only ever try one primitive root because they're all equivalent.
        break


@beartype
def check_phi_is_hermitian_symmmetric(
    a: int, b: int, p: int, q: Tuple[int, ...]
) -> bool:
    # Get the polynomial in terms of (z, w).
    phi_gamma, z, w, z_symbol, w_symbol = get_phi_gamma_z_w_polarized(a,b,p,q)
    logger.info("Phi(z,bar{w}):")
    sprint(phi_gamma)

    # Make some dummy symbols.
    z_prime_symbol = MatrixSymbol("z'", a + b, 1)
    w_prime_symbol = MatrixSymbol("w'", a + b, 1)

    # Swap (z, w).
    phi_gamma_w_z_bar = phi_gamma.subs(z_symbol, w_prime_symbol)
    phi_gamma_w_z_bar = phi_gamma_w_z_bar.subs(w_symbol, z_symbol)
    phi_gamma_w_z_bar = phi_gamma_w_z_bar.subs(w_prime_symbol, w_symbol)
    logger.info("Phi(w,bar{z}):")
    sprint(phi_gamma_w_z_bar)

    # Complex-conjugate the whole thing.
    phi_gamma_w_z_bar_conjugate = conjugate(phi_gamma_w_z_bar)
    logger.info("overline{Phi(w,bar{z})}:")
    sprint(phi_gamma_w_z_bar_conjugate)

    # Return truth value of whether the polynomial is Hermitian symmetric.
    return phi_gamma == phi_gamma_w_z_bar_conjugate


def main() -> None:
    MAX_N = 2
    MAX_P = 3
    run_experiment_with_fuzzed_parameters_a_b_p_q(
        check_phi_is_hermitian_symmmetric, max_n=MAX_N, max_p=MAX_P, min_a=1, min_b=1
    )


if __name__ == "__main__":
    main()
