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

        self._report_variables = {"input_report_variables": ("Pressure", "Demand"), 
                                    "output_report_variables": ("ID", "Leak Area", "Start Time")}

    @property
    def sensors(self):
        #NOTE Description
        return self._sensor_node_reg

    @property
    def report_variables(self):
        #NOTE Description
        return self._report_variables


    # NOTE The user can't ommit ID as parameter
    # output_report_options
    # >>> ('ID', 'Leak Area', 'Start Time')
    # >>> ('ID', 'Leak Area')
    # >>> ('ID', 'Start Time')
    # >>> ('ID')
    # >>> ('Leak Area', 'Start Time')
    # ... ('ID', 'Leak Area', 'Start Time')
    def set_report_variables(self, *, input_report_variables: tuple, output_report_variables: tuple):

        if(len(input_report_variables) != 0 and len(output_report_variables) != 0):
            self._report_variables.clear()

            #TODO When input_report_variables has len > 1 guves error

            self._report_variables["input_report_variables"] = tuple([input_report_variables])
            if("ID" not in output_report_variables):
                self._report_variables["output_report_variables"] = ("ID", *output_report_variables)
            else:
                self._report_variables["output_report_variables"] = tuple([*output_report_variables])

        
        




    

    
        



