# %%
import numpy as np
from scipy.optimize import minimize
from ogcore import demographics
from ogcore.parameters import Specifications


def baseline_pop(p, un_country_code="360"):
    """
    Returns objects for the baseline population

    Args:
        p (Specifications): baseline parameters

    Returns:
        dict: population objects
        fert_rates (np.array): fertility rates
        mort_rates (np.array): mortality rates
        infmort_rates (np.array): infant mortality rates
        imm_rates (np.array): immigration rates
    """
    # get initial population objects
    pop_dist, pre_pop_dist = demographics.get_pop(
        p.E,
        p.S,
        0,
        99,
        country_id=un_country_code,
        start_year=p.start_year,
        end_year=p.start_year + 1,
    )
    fert_rates = demographics.get_fert(
        p.E + p.S,
        0,
        99,
        country_id=un_country_code,
        start_year=p.start_year,
        end_year=p.start_year + 1,
        graph=False,
    )
    mort_rates, infmort_rates = demographics.get_mort(
        p.E + p.S,
        0,
        99,
        country_id=un_country_code,
        start_year=p.start_year,
        end_year=p.start_year + 1,
        graph=False,
    )
    imm_rates = demographics.get_imm_rates(
        p.E + p.S,
        0,
        99,
        country_id=un_country_code,
        fert_rates=fert_rates,
        mort_rates=mort_rates,
        infmort_rates=infmort_rates,
        pop_dist=pop_dist,
        start_year=p.start_year,
        end_year=p.start_year + 1,
        graph=False,
    )

    pop_dict = demographics.get_pop_objs(
        p.E,
        p.S,
        p.T,
        0,
        99,
        country_id=un_country_code,
        fert_rates=fert_rates,
        mort_rates=mort_rates,
        infmort_rates=infmort_rates,
        imm_rates=imm_rates,
        infer_pop=True,
        pop_dist=pop_dist[:1, :],
        pre_pop_dist=pre_pop_dist,
        initial_data_year=p.start_year,
        final_data_year=p.start_year+1,
        GraphDiag=False,
    )

    return pop_dict, fert_rates, mort_rates, infmort_rates, imm_rates



def update_pop(
    p,
    fert_rates,
    mort_rates,
    infmort_rates,
    imm_rates,
    un_country_code="360",
    excess_deaths=202_693,
):
    """
    Modify mortality and then get new population objects
    Estimated lives saved per year in South Africa: 202,693
    Source: https://www.cgdev.org/blog/how-many-lives-does-us-foreign-aid-save
    We don't know what ages are affected most from this, so for now just
    assume a proportional increase in mortality rates across all ages"

    Args:
        p (Specifications): baseline parameters
        fert_rates (np.array): fertility rates
        mort_rates (np.array): mortality rates
        infmort_rates (np.array): infant mortality rates
        imm_rates (np.array): immigration rates
        excess_deaths (int): number of excess deaths to achieve

    Returns:
        dict: population objects

    """
    pop_dist, pre_pop_dist = demographics.get_pop(
        p.E,
        p.S,
        0,
        99,
        country_id=un_country_code,
        start_year=p.start_year,
        end_year=p.start_year + 1,
    )

    # use the scipy minimize function to find the scale factor
    scale_factor_guess = 0.01
    res = minimize(
        excess_death_dist,
        scale_factor_guess,
        args=(pop_dist[0, :], mort_rates[0, :], excess_deaths),
    )
    scale_factor = res.x[0]

    # TODO: phase in the change in mort rates over 5 years
    alt_mort_rates = np.minimum(mort_rates * (1 + scale_factor), 1.0)

    pop_dict = demographics.get_pop_objs(
        p.E,
        p.S,
        p.T,
        0,
        99,
        country_id=un_country_code,
        fert_rates=fert_rates,
        mort_rates=alt_mort_rates,
        infmort_rates=infmort_rates,
        imm_rates=imm_rates,
        infer_pop=True,
        pop_dist=pop_dist[:1, :],
        pre_pop_dist=pre_pop_dist,
        initial_data_year=p.start_year,
        final_data_year=p.start_year + 1,
        GraphDiag=False,
    )

    return pop_dict


def excess_death_dist(
    scale_factor, pop_dist, mort_rates, excess_deaths=202_693
):
    """
    Find the scale factor to apply to the mortality rates to achieve the
    desired number of excess deaths.

    Args:
        scale_factor (float): factor to apply to the mortality rates
        pop_dist (np.array): population distribution
        mort_rates (np.array): mortality rates
        excess_deaths (int): number of excess deaths to achieve

    Returns:
        float: distance between predicted excess deaths and desired

    """
    current_deaths = np.sum(pop_dist * mort_rates)
    alt_mort_rates = np.minimum(mort_rates * (1 + scale_factor), 1.0)
    new_deaths = np.sum(pop_dist * alt_mort_rates)
    predicted_execess_deaths = new_deaths - current_deaths
    dist = (predicted_execess_deaths - excess_deaths) ** 2

    return dist


def update_pop(
    p,
    fert_rates,
    mort_rates,
    infmort_rates,
    imm_rates,
    un_country_code="360",
    excess_deaths=202_693,
):
    """
    Modify mortality and then get new population objects
    Estimated lives saved per year in South Africa: 202,693
    Source: https://www.cgdev.org/blog/how-many-lives-does-us-foreign-aid-save
    We don't know what ages are affected most from this, so for now just
    assume a proportional increase in mortality rates across all ages"

    Args:
        p (Specifications): baseline parameters
        fert_rates (np.array): fertility rates
        mort_rates (np.array): mortality rates
        infmort_rates (np.array): infant mortality rates
        imm_rates (np.array): immigration rates
        excess_deaths (int): number of excess deaths to achieve

    Returns:
        dict: population objects

    """
    pop_dist, _ = demographics.get_pop(
        p.E,
        p.S,
        0,
        99,
        country_id=un_country_code,
        start_year=p.start_year,
        end_year=p.start_year + 1,
    )

    # use the scipy minimize function to find the scale factor
    scale_factor_guess = 0.01
    res = minimize(
        excess_death_dist,
        scale_factor_guess,
        args=(pop_dist[0, :], mort_rates[0, :], excess_deaths),
    )
    scale_factor = res.x[0]

    # TODO: phase in the change in mort rates over 5 years
    alt_mort_rates = np.minimum(mort_rates * (1 + scale_factor), 1.0)

    pop_dict = demographics.get_pop_objs(
        p.E,
        p.S,
        p.T,
        0,
        99,
        country_id=un_country_code,
        fert_rates=fert_rates,
        mort_rates=alt_mort_rates,
        infmort_rates=infmort_rates,
        imm_rates=imm_rates,
        infer_pop=True,
        pop_dist=None,
        pre_pop_dist=None,
        initial_data_year=p.start_year,
        final_data_year=p.start_year + 1,
        GraphDiag=False,
    )

    return pop_dict
