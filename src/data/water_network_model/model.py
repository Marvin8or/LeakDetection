import wntr
from collections import OrderedDict
# class LeakSimulationOptions():
#     pass

class WaterNetworkLeakModel(wntr.network.WaterNetworkModel):
    #NOTE Description
    

    def __init__(self, inp_file_name: str, layout: tuple, number_of_processes: int, user_options=None):
        super().__init__(inp_file_name)
        self.num_precesses = number_of_processes
        self.layout = layout
        self._sensor_node_reg = OrderedDict(((sensor_name, self.nodes._data[sensor_name]) for sensor_name in self.layout))
        self.num_sensors = len(self._sensor_node_reg)
        self.user_options = user_options

        self.options['report']['report_params']["input_report_variables"] = []
        self.options['report']['report_params']["output_report_variables"] = []

        if self.user_options:
            self._set_user_options(self.user_options)

    @property
    def sensors(self):
        #NOTE Description
        return self._sensor_node_reg

    @property
    def report_variables(self):
        #NOTE Description
        return self._report_variables

    def _set_user_options(self, user_options: dict):
        """
        Private method to set the user options by passing a dictionary
        """
        #TODO Extensive tests needed
        for option_type in user_options:
            for option in user_options[option_type]:
                if option_type == 'report':
                    self.options[option_type]['report_params'][option] = user_options[option_type][option]
                else:
                    self.options.__dict__[option_type].__dict__[option] = user_options[option_type][option]

                
                
        
        




    

    
        



