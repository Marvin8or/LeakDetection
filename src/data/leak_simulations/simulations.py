import os
import pickle
import wntr
import re
import pandas as pd
from pathlib import Path
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
        _columns = int(len(self.wn.stored_data_features["input_report_variables"]) * len(self.wn.sensors) \
                    * (self.wn.options.time.duration // self.wn.options.time.report_timestep + 1) \
                    + len(self.wn.stored_data_features["output_report_variables"]))

        _rows = self.simulations_per_process

        return np.empty(shape=(_rows, _columns))

    def _arange_dataset_features(self, dataset_to_fill, index, results, leak_node) -> None:
        
        _, _columns = np.shape(dataset_to_fill)

        # ID, A, ST, ...S1P, ...S1D, ...S2P, ...S2D, ...S3P, ...S3D, ...
        aranged_simulation_results = np.empty(shape=_columns)

        output_report_variables_values = np.array([])

        # ID must always be specified
        _ID = float(re.search(r'\d+', leak_node.name).group())

        tmp_dict = {"ID": _ID,
                    "Leak Area": leak_node._leak_area,
                    "Start Time": leak_node._leak_start_time}

        # Append output parameters 
        for param in self.wn.stored_data_features["output_report_variables"]:
            if param in tmp_dict:
                output_report_variables_values = np.append(output_report_variables_values, tmp_dict[param])

        #Append input parameters
        for sensor in self.wn.sensors:
            # Sensor 1
            for input_report_variable in self.wn.stored_data_features["input_report_variables"]:
                # "Pressure", "Demand"
                input_report_variable = input_report_variable.lower()
                output_report_variables_values = np.append(output_report_variables_values, results.node[input_report_variable][sensor])

        np.copyto(dataset_to_fill[index], output_report_variables_values)


    @staticmethod
    def increment_simulation_ID():
        WaterNetworkLeakSimulations._simulation_ID += 1

    def _get_random_output_variables(self) -> Node:
        """
        Returns ID of pipe, Leak Area or Start Time based
        on ther wn.output_report_variables defined by the user

        Intended use:
        >>> self.wn.output_report_variables
        ... ("ID", "Leak Area", "Start Time")
        >>> _leak_node = _get_random_output_variables()
        >>> _ID = _leak_node.name
        >>> _ID
        ... LINK-5
        >>> _leak_node._leak_area
        ... 0.75
        >>> _leak_node._start_time
        ... 13:25
        """
        # get random node to be leak node
        random_pipe_name = np.random.choice(list(self.wn.pipes_ID_and_diameter.keys()))
        random_pipe_obj = self.wn.get_link(random_pipe_name)

        # XXX cant be hardcoded
        leak_area_perc = np.round(np.random.uniform(0, 0.8), 4)
        leak_diameter = np.round(random_pipe_obj.diameter * leak_area_perc, 4)

        # XXX the rounding number also not hardcoded
        leak_area = np.round(np.pi * (leak_diameter / 2) ** 2, 6)

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
        leak_node._leak_start_time = time_of_failure

        return leak_node

        
    
    def run_leak_sim(self):
        #NOTE Description
        _initial_dataset = self._initialize_internal_datasets()

        with open(Path(os.getcwd(), "LeakDetection", "pickle_files", f"simulation_{self._simulation_ID}.pickle"), "wb") as pickleObj:
            pickle.dump(self.wn, pickleObj)

        for simulation_index in range(self.simulations_per_process):

            # FIXME Generator doesnt work after second iteration
            _leak_node = self._get_random_output_variables()
            sim = wntr.sim.WNTRSimulator(self.wn)
            results = sim.run_sim()
            self._arange_dataset_features(_initial_dataset, simulation_index, results, _leak_node)
            




            

