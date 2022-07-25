import wntr
from collections import OrderedDict
class WaterNetworkLeakModel(wntr.network.WaterNetworkModel):
    #NOTE Description
    simulations_ID = list()

    def __init__(self, inp_file_name: str, layout: tuple, number_of_processes: int):
        super().__init__(inp_file_name)
        self.number_of_precesses = number_of_processes
        self.layout = layout
        self._sensor_node_reg = OrderedDict(((sensor_name, self.nodes._data[sensor_name]) for sensor_name in self.layout))
        self.number_of_sensors = len(_sensor_node_reg)
        
    @property
    def sensors(self):
        #NOTE Description
        return self._sensor_node_reg
        



