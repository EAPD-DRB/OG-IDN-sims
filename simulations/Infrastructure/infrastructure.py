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
    save_dir = os.path.join(CUR_DIR, "infrastructure")
    base_dir = os.path.join(save_dir, "OUTPUT_BASELINE")
    reform_infr_dir = os.path.join(save_dir, "OUTPUT_REFORM_INFRA")
    reform_mbg_dir = os.path.join(save_dir, "OUTPUT_REFORM_MBG")

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
        .joinpath("ogidn_multisector_default_parameters_MBG.json")
        .open("r") as file
    ):
        defaults = json.load(file)

    p.update_specifications(defaults)

    # Run model
    # start_time = time.time()
    # runner(p, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Run infrastructure increase reform policy
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    p2 = copy.deepcopy(p)
    p2.baseline = False
    p2.output_base = reform_infr_dir

    # Increase in infrastructure spending
    # 1. Temporary increase in housing investment, 1,3% of GDP for 5 years (6,6% of total GDP)
    # 2. Permanent increase in sovereign wealth fund infrastructure investment of 2% of GDP for 5 years
    updated_params_ref = {
        "alpha_I": [0.233, 0.233, 0.233, 0.233, 0.233, 0.20],
    }
    p2.update_specifications(updated_params_ref)

    # Run model
    start_time = time.time()
    # runner(p2, time_path=True, client=client)
    print("run time = ", time.time() - start_time)
    # client.close()

    """
    ---------------------------------------------------------------------------
    Save some results of simulations
    ---------------------------------------------------------------------------
    """
    # base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    # base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    # reform_tpi = safe_read_pickle(
    #     os.path.join(reform_infr_dir, "TPI", "TPI_vars.pkl")
    # )
    # reform_params = safe_read_pickle(
    #     os.path.join(reform_infr_dir, "model_params.pkl")
    # )
    # ans = ot.macro_table(
    #     base_tpi,
    #     base_params,
    #     reform_tpi=reform_tpi,
    #     reform_params=reform_params,
    #     var_list=["Y", "C", "K", "L", "r", "w"],
    #     output_type="pct_diff",
    #     num_years=10,
    #     start_year=base_params.start_year,
    # )

    # # create plots of output
    # op.plot_all(
    #     base_dir,
    #     reform_infr_dir,
    #     os.path.join(reform_infr_dir, "OG-IDN_infr_plots"),
    # )

    # print("Percentage changes in aggregates:", ans)
    # # save percentage change output to csv file
    # ans.to_csv(os.path.join(reform_infr_dir, "OG-IDN_infr_output.csv"))

    """
    ---------------------------------------------------------------------------
    Run nutritious meals program increase reform policy
    ---------------------------------------------------------------------------
    """
    # create new Specifications object for reform simulation
    p3 = copy.deepcopy(p)
    p3.baseline = False
    p3.output_base = reform_mbg_dir

    # Increase in nutritious meals program spending
    # 1. Temporary increase in government spending on free meals program, 0,8% of GDP for 5 years (6,6% of total GDP)
    updated_params_ref = {
        "alpha_T": [0.018, 0.018, 0.018, 0.018, 0.018, 0.01],
    }
    p3.update_specifications(updated_params_ref)

    # Run model
    start_time = time.time()
    runner(p3, time_path=True, client=client)
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
        os.path.join(reform_mbg_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_mbg_dir, "model_params.pkl")
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
    op.plot_all(
        base_dir,
        reform_mbg_dir,
        os.path.join(reform_mbg_dir, "mbg_plots"),
    )

    print("Percentage changes in aggregates:", ans)
    # save percentage change output to csv file
    ans.to_csv(os.path.join(reform_mbg_dir, "mbg_output.csv"))


if __name__ == "__main__":
    # execute only if run as a script
    main()
