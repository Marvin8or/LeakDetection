import wntr
import os
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

_DEFAULT_USER_OPTIONS = {

    "sensors": ["JUNCTION-17", "JUNCTION-21", "JUNCTION-68", "JUNCTION-79", "JUNCTION-122"],

    "stored_data_features": {               
        "input_report_variables": ["Pressure", "Demand"],
        "output_report_variables": ["ID", "Leak Area", "Start Time"]
                },
    "uncertainty": 0
}

def dispatch_user_options(fn):

    registry = {}
    
    if len(registry) == 0:
        registry[fn.__name__] = fn
        
    def register(fn):
        registry[fn.__name__] = fn
        return fn
    
    def set_all(self, user_options):

        if not user_options:
            user_options = _DEFAULT_USER_OPTIONS

        for f in registry.values():
            f(self, user_options)
        
    set_all.register = register
    
    return set_all

def dataset_dir_naming(user_options):

    stored_data_features_abrev = {"input_report_variables": {"Pressure": "P", 
                                                             "Demand": "D"},
                                  "output_report_variables": {"ID": "ID",
                                                              "Leak Area": "A",
                                                              "Start Time": "ST"}}


    directory_name = """"""

    directory_name += datetime.now().date().strftime("%Y%m%d")

    directory_name += "_"

    if "uncertainty" in user_options:
        directory_name += str(user_options["uncertainty"][1])

    directory_name += "_"

    for report_variables in user_options["stored_data_features"]["input_report_variables"]:
        directory_name += stored_data_features_abrev["input_report_variables"][report_variables]

    directory_name += "_"

    for report_variables in user_options["stored_data_features"]["output_report_variables"]:
        directory_name += stored_data_features_abrev["output_report_variables"][report_variables]

    return directory_name
    

class WaterNetworkLeakModel(wntr.network.WaterNetworkModel):
    #NOTE Description

    def __init__(self, inp_file_name: str, number_of_processes: int, user_options=None):

        super().__init__(inp_file_name)
        self.num_processes = number_of_processes
        self._sensor_node_reg = OrderedDict()
        self.num_sensors = len(self._sensor_node_reg)
        self._user_options = user_options
        self._stored_data_features = OrderedDict()
        self._pipes_ID_and_diameter = {link_name: np.round(self.get_link(link_name).diameter, 4) for link_name in self.links.pipe_names}

        self._pickle_files_path = Path(os.getcwd(), "LeakDetection", "pickle_files")

        self._set_options(self._user_options)

        # TODO Create directory with specific name so they can be differentiated
        # 'date_uncertainty_input_report_variables_output_report_variables'
        # '9122022_0.05_P_IDAST' or '2022912_0.1_PQ_IDA'
        # TODO copy the user code json to that directory
        self.directory_name = dataset_dir_naming(self._user_options)
        self._raw_data_path = Path(os.getcwd(), "LeakDetection", "data", "raw", self.directory_name)

        if self._raw_data_path.exists():
            raise IsADirectoryError(f"Directory {self.directory_name} already exists!")
        else:
            self._raw_data_path.mkdir()


    @property
    def sensors(self):
        #NOTE Description
        return self._sensor_node_reg

    @property
    def user_options(self):
        #NOTE Description
        return self._user_options

    @property
    def stored_data_features(self):
        #NOTE Description
        return self._stored_data_features

    @property
    def pipes_ID_and_diameter(self):
        #NOTE Description
        return self._pipes_ID_and_diameter

    @property
    def uncertainty(self):
        #NOTE Description
        return self._uncertainty

    @property
    def pickle_files_path(self):
        #NOTE Description
        return self._pickle_files_path

    @property
    def raw_data_path(self):
        #NOTE Description
        return self._raw_data_path
        
    @dispatch_user_options
    def _set_options(self, user_options: dict):
        for _option_type in user_options:
            if _option_type in dict(self.options).keys() and len(user_options[_option_type]) != 0:
                for _option in user_options[_option_type]:
                    self.options.__dict__[_option_type].__dict__[_option] = user_options[_option_type][_option]

    @_set_options.register
    def _set_stored_data_features(self, user_options: dict):
        for _option in user_options["stored_data_features"]:
            self._stored_data_features[_option] = list()
            if "out" in user_options["stored_data_features"][_option] and "ID" not in user_options["stored_data_features"][_option]:
                raise SyntaxError("'ID' must be included as expected output parameter") 
            else:
                if isinstance(user_options["stored_data_features"][_option], str):
                    self._stored_data_features[_option].append(user_options["stored_data_features"][_option])
                elif isinstance(user_options["stored_data_features"][_option], list):
                    self._stored_data_features[_option] += user_options["stored_data_features"][_option]

    @_set_options.register
    def _set_uncertainty(self, user_options: dict):
        if "uncertainty" in user_options and user_options["uncertainty"] != 0:

            if isinstance(user_options["uncertainty"], list):
                self._uncertainty = user_options["uncertainty"]

            elif isinstance(user_options["uncertainty"], float):
                if user_options["uncertainty"] > 0:
                    self._uncertainty = user_options["uncertainty"] = [-float(user_options["uncertainty"]), float(user_options["uncertainty"])]
                else:
                    self._uncertainty = user_options["uncertainty"] = [float(user_options["uncertainty"]), float(user_options["uncertainty"] * -1)]

            elif isinstance(user_options["uncertainty"], int):
                user_options["uncertainty"] = user_options["uncertainty"]/100
                if user_options["uncertainty"] > 0:
                    self._uncertainty = user_options["uncertainty"] = [-float(user_options["uncertainty"]), float(user_options["uncertainty"])]
                else:
                    self._uncertainty = user_options["uncertainty"] = [float(user_options["uncertainty"]), float(user_options["uncertainty"] * -1)]

        else:
            self._uncertainty = user_options["uncertainty"]

    @_set_options.register
    def _set_sensors(self, user_options: dict):
        if len(user_options["sensors"]) == 0:
            raise SyntaxError("Sensor locations must be specified!")
        else:
            for _sensor in user_options["sensors"]:
                self._sensor_node_reg[_sensor] = self.nodes._data[_sensor]
                self.num_sensors += 1

__all__ = ["WaterNetworkLeakModel"]