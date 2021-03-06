# This version finds the next energy level for every period in every iteration

from inputs import no_pricing_periods, next_level_difference
import inputs as P
import pricing as PR


def main(loads_tent, loads_old, prices, penalty, penalty_pre, coe):
    # compute the initial slope
    lookup_base = P.lookup_base
    loads_incr = [lt - lo for lt, lo in zip(loads_tent, loads_old)]
    delta_cost_init = sum([p * d for p, d in zip(prices, loads_incr)])
    delta_penalty_init = penalty - penalty_pre
    slope = delta_cost_init + delta_penalty_init
    # print slope

    loads_fw = loads_old[:]
    prices_fw = prices[:]
    prices_fw_pre = prices[:]

    def eval_incr(p):
        if loads_incr[p] > 0:
            try:
                next_energy = [r[p + 1] * coe for i, r in enumerate(lookup_base) if
                               (r[p + 1] * coe - loads_fw[p]) > next_level_difference and lookup_base[i + 1][0] >
                               prices_fw[p]]
            except IndexError:
                next_energy = []
        else:  # lif loads_incr[p] < 0:
            next_energy = [r[p + 1] * coe for i, r in enumerate(lookup_base) if
                           (loads_fw[p] - r[p + 1] * coe) > next_level_difference and lookup_base[i][0] < prices_fw[p]]
            next_energy.reverse()

        if not next_energy:
            loads_move1 = loads_tent[p] - loads_fw[p]
        else:
            add_on = next_level_difference + 0.000001
            # loads_move1 = next_energy[0] + add_on - loads_fw[p] if loads_incr[p] > 0 \
            #     else next_energy[0] - add_on - loads_fw[p]
            loads_move1 = next_energy[0] - loads_fw[p] if loads_incr[p] > 0 else next_energy[0] - add_on - loads_fw[p]

        return loads_move1

    changed_cost = 0.02
    alpha_current = 0
    alpha_final = 0
    counter_loop = 0
    while slope < 0 and not changed_cost == 0 and alpha_current <= 1:
        alpha_incr_periods = []
        for p in xrange(no_pricing_periods):
            if abs(loads_incr[p]) > 0:
                e_incr = eval_incr(p)
                alpha_incr = float(e_incr) / float(loads_incr[p])
            else:
                alpha_incr = 1
            alpha_incr_periods.append(alpha_incr)
        alpha_incr_min = min(alpha_incr_periods)

        # periods = [p for p in xrange(no_pricing_periods) if alpha_incr_periods[p] == alpha_incr_min]

        alpha_current += alpha_incr_min
        if alpha_current <= 1:
            loads_fw = [l_old + alpha_current * l_incr for l_old, l_incr in zip(loads_old, loads_incr)]
            prices_fw = PR.main(loads_fw, coe)
            changed_cost = sum(
                [(p_fw - p_fw_pre) * l_incr for p_fw, p_fw_pre, l_incr in zip(prices_fw, prices_fw_pre, loads_incr)])
            if not changed_cost == 0:
                slope += changed_cost
                # print slope
                if slope < 0:
                    prices_fw_pre = prices_fw[:]
                    alpha_final = alpha_current
                    counter_loop += 1

    loads_fw = [l_old + alpha_final * l_incr for l_old, l_incr in zip(loads_old, loads_incr)]
    penalty_fw = penalty_pre + alpha_final * delta_penalty_init

    # Loads_fw is the solution that after the slope turns positive
    # I am not sure if I should the keep the solution before or after the slope turns positive
    # Mark has confirmed that it should be before.
    return loads_fw, penalty_fw, alpha_final, counter_loop, prices_fw_pre

    # previous version of eval_incr(p)

    # def eval_incr(p):

    # if loads_incr[p] > 0:
    #     next_energy_levels = [row[p + 1] * coefficient for row in lookup_base if
    #                           (row[p + 1] * coefficient - loads_fw[p]) >= next_level_difference]
    #     if not next_energy_levels or len(next_energy_levels) == 1:
    #         energy_next = loads_tent[p]
    #     else:
    #         energy_next = next_energy_levels[0] + 0.000001
    # else:
    #     next_energy_levels = [row[p + 1] * coefficient for row in lookup_base if
    #                           (loads_fw[p] - row[p + 1] * coefficient) >= next_level_difference]
    #     if not next_energy_levels:
    #         energy_next = loads_tent[p]
    #     else:
    #         energy_next = next_energy_levels[0]
    # return energy_next - loads_fw[p]
