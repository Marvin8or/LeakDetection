import os
import multiprocessing as mp
import logging
import pprint

# TODO CLI with click
import click
import logging
from src.data.water_network_model import WaterNetworkLeakModel
from src.data.leak_simulations import WaterNetworkLeakSimulationsBuilder
from src.helpers import JsonFile, general_msg

from pathlib import Path
from datetime import datetime

 
main_logger = logging.getLogger("main")
main_logger.setLevel(logging.INFO)
main_formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
main_file_handler = logging.FileHandler(Path(os.getcwd(), "LeakDetection", "reports", "logs", "main.log"))
main_file_handler.setFormatter(main_formatter)
main_logger.addHandler(main_file_handler)


def main():

    # TODO add to json file
    # INP_FILE = 'LeakDetection/networks/Example_1.inp'
    # INP_FILE =  Path(os.getcwd(), "networks", "Example_1.inp")

    #TODO this must be specified in .sh SLURM file
    NUMBER_OF_PROCESSES = 2
    SIMULATIONS_PER_PROCESS = 5


    main_logger.info("Loading user defined options... ")
    user_options = JsonFile("LeakDetection/dataset_options.json")
    
    main_logger.info("Creating instance of WaterNetworkLeakModel")
    wn = WaterNetworkLeakModel(user_options["INP_FILE"], 
                                number_of_processes=NUMBER_OF_PROCESSES, 
                                user_options=user_options
                                )

    main_logger.info("Creating instance of WaterNetworkLeakSimulationsBuilder")
    leak_sim = WaterNetworkLeakSimulationsBuilder(wn,
                                simulations_per_process=SIMULATIONS_PER_PROCESS,
                                )

    main_logger.info("Running WaterNetworkLeakSimulationsBuilder.run_leak_sim()")
    with mp.Pool(processes=wn.num_processes) as pool:
        pool.starmap(leak_sim.run_leak_sim, 
                     zip([seed*100 for seed in range(wn.num_processes)],
                         [pid for pid in range(wn.num_processes)]))

    main_logger.info("Sending report email.")
    # TODO provide the raw data path -> wn.raw_data_path
    body = f"""Farming finished on {str(datetime.now())}
Dataset saved at location: {wn.raw_data_path}
number_of_processes: {NUMBER_OF_PROCESSES}
simulations_per_process: {SIMULATIONS_PER_PROCESS}
TOTAL NUMBER OF SIMULATIONS: {NUMBER_OF_PROCESSES*SIMULATIONS_PER_PROCESS}
--------------------------------------------------

User defined options:
{pprint.PrettyPrinter(indent=2).pformat(user_options)}

"""
    general_msg(
            sender = "mail1",
            reciever = "mail2",
            password = "psw",
            subject = "Finished farming on BURA",
            body = body)

if __name__ == "__main__":
    main()