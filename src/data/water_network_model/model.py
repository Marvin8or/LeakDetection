import wntr
from collections import OrderedDict
# class LeakSimulationOptions():
#     pass

class WaterNetworkLeakModel(wntr.network.WaterNetworkModel):
    #NOTE Description
    

    def __init__(self, inp_file_name: str, layout: tuple, number_of_processes: int):
        super().__init__(inp_file_name)
        self.num_precesses = number_of_processes
        self.layout = layout
        self._sensor_node_reg = OrderedDict(((sensor_name, self.nodes._data[sensor_name]) for sensor_name in self.layout))
        self.num_sensors = len(self._sensor_node_reg)
        self._report_options = {"input_report_options": ("Pressure", "Demand"), 
                                           "output_report_options": ("ID", "Leak Area", "Start Time")}

    @property
    def sensors(self):
        #NOTE Description
        return self._sensor_node_reg

    @property
    def report_options(self):
        #NOTE Description
        return self._report_options

    def set_report_options(self, *, input_report_options: tuple, output_report_options: tuple):

        if(len(input_report_options) != 0 and len(output_report_options) != 0):
            self._report_options.clear()
            self._report_options["input_report_options"] = input_report_options
            self._report_options["output_report_options"] = output_report_options

        
        




    

    
        



