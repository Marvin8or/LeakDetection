import wntr
import pickle
import os
import time
import numpy as np
import pandas as pd
from numpy import random
from pathlib import Path
from scipy.stats import truncnorm


"""
CURRENT VARIABLES:

 # Network 1 A sensor placement

simulations_initializer
> report_timestep = 3600
> hydraulic_timestep = 3600

add_uncertainty
> Added uncertainity to PD
> uncertainity_std = +-0.1

"""


RPT_TMSTP = 300
HYD_TMSTP = 300
UNCERTAINTY_PARAMETER = "P"
UNCERTAINTY = 0.1

def get_truncated_normal(mean=0.4, sd=0.1, low=0.0, upp=1.0):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

class Sensor:
    def __init__(self, node_id, results):
        self.node_id = node_id
        self.results = results

    def get_sensor_pressure(self):
        sensor_pressures_all_time = self.results.node["pressure"].loc[:, self.node_id]
        return sensor_pressures_all_time

    def get_sensor_demand(self):
        sensor_demand_all_time = self.results.node["demand"].loc[:, self.node_id]
        return sensor_demand_all_time

    def get_all_values(self):
        sp = self.get_sensor_pressure()
        sd = self.get_sensor_demand()
        all_sensor_values = pd.DataFrame(data=[sp, sd], index=["p", "Q"]).T
        return all_sensor_values

    def get_all_times(self):
        times = self.get_sensor_pressure().index
        return times


class Layout:
    def __init__(self, *sensor_list):
        self.sensor_list = list(sensor_list)
        self.number_of_sensors = len(self.sensor_list)
        self.names = [s.node_id for s in self.sensor_list]

    def get_times(self):
        return self.sensor_list[0].get_all_times()

    def add_sensor(self, sensor):
        self.sensor_list.append(sensor)
        self.number_of_sensors += 1
        self.names.append(sensor.node_id)

    def get_layout_pressure(self):
        self.p = np.array([s.get_sensor_pressure() for s in self.sensor_list]).T
        layout_pressure = pd.DataFrame(
            data=self.p, index=self.get_times(), columns=self.names
        )
        return layout_pressure

    def get_layout_demand(self):
        self.d = np.array([s.get_sensor_demand() for s in self.sensor_list]).T
        layout_demand = pd.DataFrame(
            data=self.d, index=self.get_times(), columns=self.names
        )
        return layout_demand

    def get_all_layout_values(self):
        names = list()
        for self.s in self.sensor_list:
            names.append(self.s.node_id + "_p")
            names.append(self.s.node_id + "_Q")

        data = list()
        for s in self.sensor_list:
            data.append(s.get_sensor_pressure())
            data.append(s.get_sensor_demand())

        data = np.array(data).T

        all_layout_values = pd.DataFrame(
            data=data, index=self.get_times(), columns=names
        )
        return all_layout_values


class Simulations:

    Simulations_ID = 0

    def __init__(self, *layout, inp_file):

        self.layout = list(layout)
        self.inp_file = inp_file
        self.wn = wntr.network.WaterNetworkModel(self.inp_file)
        self.wn.options.time.duration = 24 * 3600
        self.wn.options.time.hydraulic_timestep = 5 * 60
        self.wn.options.time.report_timestep = 5 * 60
        self.wn.options.hydraulic.demand_model = "PDD"
        self.wn.options.hydraulic.required_pressure = 15 # m H2O
        self.wn.options.hydraulic.minimum_pressure = 0
        # self.wn.options.hydraulic.trials = 200
        # self.wn.options.hydraulic.accuracy = 0.01

    def set_up_options(self, **kwargs):

        """
        duration - duration of simulations in hours [h]
        hydraulic_timestep(minutes) - timestep that controls the simulation
        report_timestep(minutes) - reporting timestep
        demand_model - pressure dependent demand driven simulation (PDD)

        """

        if "inp_file" in kwargs:
            self.inp_file = kwargs["inp_file"]

        if "duration" in kwargs:
            self.wn.options.time.duration = kwargs["duration"]

        if "hydraulic_timestep" in kwargs:
            self.wn.options.time.hydraulic_timestep = kwargs["hydraulic_timestep"]

        if "report_timestep" in kwargs:
            self.wn.options.time.report_timestep = kwargs["report_timestep"]

        if "required_pressure" in kwargs:
            self.wn.options.hydraulic.required_pressure = kwargs["required_pressure"]

        if "minimum_pressure" in kwargs:
            self.wn.options.hydraulic.minimum_pressure = kwargs["minimum_pressure"]

        if "demand_model" in kwargs:
            self.wn.options.hydraulic.demand_model = kwargs["demand_model"]

    def plot_network(self):
        wntr.graphics.plot_network(self.wn, title=self.wn.name)

    def random_choice_of_output_variables(self):

        """
        Random choice of pipe to fail (ID)
        Random choice of percentage of diameter of pipe to represent leak (A)
        Random choice of Cd koeficient with get_trunc_norm function (Cd)
        Random choice of time of leak occurance (start time)
        """

        pipe_diameters = self.wn.query_link_attribute(
            "diameter", link_type=wntr.network.Pipe
        )
        pipe_to_fail = np.random.choice(pipe_diameters.index, 1, replace=False)[0]
        pipe = self.wn.get_link(pipe_to_fail)

        # TODO condition to decide dimension of leak

        A_perc = np.round(np.random.uniform(0.1, 1), 4)
        leak_diameter = pipe.diameter * A_perc
        
        leak_area = np.round(3.14 * (leak_diameter / 2) ** 2, 6)

        self.wn = wntr.morph.split_pipe(
            self.wn, pipe_to_fail, pipe_to_fail + "_B", pipe_to_fail + "_leak_node"
        )

        Cd = np.round(np.random.uniform(0.1, 1), 4)
        duration = self.wn.options.time.duration
        time_of_failure = np.round(np.random.uniform(0, duration / 3600, 1)[0], 4)

        leak_node = self.wn.get_node(pipe_to_fail + "_leak_node")
        leak_node.add_leak(
            self.wn,
            area=leak_area,
            discharge_coeff=Cd,
            start_time=time_of_failure * 3600,
        )

        return pipe.name, leak_area, Cd, time_of_failure

    @staticmethod
    def increment_simulations_ID():
        Simulations.Simulations_ID += 1

    def add_uncertainty(
        self,
        results,
        std_low,
        std_high,
        add_uncertainty_to,
    ):

        junctions = self.wn.junction_name_list

        # TODO add bias favoring True bool
        nodes_and_booleans = {
            junction: random.choice([True, False]) for junction in junctions
        }

        if add_uncertainty_to == "D":
            demand = results.node["demand"]

            for key in nodes_and_booleans.keys():
                if nodes_and_booleans[key] == True:
                    R_i = np.round(np.random.uniform(low=std_low, high=std_high), 4)
                    demand[key] = demand[key].apply(lambda D_i: D_i * (R_i + 1))

            results.node["demand"] = demand

        if add_uncertainty_to == "P":
            pressure = results.node["pressure"]
            for key in nodes_and_booleans:
                if nodes_and_booleans[key] == True:
                    R_i = np.round(np.random.uniform(low=std_low, high=std_high), 4)
                    pressure[key] = pressure[key].apply(lambda D_i: D_i * (R_i + 1))

            results.node["pressure"] = pressure

        if add_uncertainty_to == "PD":
            demand = results.node["demand"]
            pressure = results.node["pressure"]
            for key in nodes_and_booleans.keys():
                if nodes_and_booleans[key] == True:
                    R_i = np.round(np.random.uniform(low=std_low, high=std_high), 4)
                    demand[key] = demand[key].apply(lambda D_i: D_i * (R_i + 1))
                    pressure[key] = pressure[key].apply(lambda D_i: D_i * (R_i + 1))

            results.node["demand"] = demand
            results.node["pressure"] = pressure

        return results

    def run(self, number_of_simulations, seed, save_results, save_to_format,):

        np.random.seed(seed)

        if save_results == "PD":
            columns = int(
                2
                * len(self.layout)
                * (
                    self.wn.options.time.duration / self.wn.options.time.report_timestep
                    + 1
                )
            )
        else:
            columns = int(
                len(self.layout)
                * (
                    self.wn.options.time.duration / self.wn.options.time.report_timestep
                    + 1
                )
            )

        with open(
            Path(os.getcwd(), "pickle_files", f"wn_{self.Simulations_ID}.pickle"), "wb"
        ) as pickleObj:
            pickle.dump(self.wn, pickleObj)

        input_of_simulations = np.empty((number_of_simulations, columns))
        output_of_simulations = list()

        simulation_number = 0
        simulation_indx = -1

        while simulation_number < number_of_simulations:

            _ID, _A, _CD, _ST = self.random_choice_of_output_variables()

            sim = wntr.sim.WNTRSimulator(self.wn)

            try:
                results = sim.run_sim()
                simulation_indx += 1

            except RuntimeError or UserWarning:
                print("RuntimeError occured: continuing...")
                with open(
                    Path(
                        os.getcwd(), "pickle_files", f"wn_{self.Simulations_ID}.pickle"
                    ),
                    "rb",
                ) as pickleObj:
                    self.wn = pickle.load(pickleObj)

                continue

            else:

                print("------------------------")
                print(f"Results of {simulation_number+1}. simulation ")
                print("-------------------------")
                print(f"ID: {_ID}")
                print(f"A: {_A}")
                print(f"Cd: {_CD}")
                print(f"ST: {_ST}")
                print("\n")

                results = self.add_uncertainty(results, 
                                               std_low=-UNCERTAINTY,
                                               std_high=UNCERTAINTY,
                                               add_uncertainty_to=UNCERTAINTY_PARAMETER)

                l = Layout()
                for sensor in self.layout:
                    l.add_sensor(Sensor(sensor, results))

                output_row = np.hstack([_ID, _A, _CD, _ST])
                output_of_simulations.append(output_row)
                times = l.get_times()

                sensor_value = list()
                sensor_value_time = list()
                for s in l.sensor_list:
                    if save_results == 'PD':
                        sensor_value.append(s.node_id + "_p")
                        sensor_value.append(s.node_id + "_Q")
                    if save_results == 'P':
                        sensor_value.append(s.node_id + "_p")
                    if save_results == 'D':
                        sensor_value.append(s.node_id + "_Q")

                sensor_value_time = []
                for t in times:
                    for n in sensor_value:
                        sensor_value_time.append(n + f"_{t}")

                if save_results == "PD":
                    all_layout_values_ravel = np.ravel(l.get_all_layout_values())
                    input_of_simulations[simulation_indx, :] = all_layout_values_ravel

                if save_results == "P":
                    layout_pressure_ravel = np.ravel(l.get_layout_pressure())
                    input_of_simulations[simulation_indx, :] = layout_pressure_ravel

                if save_results == "D":
                    layout_demand_ravel = np.ravel(l.get_layout_demand())
                    input_of_simulations[simulation_indx, :] = layout_demand_ravel

                with open(
                    Path(
                        os.getcwd(), "pickle_files", f"wn_{self.Simulations_ID}.pickle"
                    ),
                    "rb",
                ) as pickleObj:
                    self.wn = pickle.load(pickleObj)

                self.wn.reset_initial_values()
                simulation_number += 1

        index = [f"sim_{i+1}" for i in range(number_of_simulations)]
        D_input = pd.DataFrame(
            data=input_of_simulations, index=index, columns=sensor_value_time
        )
        D_output = pd.DataFrame(
            data=output_of_simulations,
            index=index,
            columns=["ID", "A", "Cd", "start_time"],
        )
        D_input_output_press = pd.concat([D_output, D_input], axis=1)
        
        if save_to_format == "csv":
            Path(os.getcwd(), f"input_output_data_{UNCERTAINTY}_{UNCERTAINTY_PARAMETER}").mkdir(parents=True, exist_ok=True)
            D_input_output_press.to_csv(Path(f'input_output_data_{UNCERTAINTY}_{UNCERTAINTY_PARAMETER}', f'input_output{self.Simulations_ID}.csv'))

def simulations_initializer(number_of_simulations, simulations_ID, format, seed):

    inp_file = Path(os.getcwd(), "networks", "Example_1.inp")

    simulations_instance = Simulations(
        "JUNCTION-17",
        "JUNCTION-21",
        "JUNCTION-68",
        "JUNCTION-79",
        "JUNCTION-122",
        inp_file=inp_file,
    )

    simulations_instance.Simulations_ID = simulations_ID
    simulations_instance.set_up_options(
        report_timestep=RPT_TMSTP, hydraulic_timestep=HYD_TMSTP
    )
    start = time.time()
    simulations_instance.run(
        number_of_simulations=number_of_simulations, 
        seed=seed, 
        save_results=UNCERTAINTY_PARAMETER,
        save_to_format=format
    )

    diff_time = time.time() - start
    print("=====================================")
    print("ELAPSED TIME SIMULATIONS: ", diff_time)
    print("=====================================")

