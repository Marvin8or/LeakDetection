from wntr.epanet import wntr
from src.data.sensor_layout import Sensor

import wntr


if __name__ == "__main__":
    inp_file = 'networks/Example_1.inp'
    wn = wntr.network.WaterNetworkModel(inp_file)
    sim = wntr.sim.WNTRSimulator(wn)
    sensor = Sensor(wn, "JUNCTION-17")
    results = sim.run_sim()
    print(sensor)