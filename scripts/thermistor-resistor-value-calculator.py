import math

import scipy.optimize
import pandas as pd
import numpy as np

# Goal: Fit data to find three parameters

# Goal: optimize ref resistor value

# Goal: make sure min and max within range
# Goal: make sure min and max +/-1C detectable

class Thermistor:
    """ Thermistor model class. """
    def __init__(self, Rt=10000, params=np.array([0.003354, 2.5e-4, 0])):
        self.Rt= Rt
        self.params = params
             
    def sh(self, R, A, B, D):
        """ 
        Steinhart-Hart function.
        Returns temperature in C.
        """
        log = np.log(R/float(self.Rt))
        return 1.0/(A + B*log + D*log**3)-273.15
        
    def fit(self, data):
        """ Find A, B and D for the Steinhart-Hart equation. 
        1/T= A + B*ln(R/Rt) + D*ln(R/Rt)^3.

        @param data: pandas dataframe, first column is temperature (C), second is resistance (Ohm).
        """
        # Filter on temperatures >= 0C
        view = data[data.iloc[:,0] >= 0]
        self.params, self.err = scipy.optimize.curve_fit(self.sh, view.iloc[:,1], view.iloc[:,0], self.params)
    
    def temperature(self, r):
        """ Predict the temperature for a certain resistance. """
        return self.sh(r, *self.params)

class Sensor:
    """ Model the system with the thermistor, ADC and reference resistor. """
    
    def __init__(self, thermistor=Thermistor(), resistor=3000):
        self.thermistor = thermistor
        self.resistor = resistor

    def temp(self, N):
        """
        Return the temperature for a reading of N on the ADC.
        """
        R = float(N*self.resistor)/(1024-N)
        return self.thermistor.temperature(R)

