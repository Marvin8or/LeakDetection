


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

        # XXX Hardcoded
        self.wn.options.time.duration = 24 * 3600
        self.wn.options.time.hydraulic_timestep = 5 * 60
        self.wn.options.time.report_timestep = 5 * 60
        self.wn.options.hydraulic.demand_model = "PDD"
        self.wn.options.hydraulic.required_pressure = 15 # m H2O
        self.wn.options.hydraulic.minimum_pressure = 0

    def _initialize_internal_datasets(self):
        #NOTE Description
        _columns = int(len(self.wn._report_variables["input_report_variables"]) * len(self.wn.sensors) \
                * (self.wn.options.time.duration // self.wn.options.time.report_timestep \
                + 1) + len(self.wn._report_variables["output_report_variables"]))

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
        pipes_ID_and_diameter = {link_name: np.round(self.wn.get_link(link_name).diameter, 4) for link_name in self.wn.links.pipe_names}

        random_pipe_name = np.random.choice(list(pipes_ID_and_diameter.keys()))
        random_pipe_obj = self.wn.get_link(random_pipe_name)

        # XXX cant be hardcoded
        leak_area_perc = np.round(np.random.uniform(0, 0.8), 4)
        leak_diameter = random_pipe_obj.diameter * leak_area_perc

        # XXX also not hardcoded rounding
        leak_area = np.round(np.pi * (pipes_ID_and_diameter[random_pipe_name] / 2) ** 2, 6)

        self.wn = wntr.morph.split_pipe(
            self.wn, random_pipe_name, random_pipe_name + "_B", random_pipe_name + "_leak_node"
        )

        duration = self.wn.options.time.duration
        time_of_failure = np.round(np.random.uniform(0, duration / 3600, 1)[0], 4)
        leak_node = self.wn.get_node(random_pipe_name + "_leak_node")
        leak_node.add_leak(
            self.wn,
            area=leak_area,
            start_time=time_of_failure * 3600,
        )
        leak_node.leak_start_time = time_of_failure

        yield leak_node

        

    def run_leak_sim(self):
        #NOTE Description
        _initial_dataset = self._initialize_internal_datasets()

        with open(Path(os.getcwd(), "pickle_files", f"simulation_{self._simulation_ID}.pickle"), "wb") as pickleObj:
            pickle.dump(self.wn, pickleObj)

        _output_vars = self._get_random_output_variables()
        for simulation_index in range(self.simulations_per_process):

            _leak_node = next(_output_vars)
            sim = wntr.sim.WNTRSimulator(self.wn)
            results = sim.run_sim()

