"""Unit testing of models2.py."""

import math

import pytest

import chamber.models2 as mods


PROP_STATE = dict(p=101325, t=295, x=0.013)
EXP_STATE = dict(p=80000, tch=290, tdp=280, tm=291)
TS_GUESS = 285


@pytest.fixture(scope='module')
def props():
    return mods.Properties()


@pytest.fixture(scope='module')
def exp_state():
    return mods.ExperimentalState(**EXP_STATE)


@pytest.fixture(scope='module')
def ref_state():
    return mods.ReferenceState(TS_GUESS, EXP_STATE)


class Test_ExperimentalState:
    """Unit testing of `ExperimentalState` class."""

    def test__init__(self, exp_state):
        assert math.isclose(exp_state.p, 80000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 280)
        assert math.isclose(exp_state.tm, 291)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.p = 90000
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.tch = 300
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.tdp = 300
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.tm = 300
        assert "can't set attribute" == str(excinfo.value)

    def test_update(self, exp_state):
        new_state = dict(p=90000, tch=290, tdp=284, tm=290.5)
        exp_state._update(**new_state)

        assert math.isclose(exp_state.p, 90000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 284)
        assert math.isclose(exp_state.tm, 290.5)


class Test_ReferenceState:
    """Unit testing of `ExperimentalState` class."""

    def test__init__(self, ref_state):
        assert math.isclose(ref_state.ts_guess, 285)

        assert isinstance(ref_state._ExpState, mods.ExperimentalState)
        assert math.isclose(ref_state._ExpState.p, 80000)
        assert math.isclose(ref_state._ExpState.tch, 290)
        assert math.isclose(ref_state._ExpState.tdp, 280)
        assert math.isclose(ref_state._ExpState.tm, 291)

        assert isinstance(ref_state._Props, mods.Properties)
        assert ref_state._Props.rho is None
        assert ref_state._Props.k is None
        assert ref_state._Props.cp is None
        assert ref_state._Props.alpha is None
        assert ref_state._Props.d12 is None
        assert ref_state._Props.ref == 'Mills'

        assert ref_state.rule == 'one-third'

        assert math.isclose(ref_state.p_film, 80000)
        assert math.isclose(ref_state.t_film, 287.0)
        assert ref_state.x_film is None
        assert ref_state.xe is None
        assert ref_state.xs is None

        with pytest.raises(AttributeError) as excinfo:
            ref_state.ts_guess = 290
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            ref_state.rule = 'one-half'
        assert "can't set attribute" == str(excinfo.value)

    def test_change_rule(self, ref_state):
        assert ref_state.rule == 'one-third'

        original_rule = ref_state.rule
        assert ref_state.change_rule('one-half')
        assert ref_state.rule == 'one-half'
        assert ref_state.change_rule(original_rule)

        with pytest.raises(ValueError) as excinfo:
            ref_state.change_rule('one')
        assert "'one' is not a valid `rule`." == str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            ref_state.change_rule(2)
        err_msg = "`rule` must be <class 'str'> not <class 'int'>."
        assert (err_msg == str(excinfo.value))

    def test_update(self, ref_state):
        assert math.isclose(ref_state.ts_guess, 285)

        original_ts_guess = ref_state.ts_guess

        # This also updates the properties.
        assert ref_state.update(300)
        assert math.isclose(ref_state.rho_film, 0.9267691278805217)
        assert math.isclose(ref_state.k_film, 0.026100437937392484)
        assert math.isclose(ref_state.cp_film, 1047.04407550437)
        assert math.isclose(ref_state.alpha_film, 2.689746012139042e-05)
        assert math.isclose(ref_state.d12_film, 3.204816199008461e-05)
        assert ref_state.update(original_ts_guess)

        with pytest.raises(TypeError) as excinfo:
            ref_state.update('300')
        err_msg = "`ts_guess` must be numeric not <class 'str'>."
        assert err_msg == str(excinfo.value)

    def test__use_rule(self, ref_state):
        assert ref_state.rule == 'one-third'
        original_rule = ref_state.rule
        assert math.isclose(ref_state._use_rule(1, 0), 1/3)
        assert ref_state.change_rule('one-half')
        assert math.isclose(ref_state._use_rule(1, 0), 0.5)
        assert ref_state.change_rule(original_rule)

    def test_eval_xe(self, ref_state):
        ref_state._eval_xe()
        assert math.isclose(ref_state.xe, 0.012439210352397811)

    def test_eval_xs(self, ref_state):
        ref_state._eval_xs()
        assert math.isclose(ref_state.xs, 0.01742142886750153)

    def test_eval(self, ref_state):
        ref_state._eval()
        assert math.isclose(ref_state.p_film, 80000)
        assert math.isclose(ref_state.t_film, 287.0)
        assert math.isclose(ref_state.x_film, 0.015760689362466957)

        assert math.isclose(ref_state._Props.rho, 0.965679984964966)
        assert math.isclose(ref_state._Props.k, 0.025391972939738265)
        assert math.isclose(ref_state._Props.cp, 1024.3338591579427)
        assert math.isclose(ref_state._Props.alpha, 2.5669752890094362e-05)
        assert math.isclose(ref_state._Props.d12, 3.0250984009617275e-05)


class Test_Properties:
    """Unit testing of `Properties` class."""

    def test__init__(self, props):
        assert props.rho is None
        assert props.k is None
        assert props.cp is None

        assert props.alpha is None
        assert props.d12 is None
        assert props.ref == 'Mills'

        with pytest.raises(AttributeError) as excinfo:
            props.rho = 1
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.k = 0.02
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.cp = 1000
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.alpha = 2e-5
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.d12 = 2.5e-5
        assert "can't set attribute" == str(excinfo.value)

    def test__eval_rho(self, props):
        props._eval_rho(**PROP_STATE)
        assert math.isclose(props.rho, 1.191183667721759)

    def test__eval_k(self, props):
        props._eval_k(**PROP_STATE)
        assert math.isclose(props.k, 0.026001674240925747)

    def test__eval_cp(self, props):
        props._eval_cp(**PROP_STATE)
        assert math.isclose(props.cp, 1021.6102706953045)

    def test__eval_alpha(self, props):
        props._eval_alpha()
        assert math.isclose(props.alpha, 2.1366694097871384e-05)

    def test_change_ref(self, props):
        assert props.ref == 'Mills'
        original_ref = props.ref
        assert props.change_ref('Marrero')
        assert props.ref == 'Marrero'
        assert props.change_ref(original_ref)

        with pytest.raises(ValueError) as excinfo:
            props.change_ref('ref')
        err_msg = "`ref` must be in ['Mills', 'Marrero']."
        assert (err_msg == str(excinfo.value))

        with pytest.raises(TypeError) as excinfo:
            props.change_ref(1)
        err_msg = "`ref` must be <class 'str'> not <class 'int'>."
        assert (err_msg == str(excinfo.value))

    def test__eval_d12(self, props):
        props._eval_d12(p=PROP_STATE['p'], t=PROP_STATE['t'])
        assert math.isclose(props.d12, 2.5016812959985912e-05)

        original_ref = props.ref
        assert props.change_ref('Marrero')
        props._eval_d12(p=PROP_STATE['p'], t=PROP_STATE['t'])
        assert math.isclose(props.d12, 2.450827945070588e-05)
        assert props.change_ref(original_ref)

    def test_eval(self, props):
        ref_state = dict(p=80000, t=300, x=0.022)
        assert props.eval(**ref_state)

        assert math.isclose(props.rho, 0.9215607460590561)
        assert math.isclose(props.k, 0.02633755190531086)
        assert math.isclose(props.cp, 1032.3912146477846)
        assert math.isclose(props.alpha, 2.768261652495241e-05)
        assert math.isclose(props.d12, 3.2595513279317516e-05)
