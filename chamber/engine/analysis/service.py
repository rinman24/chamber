"""Analysis engine service."""


import dacite
import pandas as pd
from math import log, pi

from CoolProp.HumidAirProp import HAPropsSI
from scipy.stats import chi2
from uncertainties import ufloat

from chamber.access.experiment.service import ExperimentAccess
from chamber.access.experiment.contracts import FitSpec

from chamber.utility.io.contracts import Prompt
from chamber.utility.io.service import IOUtility

from chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot
from chamber.utility.plot.service import PlotUtility


class AnalysisEngine(object):
    """TODO: docstring."""

    def __init__(self, experiment_id):
        """TODO: docstring."""
        self._experiment_id = experiment_id

        self._exp_acc = ExperimentAccess()
        self._io_util = IOUtility()
        self._plot_util = PlotUtility()

        self._error = 0.01
        self._fits = []
        self._idx = 1
        self._steps = 1

        # IR sensor calibration
        self._a = ufloat(-2.34, 0.07)
        self._b = ufloat(1.0445, 0.0022)

        # Tube radius; TODO: move to access method to obtain dynamically.
        self._R = ufloat(0.015, 0.0001)
        self._A = pi*self._R**2
        self._M1 = 18.015
        self._M2 = 28.964

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def process_fits(self, data):
        """TODO: docstring."""
        self._data = data
        self._get_observations()
        layout = self._layout_observations()
        self._plot_util.plot(layout)
        prompt = dacite.from_dict(
            Prompt,
            data=dict(messages=['Would you like to continue?: [y]/n ']),
        )
        response = self._io_util.get_input(prompt)[0]
        if (not response) or ('y' in response):
            self._get_fits()
            self._persist_fits()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _get_observations(self):
        # Create empty lists to hold data as we iterate through observations.
        dew_point = []
        mass = []
        pow_ref = []
        pressure = []
        surface_temp = []
        ic_temp = []

        cap_man = []
        optidew = []

        temp = []

        time = []

        # Interate and append observations while adding uncertainties
        observations = self._data.observations
        initial_idx = observations[0].idx
        for obs in observations:
            dew_point.append(ufloat(obs.dew_point, 0.2))
            mass.append(ufloat(obs.mass, 1e-7))
            pow_ref.append(ufloat(obs.pow_ref, abs(float(obs.pow_ref)) * 0.05))
            pressure.append(ufloat(obs.pressure, int(obs.pressure * 0.0015)))
            surface_temp.append(ufloat(obs.surface_temp, 0.5))
            ic_temp.append(ufloat(obs.ic_temp, 0.2))

            # Average temperatures with error propagation
            temps = obs.temperatures
            temp.append(
                sum(ufloat(temp.temperature, 0.2) for temp in temps)
                / len(temps)
                )

            # Bools for equipment status
            cap_man.append(obs.cap_man_ok)
            optidew.append(obs.optidew_ok)

            # Ensure that time starts at zero
            time.append(obs.idx - initial_idx)

        # DataFrame payload
        data = dict(
            Tdp=dew_point,
            m=mass,
            Jref=pow_ref,
            P=pressure,
            Te=temp,
            Ts=surface_temp,
            Tic=ic_temp,
            cap_man=cap_man,
            optidew=optidew,
            )

        self._observations = pd.DataFrame(index=time, data=data)

    def _layout_observations(self):
        # internal helper logic
        def nominal(ufloat_):
            return ufloat_.nominal_value

        def std_dev(ufloat_):
            return ufloat_.std_dev

        # DataSeries ---------------------------------------------------------
        data_series = dict()
        # First get the time data series
        data = dict(values=self._observations.index.tolist())
        data_series['t'] = dacite.from_dict(DataSeries, data)
        # dew point, Tdp
        data = dict(
            values=self._observations.Tdp.map(nominal).tolist(),
            sigma=self._observations.Tdp.map(std_dev).tolist(),
            label='Tdp')
        data_series['Tdp'] = dacite.from_dict(DataSeries, data)
        # mass, m
        data = dict(
            values=self._observations.m.map(nominal).tolist(),
            sigma=self._observations.m.map(std_dev).tolist(),
            label='m')
        data_series['m'] = dacite.from_dict(DataSeries, data)
        # pow_ref, Jref
        data = dict(
            values=self._observations.Jref.map(nominal).to_list(),
            sigma=self._observations.Jref.map(std_dev).to_list(),
            label='Jref')
        data_series['Jref'] = dacite.from_dict(DataSeries, data)
        # pressure, P
        data = dict(
            values=self._observations.P.map(nominal).tolist(),
            sigma=self._observations.P.map(std_dev).tolist(),
            label='P')
        data_series['P'] = dacite.from_dict(DataSeries, data)
        # Ambient temp, Te
        data = dict(
            values=self._observations.Te.map(nominal).tolist(),
            sigma=self._observations.Te.map(std_dev).tolist(),
            label='Te')
        data_series['Te'] = dacite.from_dict(DataSeries, data)
        # Surface temp, Ts
        data = dict(
            values=self._observations.Ts.map(nominal).tolist(),
            sigma=self._observations.Ts.map(std_dev).tolist(),
            label='Ts')
        data_series['Ts'] = dacite.from_dict(DataSeries, data)
        # IC temp, Tic
        data = dict(
            values=self._observations.Tic.map(nominal).tolist(),
            sigma=self._observations.Tic.map(std_dev).tolist(),
            label='Tic')
        data_series['Tic'] = dacite.from_dict(DataSeries, data)
        # Cap-man status, cap_man
        data = dict(
            values=self._observations.cap_man.tolist(),
            label='cap_man')
        data_series['cap_man'] = dacite.from_dict(DataSeries, data)
        # Optidew status, optidew
        data = dict(
            values=self._observations.optidew.tolist(),
            label='optidew')
        data_series['optidew'] = dacite.from_dict(DataSeries, data)

        # Axes ---------------------------------------------------------------
        axes = dict()

        data = dict(
            data=[data_series['m']], y_label='mass, [kg]',
            error_type='continuous')
        axes['mass'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['Tdp'], data_series['Te'], data_series['Ts'],
                  data_series['Tic']],
            y_label='temperature, [K]',
            error_type='continuous')
        axes['temp'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['P']], y_label='pressure, [Pa]',
            error_type='continuous')
        axes['pressure'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['Jref']], y_label='Ref power, [W]',
            error_type='continuous')
        axes['Jref'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['cap_man'], data_series['optidew']],
            y_label='status')
        axes['status'] = dacite.from_dict(Axis, data)

        # Then the Plots ---------------------------------------------------------
        plots = dict()

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['mass'], axes['temp']],
            x_label='index')
        plots['mass_and_temp'] = dacite.from_dict(Plot, data)

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['pressure']],
            x_label='index')
        plots['pressure'] = dacite.from_dict(Plot, data)

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['Jref'], axes['status']],
            x_label='index')
        plots['pow_and_status'] = dacite.from_dict(Plot, data)

        # Finally, the layout ----------------------------------------------------
        data = dict(
            plots=[
                plots['mass_and_temp'], plots['pressure'],
                plots['pow_and_status']
                ],
            style='seaborn-darkgrid')

        return dacite.from_dict(Layout, data)

    def _get_fits(self):  # TODO: This mehod should also get the non-dimensional results for the fit.
        # len - 2 because we want to make sure we never end up at the last
        # index and can't take a max slice
        while self._idx < len(self._observations) - 2:
            # Get the max slice
            left = (2 * self._idx) - len(self._observations) + 1
            right = 2 * self._idx
            self._sample = self._observations.loc[left:right, :]
            # Then search for the best fit and act accordingly
            self._get_best_local_fit()
            if self._this_fit:  # We got a fit that met the error threshold
                self._evaluate_fit()
                # TODO: self._nondimensionalize_fit()
                # NOTE: The line above will also require updateing database
                #    and orms.
                self._fits.append(self._evaluated_fit)
                # Length of the best fit is the degrees of freedom plus 2 for
                # a linear fit
                self._idx += self._evaluated_fit['nu'] + 2
            else:  # _get_best_local_fit returned None
                self._idx += len(self._sample)

    def _persist_fits(self):
        counter = 0
        for data in self._fits:
            fit_spec = dacite.from_dict(FitSpec, data)
            self._exp_acc.add_fit(fit_spec, self._experiment_id)
            counter += 1
        return counter

    # Properties .............................................................

    def _set_local_exp_state(self):
        samples = len(self._this_sample)
        data = self._this_sample
        offset = 273.15

        # Use calibration for ifrared sensor
        Ts_bar_K = sum(data.Ts)/samples
        Ts_bar_C = Ts_bar_K - offset
        Ts_bar_C = self._a + self._b*Ts_bar_C
        Ts_bar_K = Ts_bar_C + offset

        # Now the rest of the state variables
        Te_bar = sum(data.Te)/samples
        Tdp_bar = sum(data.Tdp)/samples
        P_bar = sum(data.P)/samples

        self._experimental_state = dict(
            Te=Te_bar,
            Tdp=Tdp_bar,
            Ts=Ts_bar_K,
            P=P_bar,
        )

    def _set_local_properties(self):
        # Internal mapper ----------------------------------------------------
        def x1_2_m1(self, x1):
            num = self._M1 * x1
            den = num + (self._M2 * (1 - x1))
            return num/den

        Ts = self._experimental_state['Ts']
        P = self._experimental_state['P']
        Te = self._experimental_state['Te']
        Tdp = self._experimental_state['Tdp']

        # mddp ---------------------------------------------------------------
        mdot = ufloat(-self._this_fit['b'], self._this_fit['sig_b'])
        mddp = mdot/self._A  # TODO: use exp_acc to get R and A

        # x1 -----------------------------------------------------------------
        # s-state
        x1s_nv = HAPropsSI(
            'psi_w',
            'T', Ts.nominal_value,
            'P', P.nominal_value,
            'RH', 1)
        x1s_sig = x1s_nv - HAPropsSI(
            'psi_w',
            'T', Ts.nominal_value + Ts.std_dev,
            'P', P.nominal_value,
            'RH', 1)
        x1s = ufloat(x1s_nv, abs(x1s_sig))
        # e-state
        x1e_nv = HAPropsSI(
            'psi_w',
            'T', Te.nominal_value,
            'P', P.nominal_value,
            'Tdp', Tdp.nominal_value)
        x1e_sig = x1e_nv - HAPropsSI(
            'psi_w',
            'T', Te.nominal_value + Te.std_dev,
            'P', P.nominal_value,
            'Tdp', Tdp.nominal_value + Tdp.std_dev)
        x1e = ufloat(x1e_nv, abs(x1e_sig))

        # m1 -----------------------------------------------------------------
        # s-state
        m1s = x1_2_m1(self, x1s)
        # e-state
        m1e = x1_2_m1(self, x1e)

        # rho ---------------------------------------------------------------
        # s-state
        rhos_nv = 1 / HAPropsSI(
            'Vha',
            'T', Ts.nominal_value,
            'P', P.nominal_value,
            'Y', x1s_nv)
        rhos_sig = rhos_nv - (
            1 / HAPropsSI(
                'Vha',
                'T', Ts.nominal_value + Ts.std_dev,
                'P', P.nominal_value,
                'Y', x1s_nv)
        )
        rhos = ufloat(rhos_nv, abs(rhos_sig))
        # e-state
        rhoe_nv = 1 / HAPropsSI(
            'Vha',
            'T', Te.nominal_value,
            'P', P.nominal_value,
            'Y', x1e_nv)
        rhoe_sig = rhoe_nv - (
            1 / HAPropsSI(
                'Vha',
                'T', Te.nominal_value + Te.std_dev,
                'P', P.nominal_value,
                'Y', x1e_nv)
        )
        rhoe = ufloat(rhoe_nv, abs(rhoe_sig))

        # Bm1 ----------------------------------------------------------------
        Bm1 = (m1s - m1e)/(1-m1s)

        # T ------------------------------------------------------------------
        T = (Te+Ts) / 2

        # D12 ----------------------------------------------------------------
        D12 = 1.97e-5 * (101325/P) * pow(T/256, 1.685)

        # set properties
        self._properties = dict(
            mddp=mddp,
            x1s=x1s,
            x1e=x1e,
            x1=(x1s+x1e) / 2,
            m1s=m1s,
            m1e=m1e,
            m1=(m1s+m1e) / 2,
            rhos=rhos,
            rhoe=rhoe,
            rho=(rhos+rhoe) / 2,
            Bm1=Bm1,
            T=T,
            D12=D12,
        )

    def _set_nondim_groups(self):
        Bm1 = self._properties['Bm1']
        mddp = self._properties['mddp']
        R = self._R
        rho = self._properties['rho']
        D12 = self._properties['D12']

        # We need to perform the log propagation manually
        ln_Bm1_nv = log(1 + Bm1.nominal_value)
        ln_Bm1_sig = ln_Bm1_nv - log(1 + Bm1.nominal_value + Bm1.std_dev)
        ln_Bm1 = ufloat(ln_Bm1_nv, abs(ln_Bm1_sig))

        # ShR ----------------------------------------------------------------
        ShR = (mddp * R) / (ln_Bm1 * rho * D12)

        self._nondim_groups = dict(
            ShR=ShR,
        )

    # ------------------------------------------------------------------------
    # Class helpers: internal use only

    def _ols_fit(self):
        sample = self._this_sample['m'].tolist()
        # Prepare the data
        y = [i.nominal_value for i in sample]
        sig = [i.std_dev for i in sample]
        x = list(range(len(y)))  # Always indexed at zero

        # Determine fit components
        S = sum(1/sig[i]**2 for i in range(len(x)))
        Sx = sum(x[i]/sig[i]**2 for i in range(len(x)))
        Sy = sum(y[i]/sig[i]**2 for i in range(len(x)))
        Sxx = sum(x[i]**2/sig[i]**2 for i in range(len(x)))
        Sxy = sum(x[i]*y[i]/sig[i]**2 for i in range(len(x)))
        Delta = S*Sxx - Sx**2

        # Now calculate model parameters: y = a + bx
        a = (Sxx*Sy - Sx*Sxy) / Delta
        sig_a = (Sxx/Delta)**0.5
        b = (S*Sxy - Sx*Sy) / Delta
        sig_b = (S/Delta)**0.5

        return dict(
            a=a,
            sig_a=sig_a,
            b=b,
            sig_b=sig_b,
            )

    def _get_best_local_fit(self):
        # self._sample always has an odd length, so we use integer division.
        center = len(self._sample) // 2
        steps = int(self._steps)  # Explicitly make a copy
        delta = int(steps)  # Explicityly make a copy
        while center + steps + 1 <= len(self._sample):
            self._this_sample = (
                self._sample.iloc[center - steps: center + steps + 1, :]
            )
            fit = self._ols_fit()
            # With small sample sizes, b is sometimes zero.
            # If this is the case we want to continue.
            if fit['b'] == 0:
                steps += delta
                continue
            elif fit['sig_b']/abs(fit['b']) <= self._error:
                self._this_fit = fit
                return
            else:
                steps += delta
        # We did not find a fit
        self._this_fit = None

    def _evaluate_fit(self):
        fit = self._this_fit
        # Prepare the data
        y = [i.nominal_value for i in self._this_sample['m']]
        sig = [i.std_dev for i in self._this_sample['m']]
        x = list(range(len(y)))  # Always indexed at zero

        a = self._this_fit['a']
        b = self._this_fit['b']

        # Calculate R^2
        predicted = [a + b*i for i in x]
        y_bar = sum(y)/len(y)
        SSres = sum((y[i] - predicted[i])**2 for i in range(len(x)))
        SStot = sum((y[i] - y_bar)**2 for i in range(len(x)))
        R2 = 1 - SSres/SStot

        # Now for the merit function; i.e. chi^2
        merit_value = sum(((y[i] - a - b*x[i])/sig[i])**2 for i in range(len(x)))

        # And the goodness of fit; i.e. Q from Numerical Recipes
        Q = chi2.sf(merit_value, len(x)-2)

        # Prepare payload
        data = fit  # copy of a, b, sig_a, and sig_b
        data['r2'] = R2
        data['q'] = Q
        data['chi2'] = merit_value
        data['nu'] = len(x) - 2
        data['exp_id'] = self._experiment_id
        data['idx'] = self._idx

        self._evaluated_fit = data
