"""Constants used for Spalding engine unit testing."""

import uncertainties as un

mass = 0.099
press = 101325
amb_temp = 290
dew_point = 280
ref = 'Mills'
rule = '1/2'

spald_input = dict(
    m=mass, p=press, t_e=amb_temp, t_dp=dew_point,
    ref=ref, rule=rule)

exp_state = dict(
    L=un.ufloat(0.04351613825556731, 0.0012399392152624728),
    P=un.ufloat(101325.0, 151.9875),
    T_e=un.ufloat(amb_temp, 0.2),
    T_dp=un.ufloat(280, 0.2),
    )

initial_s_state = dict(
    h=0,
    h_fg=2460974.1659213207,
    m_1=0.011919754919993641,
    T=amb_temp,
    )

initial_u_state = dict(
    T=amb_temp,
    h=-2460974.1659213207,
    )

initial_liq_props = dict(
    c_p=4186.928150136838,
    T=amb_temp,
    )

properties = ['film_guide', 'exp_state', 's_state', 'u_state', 'liq_props']
