"""Integration test suite for analysis engine."""


import dacite as dac

from chamber.access.experiment.contracts import (
    FitSpec
)
from chamber.access.experiment.models import (
    Fit
)

# ----------------------------------------------------------------------------
# Fixtures


# ----------------------------------------------------------------------------
# AnalysisEngine


def test_persist_fits(
        anlys_eng, exp_acc, tube_spec, setting_spec, experiment_spec,
        observation_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Use ExperimentAccess to add a tube, a setting, an experiment, and some
    # observations.
    access = exp_acc
    _ = access._add_tube(tube_spec)
    setting_id = access._add_setting(setting_spec)
    experiment_id = access._add_experiment(experiment_spec, setting_id)
    _ = access._add_observations(observation_spec, experiment_id)
    # Setup a list of fits to add
    fits_to_add = []
    data = dict(
        a=0.1,
        sig_a=0.01,
        b=-0.2,
        sig_b=0.02,
        r2=0.99,
        q=1e-8,
        chi2=9.5,
        nu=11,
        exp_id=experiment_id,
        idx=0,
    )
    fit_spec = dac.from_dict(FitSpec, data)
    fits_to_add.append(fit_spec)
    # Now the second one
    data = dict(
        a=0.11,
        sig_a=0.011,
        b=-0.21,
        sig_b=0.021,
        r2=0.991,
        q=1.1e-8,
        chi2=9.51,
        nu=111,
        exp_id=experiment_id,
        idx=1,
    )
    fit_spec = dac.from_dict(FitSpec, data)
    fits_to_add.append(fit_spec)
    # Act --------------------------------------------------------------------
    num_fits_added = anlys_eng._persist_fits(fits_to_add)
    # Assert -----------------------------------------------------------------
    assert num_fits_added == 2
    # Now query result -------------------------------------------------------
    session = access.Session()
    try:
        query = session.query(Fit).filter(Fit.experiment_id == 1)
        queried_fits = query.all()
        session.commit()
        assert len(queried_fits) == 2
        for fit in queried_fits:
            if fit.idx == 0:
                assert fit.a == 0.1
                assert fit.sig_a == 0.01
                assert fit.b == -0.2
                assert fit.sig_b == 0.02
                assert fit.r2 == 0.99
                assert fit.q == 1e-8
                assert fit.chi2 == 9.5
                assert fit.nu == 11
            elif fit.idx == 1:
                assert fit.a == 0.11
                assert fit.sig_a == 0.011
                assert fit.b == -0.21
                assert fit.sig_b == 0.021
                assert fit.r2 == 0.991
                assert fit.q == 1.1e-8
                assert fit.chi2 == 9.51
                assert fit.nu == 111
    finally:
        session.close()
