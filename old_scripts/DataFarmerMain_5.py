import sys
import time
import multiprocessing as mp
import numpy as np
import time
from LeakDetectionLib_5 import (
    simulations_initializer,
    RPT_TMSTP,
    HYD_TMSTP,
    UNCERTAINTY,
    UNCERTAINTY_PARAMETER
)
from pprint import pprint


if __name__ == "__main__":
    
    """
    When running from .sh script first argument is number of simulation per CPU
    Second argument is number of CPUs
    """

    options_dict = {
        "report_timestep": RPT_TMSTP,
        "hydraulic_timestep": HYD_TMSTP,
        "uncertainity_parameter": UNCERTAINTY_PARAMETER,
        "uncertainity_std": UNCERTAINTY,
    }

    pprint(options_dict)

    number_of_simulations = int(sys.argv[1])
    number_of_CPUs = int(sys.argv[2])
    save_frmt = sys.argv[3]
    # number_of_simulations = 3
    # number_of_CPUs = 2
    # save_frmt = "csv"

    simulations_ID = [i for i in range(number_of_CPUs)]
    number_of_simulations_mapping = [
        number_of_simulations for i in range(number_of_CPUs)
    ]
    list_of_seeds = [
        int(np.random.uniform(1, int(time.time()))) for i in range(number_of_CPUs)
    ]
    list_of_formats = [save_frmt for _ in range(number_of_CPUs)]
    pool = mp.Pool(processes=number_of_CPUs)
    pool.starmap(
        simulations_initializer,
        list(zip(number_of_simulations_mapping, simulations_ID, list_of_formats, list_of_seeds)),
    )
    # simulations_initializer(number_of_simulations, simulations_ID[0], list_of_formats[0], list_of_seeds[0])
    start_merge = time.time()

