"""Unit testing of `film` module."""

import math

import pytest

from chamber import film


P_VALUE = 101325
T_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 285


def test_use_rule():
    e_value = 1
    s_value = 0

    # Test e = 0 and s = 1 with '1/2'
    assert math.isclose(
        film.use_rule(e_value, s_value, '1/2'),
        1/2
    )

    # Test e = 0 and s = 1 with '1/3'
    assert math.isclose(
        film.use_rule(e_value, s_value, '1/3'),
        1/3
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.use_rule(e_value, s_value, '1/4')
    err_msg = "'1/4' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)

    # Test temp_e = 300 and temp_s = 290 with '1/2'
    temp_e = 300
    temp_s = 290
    assert math.isclose(
        film.use_rule(temp_e, temp_s, '1/2'),
        295
    )

    # Test temp_e = 300 and temp_s = 290 with '1/3'
    assert math.isclose(
        film.use_rule(temp_e, temp_s, '1/3'),
        293.3333333333333
    )


def test__est_c_pm():
    # Test rule = '1/2'
    assert math.isclose(
        film._est_c_pm(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        1019.9627505486458
    )

    # Test rule = '1/3'
    assert math.isclose(
        film._est_c_pm(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        1020.7363637843752
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film._est_c_pm(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/5')
    err_msg = "'1/5' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test__est_rho_m():
    # Test rule = '1/2'
    assert math.isclose(
        film._est_rho_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        1.2229936606324967
    )

    # Test rule = '1/3'
    assert math.isclose(
        film._est_rho_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        1.2262478476537964
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film._est_rho_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '24 Sep 1984')
    err_msg = "'24 Sep 1984' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test__est_k_m():
    # Test rule = '1/2'
    assert math.isclose(
        film._est_k_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        0.025446947707731902
    )

    # Test rule = '1/3'
    assert math.isclose(
        film._est_k_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        0.025384761174818384
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film._est_k_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '20 Mar 1987')
    err_msg = "'20 Mar 1987' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)


def test__est_alpha_m():
    # Test rule = '1/2'
    assert math.isclose(
        film._est_alpha_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        2.040317009201964e-05
    )

    # Test rule = '1/3'
    assert math.isclose(
        film._est_alpha_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        2.028355491502325e-05
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film._est_k_m(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, 'beta')
    err_msg = "'beta' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)
