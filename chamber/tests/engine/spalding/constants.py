"""Constants used for Spalding engine unit testing."""

import uncertainties as un

mass = 0.099
press = 101325
amb_temp = 290
dew_point = 280
# TS_VALUE = 285

t_s_guess = un.ufloat(290, 0.2)

spald_input = dict(
    m=mass, p=press, t_e=amb_temp, t_dp=dew_point,
    ref='Mills', rule='1/2')

exp_state = dict(
    L=un.ufloat(0.04351613825556731, 0.0012399392152624728),
    P=un.ufloat(101325.0, 151.9875),
    T_e=un.ufloat(290, 0.2),
    T_dp=un.ufloat(280, 0.2),
    )

properties = ['film_guide', 'exp_state', 't_s_guess', 's_state']

m_1s_g = un.ufloat(0.01192707878398699, 0.00013523614304376794)
