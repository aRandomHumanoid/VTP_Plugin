import math
import re

import numpy
from sympy import symbols, sympify


class PrintingStats:
    nozzle_dia = 0.4

    slicing_interval = 0
    layer_height = 0
    layer_width = 0
    extruder_num = 0

    alpha = 0
    fil_area = 0
    thread_area = 0
    e_dot = 0

    z_offset = -0.5

    V_star_functions = []
    H_star_functions = []

    def __init__(self, lines, path, alpha, nozzle_dia, fil_dia, e_dot):
        for line in lines:
            if "; layer_height = " in line:
                self.layer_height = float(re.search(r'\d+(?:\.\d+)?', line).group())
            if ";layer_height = " in line:
                self.layer_width = float(re.search(r'\d+(?:\.\d+)?', line).group())
        self.fill_functions(path)
        self.alpha = alpha
        self.fil_area = 3.1415 * ((fil_dia / 2) ** 2)
        self.thread_area = 3.1415 * ((alpha * nozzle_dia / 2) ** 2)
        self.e_dot = e_dot

    def fill_functions(self, path):
        with open(path, 'r') as infile:
            lines = infile.readlines()
        for line in lines:
            subline = line.split(";")
            self.V_star_functions.append(subline[0])
            self.H_star_functions.append(subline[1])

    def make_function_list(self, function_list, output_function_list):
        for function_string in function_list:
            output_function_list.append(sympify(function_string))

    def debug_vars(self, x_start, x_end, y_start, y_end, z_end, n):
        length = math.dist((x_start, y_start), (x_end, y_end))
        x_mid = (x_start + x_end) / 2
        y_mid = (y_start + y_end) / 2

        V_star = self.V_star_functions[n].evalf(subs={'x': x_mid, 'y': y_mid, 'z': z_end})
        H_star = self.H_star_functions[n].evalf(subs={'x': x_mid, 'y': y_mid, 'z': z_end})

        H_new = H_star * self.alpha * self.nozzle_dia

        f_new = self.e_dot * V_star * self.fil_area / self.thread_area
        e_new = length * self.e_dot / f_new
        z_new = z_end + H_new - self.layer_height
        return V_star, H_star, self.e_dot, H_new, f_new, e_new, z_new

    def evaluate_z_at_point(self, x, y, z, n):
        _, H_star = self.eval_funcs(x, y, z, n)
        H_new = H_star * self.alpha * self.nozzle_dia
        z_new = z + H_new - self.layer_height + self.z_offset
        return z_new


    def evaluate_vars(self, x_start, x_end, y_start, y_end, z_end, n):
        length = math.dist((x_start, y_start), (x_end, y_end))
        x_mid = (x_start + x_end) / 2
        y_mid = (y_start + y_end) / 2

        V_star, H_star = self.eval_funcs(x_mid, y_mid, z_end, n)

        H_new = H_star * self.alpha * self.nozzle_dia

        f_new = self.e_dot * V_star * self.fil_area / self.thread_area
        e_new = length * self.e_dot / f_new
        z_new = z_end + H_new - self.layer_height + self.z_offset

        return z_new, e_new, f_new,

    def eval_funcs(self, x, y, z, n):
        V_star = 0.1 + 0.003*(x-100) + 0.003*(y-100) + 0.003*z
        H_star = 6
        return V_star, H_star