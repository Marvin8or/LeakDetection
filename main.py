
import wntr
from src.data.water_network_model import WaterNetworkLeakModel
from src.data.leak_simulations import WaterNetworkLeakSimulations



if __name__ == "__main__":
    inp_file = 'LeakDetection/networks/Example_1.inp'


    wn = WaterNetworkLeakModel(inp_file, 
                               layout=("JUNCTION-17",
                                       "JUNCTION-21",
                                       "JUNCTION-68",
                                       "JUNCTION-79",
                                       "JUNCTION-122"),
                                number_of_processes=20
                                )
    

    user_report_variables = {"input_report_variables": {"Pressure"},
                             "output_report_variables": {"ID", "Leak Area", "Start Time"}}
    wn.set_report_variables(input_report_variables=("Pressure"), 
                            output_report_variables=("ID", "Leak Area", "Start Time"))

    leak_sim = WaterNetworkLeakSimulations(wn, 10)

    #SensorLayoutResults
    # for sim in range(10):
    results = leak_sim.run_leak_sim()

    results.pressure.to_csv()
    # results.demand
    # results.pressure_demand
    