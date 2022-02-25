# Merit Distributor

An attempt to programmatically distribute wage pools to a set of
employees.

## Setup and Running
Define each employees in the `employees.yml` file and set appropriate
options in the `distributor_options.yml` file; both should be in the
root directory of the project.

The following fields, in `employees.yml` are required for each Employee
in the following format:

```yaml
- name: <Name> # Employee's name as a string
  cur_salary: <Salary> # The current salary as a float
  mrp: <MRP> # The MRP* for the employee's pay band as a float
  rating: <Rating> # The employee's performance rating as an int
```

Additional options are detailed in the `_employee_from_dictionary` in
`libmerit.py`.

\* If your company does not use MRP, define the following attributes
for each employee as follows:
* `mrp`: set to the middle (top+bottom/2) of the pay band
* `mrp_top_range`: Set to the top/middle of the pay band
* `mrp_bottom_range`: Set to the bottom/middle of the pay band

Options, found in `distributor_options.yml`, are as follows:

```yaml
pool: <Pool> # Pool of raise money as a float
divisions: 100 # The size of each division of the Knapsack as an int
perf_translate: # Weights for each performance level as a dict
  <Rating>: <Weight> # Translation of one or more ratings to weights
  <Rating>: <Weight> # each defined as int: float
  ...                # Set weights to `1` for each rating to disable
  <Rating>: <Weight> # weighting
min_salary_increase: 0.015 # Optional minimum increase as a float
bad_performer_gets_min: False # Set to True if bad performers (weight `0`)
                              # still get the minimum salary increase
```

Once all options are set and employees are set, run:
`> python3 merit_distributor.py`
