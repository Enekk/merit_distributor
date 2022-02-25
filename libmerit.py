from dataclasses import dataclass, field
from math import e as euler, log
import yaml

@dataclass
class Employee:
    """Data Class that defines an employee

    Properties
    ----------
    name : str
        A string that identifies an employee
    cur_salary : float
        The current salary of the employee
    mrp : float
        The 'Market Reference Point' for a job.  If your company does
        not use this, set to the 'middle' (top+bottom/2) of the
        employee's pay band, mrp_top_range to top/middle, and mrp_bottom_range
        to bottom/middle.
    rating : int
        The numeric representation of an employee's performance rating.  If
        your company does not use performance ratings, it is safe to leave
        this at its default. (default 3)
    mrp_top_range : float
        The percent of MRP that defines the top of the pay band.
        If your company does not use MPR, see 'mrp' property's
        description for advice on what to do (default 1.2)
    mpr_bottom_range : float
        The percent of MRP that defines the bottom of the pay band.
        If your company does not use MPR, see 'mrp' property's
        description for advice on what to do (default .8)
    perf_weight : float
        Extra weighting for an employee based on performance.
        Set to 1 for no weighting (default 1)
    min_perc_increase : float
        The minimum required pay increase, as a percentage, for this
        employee (default 0)
    cur_perc_mrp : float
        The current percentage of MRP of the employee's current salary
        This is set programmatically and it is not recommended to set it
        in the constructor.
    _cur_perc_mrp : float
        A private property which enables automatic setting of the
        'cur_perc_mrp' property.
    max_perc_increase : float
        The maximum allowable pay increase, as a percentage, for this
        employee.  By default, this will be set to the top of the pay
        band as defined by 'mrp*mrp_top_range'
    _max_perc_increase : float
        A private property which enables automatic setting of the
        'max_perc_increase' property
    new_salary : float
        The new salary of the employee after adjustments.
        This is automatically set to start at 'cur_salary'
    _new_salary : float
        A private property which enables automatic setting of the
        'cur_salary' property
    rounds : int
        The number of knapsack rounds won by an employee

    Methods
    -------
    knapsack(increase : float) -> float
        Returns the knapsack calculation for a salary increase defined
        as Value(increase)/Cost(increase)
    new_perc_mrp(increase : float = 0) -> float
        Returns the percent of MRP of 'new_salary' property.
    salary_delta() -> float
        Returns the absolute difference between 'new_salary' and
        'cur_salary'
    salary_perc_delta() -> float
        Returns the percent difference between 'new_salary' and
        'cur_salary'
    win_round(division : float, r : int = 1)
         Assign one or more pool divisions to an employee
    """

    name: str
    cur_salary: float
    mrp: float
    rating: int = 3
    mrp_top_range: float = 1.2
    mrp_bottom_range: float = .8
    perf_weight: float = 1
    min_perc_increase: float = 0
    cur_perc_mrp: float
    _cur_perc_mrp: float = field(init=False, repr=False)
    max_perc_increase: float
    _max_perc_increase: float = field(init=False, repr=False)
    new_salary: float
    _new_salary: float = field(init=False, repr=False)
    rounds: int = field(repr=False, default=0)

    @property
    def cur_perc_mrp(self) -> float:
        return self._cur_perc_mrp

    @cur_perc_mrp.setter
    def cur_perc_mrp(self, perc) -> float:
        self._cur_perc_mrp = self._calc_mrp_perc(self.cur_salary)

    @property
    def max_perc_increase(self) -> float:
        return self._max_perc_increase

    @max_perc_increase.setter
    def max_perc_increase(self, perc: float) -> None:
        if type(perc) is property:
            old = float(self.cur_salary)
            new = float(self.mrp_top_range*self.mrp)
            perc = self._percent_change(old, new)
        self._max_perc_increase = perc

    @property
    def new_salary(self) -> float:
        return self._new_salary

    @new_salary.setter
    def new_salary(self, salary: float) -> None:
        if type(salary) is property:
            salary = self.cur_salary
        self._new_salary = salary

    def knapsack(self, increase: float) -> float:
        """ Returns the knapsack calculation for a salary increase defined
            as Value(increase)/Cost(increase)
        """

        return self._calc_value(increase)/self._calc_cost()

    def new_perc_mrp(self, increase: float = 0) -> float:
        """ Returns the percent of MRP of 'new_salary' property.
            Optionally, a proposed increase, 'increase', can be passed to
            calculate the percent of MRP of 'new_salary + increase'
        """
        return self._calc_mrp_perc(self.new_salary + increase)

    def salary_delta(self) -> float:
        """ Returns the absolute difference between 'new_salary' and
            'cur_salary'
        """

        return (self.new_salary - self.cur_salary)

    def salary_perc_delta(self) -> float:
        """ Returns the percent difference between 'new_salary' and
        'cur_salary'
        """

        return self._percent_change(self.cur_salary, self.new_salary)

    def win_round(self, division: float, r: int=1) -> None:
        """ Assign one or more ('r') rounds of size 'division' to an
            Employee and update their 'new_salary' attribute.
        """

        self.new_salary += division*r
        self.rounds += r

    def _calc_cost(self) -> float:
        """ Calculate the cost portion of a knapsack calculation
            this is one of two methods, the other being '_calc_value()'
            that an end user might wish to modify to better meet their
            own situation.

            Cost is defined as the number of rounds (plus one) an
            Employee has won; this slows down runaway winners.
        """

        return (self.rounds+1)

    def _calc_mrp_perc(self, salary: float) -> float:
       return salary/self.mrp

    def _calc_value(self, increase: float) -> float:
        """ Calculate the value portion of a knapsack calculation
            this is one of two methods, the other being '_calc_cost()'
            that an end user might wish to modify to better meet their
            own situation.

            Value is defined as the product of three metrics 1) the
            Employee's performance weighting, 2) how much change to
            MRP a single increase will bring to the Employee and 3) how
            far from the bottom of the pay scale an Employee is.  To
            help boost the effects of factors 2 and 3, an inverse
            natural log is applied to their product before being
            weighted.

            Factor 2 was the original, sole, measure of value, but it
            meant that the lowest paid Employees nearly always won each
            knapsack round, no matter how well positioned they were
            within their pay band.  Factor 3 was introduced to help
            boost Employees that are paid at a higher rate, but are
            lower in their pay bands.
        """

        dist_from_mrp_min = self._calc_mrp_perc(self.new_salary+increase)-self.mrp_bottom_range
        mrp_delta = self._calc_mrp_perc(self.new_salary+increase)-self.new_perc_mrp()
        log_small_vals = log(dist_from_mrp_min*mrp_delta, 1/euler)
        return self.perf_weight*log_small_vals

    def _percent_change(self, old_value: float, new_value: float) -> float:
        return (new_value/old_value - 1)

def load_emps(path: str) -> list:
    """ Load employees from the Employees YAML """

    yam_emps = _load_yaml(path)
    return([_employee_from_dictionary(emp) for emp in yam_emps])

def load_opts(path: str) -> dict:
    """ Initialize default options and then overwrite the defaults with
        opts from the options YAML
    """

    yam_opts = _load_yaml(path)
    def_opts = {'pool': 10000,
                'divisions': 100,
                'perf_translate': {1: 0, 2: 0, 3: 1, 4: 1.5, 5: 2},
                'min_salary_increase': 0.015,
                'bad_performer_gets_min': False}

    def_opts.update({opt: yam_opts[opt] for opt in yam_opts if opt in def_opts})
    return(def_opts)

def _employee_from_dictionary(args: dict) -> Employee:
    """ Generate an Employee object from a dictionary of options """

    initable_options = ['name', 'cur_salary', 'mrp', 'rating', # Required Options
                        'mrp_top_range', 'mrp_bottom_range', 'perf_weight', 'min_perc_increase'] # Optional Options
    kwargs = dict()
    for opt in initable_options:
        if opt in args:
            kwargs[opt] = args[opt]

    return Employee(**kwargs)

def _load_yaml(path: str) -> dict():
    """ Standard Safe Load of a YAML file """

    with open(path) as f:
        try:
            loaded_yaml = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
        return loaded_yaml
