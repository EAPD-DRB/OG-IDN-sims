# Need to fix references to Calculator, reform json, and substitute new tax
# function call
import multiprocessing
from distributed import Client
import os
import json
import time
import copy
from importlib.resources import files
import matplotlib.pyplot as plt
import ogcore
from ogcore.parameters import Specifications
from ogcore import output_tables as ot
from ogcore import output_plots as op
from ogcore.execute import runner
from ogcore.utils import safe_read_pickle, param_dump_json
from ogidn.calibrate import Calibration
from ogidn.utils import is_connected

# Use a custom matplotlib style file for plots
plt.style.use("ogcore.OGcorePlots")


def main():
    # Define parameters to use for multiprocessing
    num_workers = min(multiprocessing.cpu_count(), 7)
    client = Client(n_workers=num_workers, threads_per_worker=1)
    print("Number of workers = ", num_workers)

    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    save_dir = os.path.join(CUR_DIR, "OG-IDN-Taxff")
    base_dir = os.path.join(save_dir, "OUTPUT_BASELINE")
    reform_dir = os.path.join(save_dir, "OUTPUT_REFORM")

    """
    ---------------------------------------------------------------------------
    Run baseline policy
    ---------------------------------------------------------------------------
    """
    # Set up baseline parameterization
    p = Specifications(
        baseline=True,
        num_workers=num_workers,
        baseline_dir=base_dir,
        output_base=base_dir,
    )
    # Update parameters for baseline from default json file
    with (
        files("ogidn")
        .joinpath("ogidn_multisector_default_parameters.json")
        .open("r") as file
    ):
        defaults = json.load(file)
    p.update_specifications(defaults)

    updated_params_ref = {  # order of industries is Agriculture, Mining, manufacturing, utilities, construction, trade&transport, service
        "cit_rate": [[0.22, 0.22, 0.22, 0.22, 0.22, 0.22, 0.22]],
        "Z": [[1, 1, 1, 1, 1, 1, 1]],
        "inv_tax_credit": [[0, 0, 0, 0, 0, 0, 0]],
    }
    p.update_specifications(updated_params_ref)

    # Run model
    start_time = time.time()
    runner(p, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Run reform policy
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    p2 = copy.deepcopy(p)
    p2.baseline = False
    p2.output_base = reform_dir

    # Parameter change for the reform run: corporate income tax rate cut
    updated_params_ref = {  # order of industries is Agriculture, Mining, manufacturing, utilities, construction, trade&transport, service
        "Z": [
            [1.1, 1.05, 1.15, 1.08, 1.07, 1.12, 1.1],
            [1.1, 1.05, 1.15, 1.08, 1.07, 1.12, 1.1],
            [1.1, 1.05, 1.15, 1.08, 1.07, 1.12, 1.1],
            [1.1, 1.05, 1.15, 1.08, 1.07, 1.12, 1.1],
            [1.1, 1.05, 1.15, 1.08, 1.07, 1.12, 1.1],

            [1.12, 1.08, 1.18, 1.1, 1.09, 1.15, 1.13],
            [1.12, 1.08, 1.18, 1.1, 1.09, 1.15, 1.13],
            [1.12, 1.08, 1.18, 1.1, 1.09, 1.15, 1.13],
            [1.12, 1.08, 1.18, 1.1, 1.09, 1.15, 1.13],
            [1.12, 1.08, 1.18, 1.1, 1.09, 1.15, 1.13],

            [1.15, 1.1, 1.2, 1.12, 1.11, 1.18, 1.15],
            [1.15, 1.1, 1.2, 1.12, 1.11, 1.18, 1.15],
            [1.15, 1.1, 1.2, 1.12, 1.11, 1.18, 1.15],
            [1.15, 1.1, 1.2, 1.12, 1.11, 1.18, 1.15],
            [1.15, 1.1, 1.2, 1.12, 1.11, 1.18, 1.15],
        ],
        "cit_rate": [
            [0.27, 0.29, 0.28, 0.26, 0.275, 0.285, 0.25],
            [0.27, 0.29, 0.28, 0.26, 0.275, 0.285, 0.25],
            [0.27, 0.29, 0.28, 0.26, 0.275, 0.285, 0.25],
            [0.27, 0.29, 0.28, 0.26, 0.275, 0.285, 0.25],
            [0.27, 0.29, 0.28, 0.26, 0.275, 0.285, 0.25],

            [0.25, 0.27, 0.26, 0.24, 0.255, 0.265, 0.235],
            [0.25, 0.27, 0.26, 0.24, 0.255, 0.265, 0.235],
            [0.25, 0.27, 0.26, 0.24, 0.255, 0.265, 0.235],
            [0.25, 0.27, 0.26, 0.24, 0.255, 0.265, 0.235],
            [0.25, 0.27, 0.26, 0.24, 0.255, 0.265, 0.235],

            [0.23, 0.25, 0.24, 0.23, 0.235, 0.245, 0.225],
            [0.23, 0.25, 0.24, 0.23, 0.235, 0.245, 0.225],
            [0.23, 0.25, 0.24, 0.23, 0.235, 0.245, 0.225],
            [0.23, 0.25, 0.24, 0.23, 0.235, 0.245, 0.225],
            [0.23, 0.25, 0.24, 0.23, 0.235, 0.245, 0.225],

        ],
        "inv_tax_credit": [
            [0.05, 0.03, 0.04, 0.06, 0.045, 0.035, 0.07],
            [0.05, 0.03, 0.04, 0.06, 0.045, 0.035, 0.07],
            [0.05, 0.03, 0.04, 0.06, 0.045, 0.035, 0.07],
            [0.05, 0.03, 0.04, 0.06, 0.045, 0.035, 0.07],
            [0.05, 0.03, 0.04, 0.06, 0.045, 0.035, 0.07],
            
            [0.07, 0.05, 0.06, 0.08, 0.065, 0.055, 0.085],
            [0.07, 0.05, 0.06, 0.08, 0.065, 0.055, 0.085],
            [0.07, 0.05, 0.06, 0.08, 0.065, 0.055, 0.085],
            [0.07, 0.05, 0.06, 0.08, 0.065, 0.055, 0.085],
            [0.07, 0.05, 0.06, 0.08, 0.065, 0.055, 0.085],

            [0.09, 0.07, 0.08, 0.09, 0.085, 0.075, 0.095],
            [0.09, 0.07, 0.08, 0.09, 0.085, 0.075, 0.095],
            [0.09, 0.07, 0.08, 0.09, 0.085, 0.075, 0.095],
            [0.09, 0.07, 0.08, 0.09, 0.085, 0.075, 0.095],
            [0.09, 0.07, 0.08, 0.09, 0.085, 0.075, 0.095],
        ],
    }
    p2.update_specifications(updated_params_ref)

    # Run model
    start_time = time.time()
    runner(p2, time_path=True, client=client)
    print("run time = ", time.time() - start_time)
    client.close()

    """
    ---------------------------------------------------------------------------
    Save some results of simulations
    ---------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_dir, "model_params.pkl")
    )
    ans = ot.macro_table(
        base_tpi,
        base_params,
        reform_tpi=reform_tpi,
        reform_params=reform_params,
        var_list=["Y", "C", "K", "L", "r", "w"],
        output_type="pct_diff",
        num_years=10,
        start_year=base_params.start_year,
    )

    # create plots of output
    op.plot_all(base_dir, reform_dir, os.path.join(save_dir, "OG-IDN_Taxff"))

    print("Percentage changes in aggregates:", ans)
    # save percentage change output to csv file
    ans.to_csv(os.path.join(save_dir, "OG-IDN_example_Taxff.csv"))


if __name__ == "__main__":
    # execute only if run as a script
    main()
