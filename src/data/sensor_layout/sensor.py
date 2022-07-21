import wntr

class Sensor(wntr.network.base.Node):
    
    def __init__(self, wn, name):
        super().__init__(wn, name)

    

    

    # def get_sensor_pressure(self):
    #     sensor_pressures_all_time = self.results.node["pressure"].loc[:, self.node_id]
    #     return sensor_pressures_all_time

    # def get_sensor_demand(self):
    #     sensor_demand_all_time = self.results.node["demand"].loc[:, self.node_id]
    #     return sensor_demand_all_time

    # def get_all_values(self):
    #     sp = self.get_sensor_pressure()
    #     sd = self.get_sensor_demand()
    #     all_sensor_values = pd.DataFrame(data=[sp, sd], index=["p", "Q"]).T
    #     return all_sensor_values

    # def get_all_times(self):
    #     times = self.get_sensor_pressure().index
    #     return times