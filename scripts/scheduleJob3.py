# Version 2 combines scheduling and aggregating loads together
# Version 3 uses a for loop to find the cheapest time slot, instead of using the list comprehension

from inputs import no_intervals_day, penalty_coefficient, \
    i_pstart, i_astart, i_estart, i_dur, i_lfinish, i_caf, i_demand, i_bill, i_penalty


def main(household, prices_long, total_penalty):

    loads_household = [0] * no_intervals_day
    for job in household:
        job, loads_household = evaluate_job(job, prices_long, loads_household)
        total_penalty += job[i_penalty]
        # print(job)

    # print(total_penalty)
    # print(loads_household)
    return total_penalty, loads_household


def evaluate_job(job, price_long, loads):
    # t_begin = time()
    load_per_scheduling_period = job[i_demand] / (no_intervals_day / 24.0)
    e_s = job[i_estart]
    p_s = job[i_pstart]
    dur = job[i_dur]
    l_f = job[i_lfinish]
    caf = job[i_caf]

    # if e_s and l_f are NOT in the same day
    if 0 <= e_s <= p_s and p_s + dur - 1 <= l_f <= no_intervals_day - 1:
        price_long = price_long[e_s:l_f + 1]

    else:

        # if e_s is in the previous day and l_f is in the next day
        if e_s > p_s and p_s + dur - 1 > l_f:
            price_long = price_long + price_long + price_long[0: l_f + 1]
        # if e_s is in the previous day or l_f is in the next day
        else:
            price_long = price_long + price_long[0: l_f + 1]

        if e_s > p_s:
            p_s += no_intervals_day - e_s
        else:
            p_s = p_s - e_s

    cost_min = 9999999999
    penalty_min = 9999999999
    bill_min = 0
    actual_start = 0
    for i in xrange(len(price_long) - dur + 1):
        bill = sum(price_long[i: i + dur]) * load_per_scheduling_period
        penalty = abs(i - p_s) * caf * penalty_coefficient
        cost = bill + penalty
        if cost < cost_min:
            # if cost < cost_min or (cost == cost_min and penalty < penalty_min):
            cost_min = cost
            actual_start = i
            bill_min = bill
            penalty_min = penalty

    # job[i_astart] = (actual_start + e_s) % no_periods_day
    actual_start = (actual_start + e_s) % no_intervals_day
    job[i_astart] = actual_start
    job[i_bill] = bill_min
    job[i_penalty] = penalty_min

    # print str(time() - t_begin) + "s"

    # add this load to the aggregate loads
    for i in xrange(dur):
        if actual_start + i > no_intervals_day - 1:
            loads[actual_start + i - no_intervals_day] += load_per_scheduling_period
        else:
            loads[actual_start + i] += load_per_scheduling_period

    return job, loads


