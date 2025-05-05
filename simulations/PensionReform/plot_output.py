import os
from ogcore.utils import safe_read_pickle
from ogcore import output_tables as ot
from ogcore import output_plots as op
import matplotlib.pyplot as plt

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
save_dir = os.path.join(CUR_DIR, "PensionReform")
base_dir = os.path.join(save_dir, "OUTPUT_BASELINE")
reform_dir = os.path.join(save_dir, "OUTPUT_REFORM")
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

op.plot_gdp_ratio(
    base_tpi=base_tpi,
    base_params=base_params,
    reform_tpi=reform_tpi,
    reform_params=reform_params,
    var_list=['agg_pension_outlays'],  # or change to other vars like ['Y'] depending on what you want to plot
    plot_type='levels',  # can be 'levels' or 'pct_diff'
    num_years_to_plot=50,
    start_year=2025,
    vertical_line_years=[2045],  # you can set e.g., [2035, 2050] if you want lines
    plot_title="Pension to GDP Ratio",
    path=os.path.join(save_dir, "Pension_to_GDP")
)

op.plot_gdp_ratio(
    base_tpi=base_tpi,
    base_params=base_params,
    reform_tpi=reform_tpi,
    reform_params=reform_params,
    var_list=['D'],  # or change to other vars like ['Y'] depending on what you want to plot
    plot_type='levels',  # can be 'levels' or 'pct_diff'
    num_years_to_plot=50,
    start_year=2025,
    vertical_line_years=[2045],  # you can set e.g., [2035, 2050] if you want lines
    plot_title="Debt to GDP Ratio",
    path=os.path.join(save_dir, "Debt_to_GDP")
)

op.plot_aggregates(
    base_tpi=base_tpi,
    base_params=base_params,
    reform_tpi=reform_tpi,
    reform_params=reform_params,
    var_list=['agg_pension_outlays', 'total_tax_revenue'],  # Output, Consumption, Capital, Labor
    plot_type='diff',          # Plot percent differences between baseline and reform
    stationarized=True,            # Plots stationarized values (normalized to remove growth)
    num_years_to_plot=50,
    start_year=2025,
    forecast_data=None,
    forecast_units=None,
    vertical_line_years=None,      # Add [2030, 2040] if you want vertical markers
    plot_title="Differences in Government Pension Expenditure and Revenue",
    path=os.path.join(save_dir, "aggregate_pension")
)

op.tpi_profiles(
    base_tpi=base_tpi,
    base_params=base_params,
    reform_tpi=reform_tpi,
    reform_params=reform_params,
    by_j=False,                        # Disaggregate by ability type j
    var='b_sp1',                          # Variable to plot (e.g., labor supply)
    num_years=5,
    start_year=2025,
    plot_title="Savings by Age",
    path=os.path.join(save_dir, "Savings")
)

op.plot_aggregates(
    base_tpi=base_tpi,
    base_params=base_params,
    reform_tpi=reform_tpi,
    reform_params=reform_params,
    var_list=['I'],  # Output, Consumption, Capital, Labor
    plot_type='pct_diff',          # Plot percent differences between baseline and reform
    stationarized=True,            # Plots stationarized values (normalized to remove growth)
    num_years_to_plot=50,
    start_year=2025,
    forecast_data=None,
    forecast_units=None,
    vertical_line_years=None,      # Add [2030, 2040] if you want vertical markers
    plot_title="Percentage Changes in Investment",
    path=os.path.join(save_dir, "aggregate_investment")
)

