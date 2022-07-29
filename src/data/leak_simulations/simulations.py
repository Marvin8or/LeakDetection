


from email import generator
import os
from pathlib import Path
import pickle
from collections import OrderedDict
from tokenize import generate_tokens
import wntr
import pandas as pd
import numpy as np

class WaterNetworkLeakSimulations(wntr.sim.WNTRSimulator):
    #NOTE Description

    _simulation_ID = 0

    def __init__(self, wn, simulations_per_process: int):
        super().__init__(wn)
        self.wn = wn
        self.simulations_per_process = simulations_per_process

    def _initialize_internal_datasets(self):
        #NOTE Description
        _columns = len(self.wn.report_options["input_report_options"]) * len(self.wn.sensors) \
                * (self.wn.options.time.duration // self.wn.options.time.report_timestep \
                + 1) + len(self.wn.report_options["output_report_options"])

        _rows = self.simulations_per_process

        return np.empty(shape=(_rows, _columns))

    @staticmethod
    def increment_simulation_ID():
        WaterNetworkLeakSimulations._simulation_ID += 1

    def _get_random_output_variables(self) -> generator:
        """
        Returns ID of pipe, Leak Area or Start Time based
        on ther wn.output_report_variables defined by the user

        Intended use:
        >>> self.wn.output_report_variables
        ... ("ID", "Leak Area", "Start Time")
        >>> output_variables: generator = _get_random_output_variables()
        >>> _ID, _leak_area, _start_time = next(output_variables)
        >>> _ID
        ... JUNCTION-5
        >>> _leak_area
        ... 0.75
        >>> _start_time
        ... 13:25
        """
        # get random node to be leak node
        
        pipes_ID_and_diameter = {link_name: self.wn.get_link(link_name).diameter for link_name in self.wn.links.pipe_names}

        #XXX doesnt work
        random_pipe = np.random.choice(pipes_ID_and_diameter.keys)
        # self.wn.report_variables

        pass

        # yield _output_variables:tuple

        

    def run_leak_sim(self):
        #NOTE Description
        _initial_dataset = self._initialize_internal_datasets()

        with open(Path(os.getcwd(), "pickle_files", f"simulation_{self._simulation_ID}.pickle"), "wb") as pickleObj:
            pickle.dump(self.wn, pickleObj)

        _output_vars = self._get_random_output_variables()
        for simulation_index in range(self.simulations_per_process):

            _ID, _leak_area, _start_time = next(_output_vars)
            pass

