import time
from typing import Optional
from CSP.Problem import Problem
from CSP.Variable import Variable


class Solver:

    def __init__(self, problem: Problem, use_mrv=False, use_lcv=False, use_forward_check=False):
        self.problem = problem
        self.use_lcv = use_lcv
        self.use_mrv = use_mrv
        self.use_forward_check = use_forward_check

    def is_finished(self) -> bool:
        return all([x.is_satisfied() for x in self.problem.constraints]) and len(
            self.problem.get_unassigned_variables()) == 0

    def solve(self):
        self.problem.calculate_neighbors()
        start = time.time()
        for var in self.problem.variables:
            if not self.forward_check(var):
                print("Problem Unsolvable")
                return
        result = self.backtracking()
        end = time.time()
        time_elapsed = (end - start) * 1000
        if result:
            print(f'Solved after {time_elapsed} ms')
        else:
            print(f'Failed to solve after {time_elapsed} ms')

    def backtracking(self):
        if self.is_finished():
            return True
        var = self.select_unassigned_variable()
        if var is None:
            return False
        for value in self.order_domain_values(var):
            var.value = value
            if self.use_forward_check:
                self.forward_check(var)
            if self.is_consistent(var):
                if self.backtracking():
                    return True
            var.value = None
        return False

    def forward_check(self, var):
        for neighbor in var.neighbors:
            if not neighbor.has_value:
                for value in neighbor.domain:
                    neighbor.value = value
                    consistent = self.is_consistent(neighbor)
                    neighbor.value = None
                    if not consistent:
                        neighbor.domain.remove(value)
                if not neighbor.domain:
                    return False
        return True

    def select_unassigned_variable(self) -> Optional[Variable]:
        if self.use_mrv:
            return self.mrv()
        unassigned_variables = self.problem.get_unassigned_variables()
        return unassigned_variables[0] if unassigned_variables else None

    def order_domain_values(self, var: Variable):
        if self.use_lcv:
            return self.lcv(var)
        return var.domain

    def mrv(self) -> Optional[Variable]:
        unassigned_variables = self.problem.get_unassigned_variables()
        if not unassigned_variables:
            return None
        return min(unassigned_variables, key=lambda var: len(var.domain))

    def is_consistent(self, var: Variable):
        for neighbor in var.neighbors:
            if neighbor.has_value and neighbor.value == var.value:
                return False
        return True

    def lcv(self, var: Variable):
        value_count = {}
        for value in var.domain:
            count = 0
            for neighbor in var.neighbors:
                if not neighbor.has_value and value in neighbor.domain:
                    count += 1
            value_count[value] = count
        sorted_values = sorted(value_count, key=value_count.get)
        return sorted_values

