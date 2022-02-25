#! /usr/bin/env python3

from math import ceil
from libmerit import Employee, load_emps, load_opts

def main() -> None:
    """Main execution path of Merit Distributor """

    options_path = './distributor_options.yml'
    employees_path = './employees.yml'

    opts = load_opts(options_path)
    employees = load_emps(employees_path)
            
    # Set minimum and maximum increases based on rankings and
    # user defined preferences.  Also, calculates those increases
    pool_remaining = opts['pool']
    for emp in employees:
        emp.perf_weight = opts['perf_translate'][emp.rating]

        # Set minimum percent increase unless it is set previously
        if not emp.min_perc_increase:
            emp.min_perc_increase = min([
                opts['min_salary_increase'],
                emp.max_perc_increase,
                float('inf') if emp.perf_weight or opts['bad_performer_gets_min'] else 0 ])
        # Set the max increase to the min increase for bad performers;
        # 0% unless bad_performer_gets_min is True
        if not emp.perf_weight:
            emp.max_perc_increase = emp.min_perc_increase

        emp.new_salary = emp.new_salary + emp.new_salary*emp.min_perc_increase
        rounds = ceil(emp.salary_delta()/opts['divisions'])
        emp.rounds += rounds

        pool_remaining -= rounds*opts['divisions']
        if pool_remaining < 0:
            raise Exception(f'Pool of {opts["pool"]} is too small to meet minimum raises for all employees at a minimum salary increase of {opts["min_salary_increase"]}.')

    # Assign remaining pool based on Knapsack sort
    while pool_remaining >= opts['divisions']:
        pool_remaining -= opts['divisions']
        best_pick = -1
        max_knapsack = 0
        for i in range(len(employees)):
            my_ks = employees[i].knapsack(opts['divisions'])
            if my_ks > max_knapsack and employees[i].new_perc_mrp(increase=opts['divisions']) < employees[i].mrp_top_range:
                best_pick = i
                max_knapsack = my_ks
        if best_pick >= 0:
            employees[best_pick].win_round(opts['divisions'])
        else: # No Employee won the sort, return division to pool and stop early
            pool_remaining += ['divisions']
            break

    # Print results
    for emp in employees:
        print(f'{emp.name}: ${emp.cur_salary} -> ${emp.new_salary}, {round(emp.cur_perc_mrp,3)} MRP -> {round(emp.new_perc_mrp(),3)} MRP, a {round(emp.salary_perc_delta()*100,3)}% {"increase" if emp.salary_perc_delta() >= 0 else "decrease"} after {emp.rounds} rounds')
    print(f'Pool Remaining: ${pool_remaining}') if pool_remaining > 0 else None


if __name__ == '__main__':
    main()
