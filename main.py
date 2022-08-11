from src.data.water_network_model import WaterNetworkLeakModel
from src.data.leak_simulations import WaterNetworkLeakSimulations



if __name__ == "__main__":
    inp_file = 'LeakDetection/networks/Example_1.inp'

    user_options = {
    "sensors": ["JUNCTION-17", "JUNCTION-21", "JUNCTION-68", "JUNCTION-79", "JUNCTION-122"],

    "stored_data_features": {               
        "input_report_variables": ["Pressure", "Demand"],
        "output_report_variables": ["ID", "Leak Area", "Start Time"]
                },
    
    "time": {                    
        "duration": 24 * 3600, 
        "hydraulic_timestep": 60 * 60,
        "report_timestep": 60 * 60
            },

    "hydraulic": {
        "demand_model": "PDD",
        "required_pressure": 15.0,
        "minimum_pressure": 0.0
                    }
        }

    wn = WaterNetworkLeakModel(inp_file, 
                                number_of_processes=20,
                                user_options=user_options
                                )
    

    leak_sim = WaterNetworkLeakSimulations(wn, 
                                simulations_per_process=10
                                )

    #SensorLayoutResults
    results = leak_sim.run_leak_sim()

    results.pressure.to_csv()
    # results.demand
    # results.pressure_demand
    