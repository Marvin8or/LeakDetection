import wntr
from collections import OrderedDict
# class LeakSimulationOptions():
#     pass



class WaterNetworkLeakModel(wntr.network.WaterNetworkModel):
    #NOTE Description
    

    def __init__(self, inp_file_name: str, number_of_processes: int, user_options=None):
        super().__init__(inp_file_name)
        self.num_precesses = number_of_processes
        self._sensor_node_reg = OrderedDict()
        self.num_sensors = len(self._sensor_node_reg)
        self._user_options = user_options
        self._stored_data_features = OrderedDict()

        if self._user_options:
            self._set_user_options(self._user_options)

    @property
    def sensors(self):
        #NOTE Description
        return self._sensor_node_reg

    @property
    def user_options(self):
        #NOTE Description
        return self._user_options


    def _set_stored_data_features(self, user_options:dict):
        for _option in user_options["stored_data_features"]:
            self._stored_data_features[_option] = list()
            if "out" in user_options["stored_data_features"][_option] and "ID" not in user_options["stored_data_features"][_option]:
                raise SyntaxError("'ID' must be included as expected output parameter") 
            else:
                if isinstance(user_options["stored_data_features"][_option], str):
                    self._stored_data_features[_option].append(user_options["stored_data_features"][_option])
                elif isinstance(user_options["stored_data_features"][_option], list):
                    self._stored_data_features[_option] += user_options["stored_data_features"][_option]

    def _set_sensors(self, user_options:dict):
        if len(user_options["sensors"]) == 0:
            raise SyntaxError("Sensor locations must be specified!")
        else:
            for _sensor in user_options["sensors"]:
                self._sensor_node_reg[_sensor] = self.nodes._data[_sensor]
                self.num_sensors += 1


    def _set_parent_class_options(self, user_options:dict):
        for _option_type in user_options:
            if _option_type in dict(self.options).keys() and len(user_options[_option_type]) != 0:
                for _option in user_options[_option_type]:
                    self.options.__dict__[_option_type].__dict__[_option] = user_options[_option_type][_option]
            else:
                continue

    def _set_user_options(self, user_options: dict):
        """
        Private method to set the user options by passing a dictionary
        """
        self._set_parent_class_options(user_options)
        self._set_stored_data_features(user_options)
        self._set_sensors(user_options)
        
        




    

    
        



