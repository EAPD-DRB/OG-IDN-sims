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
    save_dir = os.path.join(CUR_DIR, "OG-IDN-tau_c")
    base_dir = os.path.join(save_dir, "OUTPUT_BASELINE")
    # reform_dir = os.path.join(save_dir, "OUTPUT_REFORM")
    reform_vat_dir = os.path.join(save_dir, "OUTPUT_REFORM_VAT")
    reform_alloc_dir = os.path.join(save_dir, "OUTPUT_REFORM_ALLOC")

    """
    ---------------------------------------------------------------------------
    Run baseline policy
    ---------------------------------------------------------------------------
    """
    # Set up baseline parameterization
    # p = Specifications(
    #     baseline=True,
    #     num_workers=num_workers,
    #     baseline_dir=base_dir,
    #     output_base=base_dir,
    # )
    # # Update parameters for baseline from default json file
    # with (
    #     files("ogidn")
    #     .joinpath("ogidn_default_parameters_vat.json")
    #     .open("r") as file
    # ):
    #     defaults = json.load(file)
    # p.update_specifications(defaults)
    # # Update parameters from calibrate.py Calibration class
    # if is_connected():  # only update if connected to internet
    #     c = Calibration(p)
    #     updated_params = c.get_dict()
    #     p.update_specifications(updated_params)

    # # Run model
    # start_time = time.time()
    # # runner(p, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Run reform policy 1
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    # p2 = copy.deepcopy(p)
    # p2.baseline = False
    # p2.output_base = reform_vat_dir

    # # Parameter change for the reform run: changes in tau_c in 2025 (1st period and after) by 0.12
    # updated_params_ref = {
    #     "tau_c": [[0.12]],
    # }
    # p2.update_specifications(updated_params_ref)

    # # Run model
    # start_time = time.time()
    # # runner(p2, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)
    # # client.close()  # Keep this open because we want to run another scenario below

    """
    ---------------------------------------------------------------------------
    Save some results of simulations
    ---------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_vat_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_vat_dir, "model_params.pkl")
    )
    # ans = ot.macro_table(
    #     base_tpi,
    #     base_params,
    #     reform_tpi=reform_tpi,
    #     reform_params=reform_params,
    #     var_list=["Y", "C", "K", "L", "r", "w"],
    #     output_type="pct_diff",
    #     num_years=21,
    #     start_year=base_params.start_year,
    # )

    # # create plots of output
    # op.plot_all(
    #     base_dir,
    #     reform_vat_dir,
    #     os.path.join(reform_vat_dir, "OG-IDN_tau_c"),
    # )

    # create a table of the all the TPI results
    all = ot.tp_output_dump_table(
        base_params,
        base_tpi,
        reform_params=reform_params,
        reform_tpi=reform_tpi,
        table_format="csv",
        path=None,
    )
    # save the full results to a csv file
    all.to_csv(os.path.join(reform_vat_dir, "OG-IDN_TAU_C-full.csv"))

    # print("Percentage changes in aggregates:", ans)
    # # save percentage change output to csv file
    # ans.to_csv(os.path.join(reform_vat_dir, "OG-IDN-tau_creform1.csv"))

    """
    ---------------------------------------------------------------------------
    Run reform policy 2
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    # p3 = copy.deepcopy(p)
    # p3.baseline = False
    # p3.output_base = reform_alloc_dir

    # # Parameter change for the reform run: changes in alpha_g in 2025 by 0.15
    # updated_params_ref = {
    #     "budget_balance": False,
    #     "alpha_G": [0.132, 0.15],
    #     "alpha_I": [0.015, 0.010, 0.010, 0.010, 0.010, 0.010, 0.015],
    # }
    # p3.update_specifications(updated_params_ref)

    # # Run model
    # start_time = time.time()
    # runner(p3, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)
    # client.close()  # Close the client after running the last scenario

    """
    ---------------------------------------------------------------------------
    Save some results of simulations
    ---------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_alloc_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_alloc_dir, "model_params.pkl")
    )
    # ans = ot.macro_table(
    #     base_tpi,
    #     base_params,
    #     reform_tpi=reform_tpi,
    #     reform_params=reform_params,
    #     var_list=["Y", "C", "K", "L", "r", "w"],
    #     output_type="pct_diff",
    #     num_years=21,
    #     start_year=base_params.start_year,
    # )

    # # create plots of output
    # op.plot_all(
    #     base_dir,
    #     reform_alloc_dir,
    #     os.path.join(reform_alloc_dir, "OG-IDN-ALLOC"),
    # )

    # print("Percentage changes in aggregates:", ans)
    # # save percentage change output to csv file
    # ans.to_csv(os.path.join(reform_alloc_dir, "OG-IDN_ALLOC_reform.csv"))

    # create a table of the all the TPI results
    all = ot.tp_output_dump_table(
        base_params,
        base_tpi,
        reform_params=reform_params,
        reform_tpi=reform_tpi,
        table_format="csv",
        path=None,
    )
    # save the full results to a csv file
    all.to_csv(os.path.join(reform_alloc_dir, "OG-IDN_ALLOC_full.csv"))


if __name__ == "__main__":
    # execute only if run as a script
    main()
