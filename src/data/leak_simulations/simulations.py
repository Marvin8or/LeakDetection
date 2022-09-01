import os
import pickle
import wntr
import re
from pathlib import Path
import numpy as np

class WaterNetworkLeakSimulations:

    def __init__(self, wn, simulations_per_process: int, simulation_id: int):
        self.wn = wn
        self.simulations_per_process = simulations_per_process
        self.simulation_id = simulation_id
        
        with open(Path(self.wn.pickle_files_path, f"simulation_{simulation_id}.pickle"), "wb") as pickleObj:
            pickle.dump(self.wn, pickleObj)

    def __len__(self):
        return self.simulations_per_process
            
    def __iter__(self):
        return self.WaterNetworkLeakSimulationIterator(self)
            
    def log_results(self, sim_indx, leak_node):
        print("------------------------")
        print(f"Simulation {sim_indx} results...")
        print("------------------------")
        print(f"ID: {leak_node.pipe_name}")
        print(f"A: {leak_node.leak_area}")
        print(f"Start Time: {leak_node.leak_start_time}")
        print("\n")

    def _get_random_output_variables(self):
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
            leak_node.pipe_name = random_pipe_name
            leak_node.leak_start_time = time_of_failure

            return leak_node

    def _add_uncertainty(self, results):
            """
            Private method to add uncertainty to randomly selected junctions in the WND.
            """
            if self.wn.uncertainty == 0:
                return results
                
            junctions = self.wn.junction_name_list
            nodes_and_booleans = {junction: np.random.choice([True, False]) for junction in junctions}
            std_low, std_high = self.wn.uncertainty[0],  self.wn.uncertainty[1]
            
            for input_report_variable in self.wn.stored_data_features["input_report_variables"]:

                input_report_variable = input_report_variable.lower()
                input_report_variable_value_array = results.node[input_report_variable]

                for node in nodes_and_booleans:
                    if nodes_and_booleans[node] and "leak_node" not in node:
                        R_i = np.round(np.random.uniform(low=std_low, high=std_high), 4)
                        input_report_variable_value_array[node] = input_report_variable_value_array[node].apply(lambda D_i: D_i * (R_i + 1))

                results.node[input_report_variable] = input_report_variable_value_array
            return results

    class WaterNetworkLeakSimulationIterator:

        def __init__(self, iterable):
            self.iterable = iterable
            
            self.sim_indx = 0

        def __iter__(self):
            return self
        
        def __next__(self):
            if self.sim_indx < len(self.iterable):

                sim = wntr.sim.WNTRSimulator(self.iterable.wn)
                _leak_node = self.iterable._get_random_output_variables()
                results = sim.run_sim()
                results = self.iterable._add_uncertainty(results)

                results._leak_node = _leak_node
                self.iterable.log_results(self.sim_indx, results._leak_node)
                self.sim_indx += 1
                
                with open(Path(self.iterable.wn.pickle_files_path, f"simulation_{self.iterable.simulation_id}.pickle"), "rb") as pickleObj:
                    self.iterable.wn = pickle.load(pickleObj)

                return results
            else:
                raise StopIteration


class WaterNetworkLeakSimulationsBuilder(wntr.sim.WNTRSimulator):
    #NOTE Description

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

    def _arange_dataset_features(self, dataset_to_fill, index, results) -> None:
        
        # ID, A, ST, ...S1P, ...S1D, ...S2P, ...S2D, ...S3P, ...S3D, ...
        output_report_variables_values = np.array([])

        # ID must always be specified
        _ID = float(re.search(r'\d+', results._leak_node.name).group())

        tmp_dict = {"ID": _ID,
                    "Leak Area": results._leak_node.leak_area,
                    "Start Time": results._leak_node.leak_start_time}

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

    def run_leak_sim(self, seed, simulation_id):
        #NOTE Description

        np.random.seed(seed)
        # warnings.filterwarnings("error")

        _initial_dataset = self._initialize_internal_datasets()
        leak_simulations = WaterNetworkLeakSimulations(self.wn, self.simulations_per_process, simulation_id)

        for indx, simulation_results in enumerate(leak_simulations):
            self._arange_dataset_features(_initial_dataset, indx, simulation_results)

        print(f"Saving dataset with id: {simulation_id}")
        print(f"Size in bytes: {_initial_dataset.nbytes}")
        np.savetxt(Path(self.wn.raw_data_path, f"simulation_{simulation_id}.out"), _initial_dataset, fmt='%.5e')