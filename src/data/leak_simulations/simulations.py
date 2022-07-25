

import wntr
import pandas as pd
import numpy as np
from src.data.leak_results import SensorLayoutResults



class WaterNetworkLeakSimulations(wntr.sim.WNTRSimulator):
    #NOTE Description
    def __init__(self, wn, simulations_per_process: int, save_simulations_params: tuple, save_leak_params: tuple):
        super().__init__(wn)
        self.wn = wn
        self.simulations_per_process = simulations_per_process
        self.save_simulations_params = save_simulations_params
        self.save_leak_params = save_leak_params

    def _initialize_internal_datasets(self):
        #NOTE Description
        _columns = len(self.save_simulations_params) * len(self.wn.sensors) \
                * (self.wn.options.time.duration // self.wn.options.time.report_timestep \
                + 1) + len(self.save_leak_params)

        _rows = self.simulations_per_process

        return np.empty(shape=(_rows, _columns))

    
    def run_leak_sim(self):
        #NOTE Description
        _initial_dataset = self._initialize_internal_datasets()
