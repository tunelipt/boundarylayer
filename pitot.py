import numpy as np


class Pitot(object):

    def __init__(self, cd=0.997, rho=1.08):

        self.cd = cd
        self.rho = 1.08

    def __call__(self, dp, rho=None):

        if rho is None:
            rho = self.rho

        return self.cd * np.sqrt(2*dp/rho)

        
