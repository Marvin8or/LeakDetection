

import os
from pathlib import Path
import pickle
import wntr
import pandas as pd
import numpy as np
from src.data.leak_results import SensorLayoutResults

class WaterNetworkLeakSimulations(wntr.sim.WNTRSimulator):
    #NOTE Description

    _simulation_ID = 0

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

    @staticmethod
    def increment_simulation_ID():
        WaterNetworkLeakSimulations._simulation_ID += 1

    def run_leak_sim(self):
        #NOTE Description
        _initial_dataset = self._initialize_internal_datasets()

        with open(Path(os.getcwd(), "pickle_files", f"simulation_{self._simulation_ID}.pickle"), "wb") as pickleObj:
            pickle.dump(self.wn, pickleObj)

        for simulation_index in range(self.simulations_per_process):
            pass

