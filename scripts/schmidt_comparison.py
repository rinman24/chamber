import pandas as pd

import sys
sys.path.insert(0, 'C:/Users/sabre/Documents/GitHub/chamber')

from chamber.models import params
from chamber.models import props

df = pd.DataFrame()

if __name__=="__main__":
	for p in range(int(3e4), int(1.01325e5), int(1e4)):
		# Uses the model limit as the upper bound of the loop range
		for t in range(275, int(310*pow(p/101325, 0.09)), 5):
			for rh in (rh_int/100 for rh_int in range(5, 90, 5)):
				t_dp = props.get_tdp(p, t, rh)
				schmidt_mills = params.get_schmidt(p, t, t_dp, 'Mills')
				schmidt_marrero = params.get_schmidt(p, t, t_dp, 'Marrero')
				df = df.append({
					'Pressure (Pa)': p, 'Temperature (K)': t,
					'Dew Point (K)': t_dp, 'Ralative Humidity': rh,
				    'Schmidt Mills': schmidt_mills,
				    'Schmidt Marrero': schmidt_marrero
				    }, ignore_index=True)

	df[['Pressure (Pa)', 'Temperature (K)', 'Dew Point (K)','Ralative Humidity',
		'Schmidt Mills', 'Schmidt Marrero']].to_csv('schmidt_comparison.csv')
