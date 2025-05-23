# Need to fix references to Calculator, reform json, and substitute new tax
# function call
import multiprocessing
from distributed import Client
import os
import json
import time
import copy
import numpy as np
from importlib.resources import files
import matplotlib.pyplot as plt
from ogidn.calibrate import Calibration
from ogcore.parameters import Specifications
from ogcore import output_tables as ot
from ogcore import output_plots as op
import get_pop_data
import ogcore
from ogcore.execute import runner
from ogcore.utils import safe_read_pickle
from ogcore import demographics as demog


# Use a custom matplotlib style file for plots
plt.style.use("ogcore.OGcorePlots")


def main():
    # Define parameters to use for multiprocessing
    num_workers = min(multiprocessing.cpu_count(), 7)
    client = Client(n_workers=num_workers, threads_per_worker=1)
    print("Number of workers = ", num_workers)

    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(CUR_DIR, "OUTPUT_BASELINE")
    reform_educ_dir = os.path.join(CUR_DIR, "OUTPUT_EDUC")
    reform_hlth_dir = os.path.join(CUR_DIR, "OUTPUT_HEALTH")

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
        .joinpath("ogidn_default_parameters.json")
        .open("r") as file
    ):
        defaults = json.load(file)
    p.update_specifications(defaults)
    un_country_code = "360"
    pop_dict, fert_rates, mort_rates, infmort_rates, imm_rates = (
        get_pop_data.baseline_pop(p, un_country_code=un_country_code)
    )
    p.update_specifications(pop_dict)

    # move closure rule out to 50 years since education phases in over 20 years
    p.tG1 = 50

    # Run model
    # start_time = time.time()
    # runner(p, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Run education spending reform
    ---------------------------------------------------------------------------
    """

    # create new Specifications object for reform simulation
    p2 = copy.deepcopy(p)
    p2.baseline = False
    p2.output_base = reform_educ_dir

    # Increase government spending on education by 0.05% of GDP per year
    updated_params_ref = {
        "alpha_G": [0.1325],  # baseline is 0.132
    }
    p2.update_specifications(updated_params_ref)

    # adjust labor productivity to account for education investment
    # Paper published in Economics and Finance in Indonesia, 2016:
    # https://scholarhub.ui.ac.id/cgi/viewcontent.cgi?params=/context/efi/article/1047/&path_info=EFI_62_283_29_05._20T_20Jasmina_rev2.pdf
    # Finding: 1pp increase in spending (as fraction of GDP) increases test scores by 7.2 points (mean is about 43)
    # Spending is about 0.2 * 0.13 = 0.026 of GDP, so the 1pp increase in spending would be about a 38% increase in spending
    # The test score increase is about 16%
    # no time for paper, but let's assume this increases productivity of those bottom 70% by 16% for all ages 20+
    # Let's assume this phases in linearly over 20 years
    num_years = 20  # 20 years to phase in
    total_benefit = 0.008  # 0.16 * 0.05, total effect on productivity when fully phased in
    benefits = np.linspace(0, total_benefit, num_years)
    for t, benefit in enumerate(benefits):
        p2.e[t, :, :3] = p.e[t, :, :3] * (
            1 + benefit
        )  # just apply to bottom 70%
    p2.e[num_years:, :, :3] = p.e[num_years:, :, :3] * (1 + total_benefit)

    # Run sim with just the benefits of education
    # start_time = time.time()
    # runner(p2, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)

    """
    ---------------------------------------------------------------------------
    Run public health spending reform, separate from education reform
    ---------------------------------------------------------------------------
    """

    # Independently make a new parameters object based off of the baseline
    p3 = copy.deepcopy(p)
    p3.baseline = False
    p3.output_base = reform_hlth_dir
    # Increase gov't spending to account on public health by 2.5% of GDP per
    # year. Baseline is 0.132 or 13.2% of GDP
    p3.alpha_G = (
        p3.alpha_G + 0.025
    )
    p3.RC_SS = 0.0005
    # Assume mortality rates decrease by 1.0%,
    # Assume fertility rates increase by 0.1%
    num_years = 5  # 5 years to phase in
    fert_rates_pctincr = 0.001
    mort_rates_pctdecr = 0.01
    fert_rates_adj = np.vstack(
        (fert_rates, np.zeros((num_years-1, fert_rates.shape[1])))
    )
    mort_rates_adj = np.vstack(
        (mort_rates, np.zeros((num_years-1, mort_rates.shape[1])))
    )
    imm_rates_exp = np.vstack(
        (imm_rates, np.tile(imm_rates[-1, :], (num_years-1, 1)))
    )
    # Add four zero elements at the end of vector infmort_rates
    infmort_rates_adj = np.append(infmort_rates, np.zeros(num_years-1))
    fert_rate_pcts = np.linspace(
        fert_rates_pctincr/(num_years-1), fert_rates_pctincr, num_years-1
    )
    mort_rate_pcts = np.linspace(
        mort_rates_pctdecr/(num_years-1), mort_rates_pctdecr, num_years-1
    )
    for i in range(num_years-1):
        fert_rates_adj[i+2, :] = (
            fert_rates_adj[i+1, :] * (1 + fert_rate_pcts[i])
        )
        mort_rates_adj[i+2, :] = (
            mort_rates_adj[i+1, :] * (1 - mort_rate_pcts[i])
        )
        infmort_rates_adj[i+2] = (
            infmort_rates_adj[i+1] * (1 - mort_rate_pcts[i])
        )

    new_pop_dict = demog.get_pop_objs(
        p3.E,
        p3.S,
        p3.T,
        0,
        99,
        country_id=un_country_code,
        fert_rates=fert_rates_adj,
        mort_rates=mort_rates_adj,
        infmort_rates=infmort_rates_adj,
        imm_rates=imm_rates_exp,
        infer_pop=True,
        pop_dist=None,
        pre_pop_dist=None,
        initial_data_year=p3.start_year,
        final_data_year=p3.start_year + num_years,
        GraphDiag=False
    )
    p3.update_specifications(new_pop_dict)

    # Assume worker productivity increases by 0.5%
    # Let's assume this phases in linearly over 5 years
    total_benefit = 0.005
    benefits = np.linspace(0, total_benefit, num_years)
    for t, benefit in enumerate(benefits):
        p3.e[t, :, :3] = p.e[t, :, :3] * (
            1 + benefit
        )  # just apply to bottom 70%
    p3.e[num_years:, :, :3] = p.e[num_years:, :, :3] * (1 + total_benefit)

    start_time = time.time()
    runner(p3, time_path=True, client=client)
    print("run time = ", time.time() - start_time)

    # p4 = copy.deepcopy(p3)
    # p4.baseline = False
    # p4.output_base = reform_dir3
    # # increase gov't spending to account for costs of education
    # # Spending currently about 2.6% of GDP (source: https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS?locations=ID)
    # # Let's assume this increases to 3.6% of GDP
    # p4.alpha_G = (
    #     p4.alpha_G + 0.04
    # )  # counterfactual 6.6% of GDP - current 2.6% of GDP
    # start_time = time.time()
    # runner(p4, time_path=True, client=client)
    # print("run time = ", time.time() - start_time)
    client.close()

    """
    ---------------------------------------------------------------------------
    Save some results of simulations
    ---------------------------------------------------------------------------
    """
    base_tpi = safe_read_pickle(os.path.join(base_dir, "TPI", "TPI_vars.pkl"))
    base_params = safe_read_pickle(os.path.join(base_dir, "model_params.pkl"))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_hlth_dir, "TPI", "TPI_vars.pkl")
    )
    reform_params = safe_read_pickle(
        os.path.join(reform_hlth_dir, "model_params.pkl")
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
        base_dir, reform_hlth_dir, os.path.join(reform_hlth_dir, "health_plots")
    )

    print("Percentage changes in aggregates:", ans)
    # save percentage change output to csv file
    ans.to_csv(os.path.join(reform_hlth_dir, "health_output.csv"))


if __name__ == "__main__":
    # execute only if run as a script
    main()
