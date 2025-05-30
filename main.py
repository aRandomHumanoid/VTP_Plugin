# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (c) [2025] [Roman Tenger]
import math
import re
import logging
import os
import argparse
import tkinter as tk

# Vars: the important ones
global V_STAR, H_STAR, H, E_DOT, ALPHA, FIL_AREA, THREAD_AREA



def gui():
    def on_submit():
        global V_STAR,H_STAR,E_DOT
        V_STAR = float(entry1.get())
        H_STAR = float(entry2.get())
        E_DOT = float(entry3.get())
        root.destroy()  # Closes the window after submit

    root = tk.Tk()
    root.title("Inputs")
    root.geometry("200x300")

    # Labels
    tk.Label(root, text="Enter V_star:").pack()
    entry1 = tk.Entry(root)
    entry1.pack()

    tk.Label(root, text="Enter H_star:").pack()
    entry2 = tk.Entry(root)
    entry2.pack()

    tk.Label(root, text="Enter E_dot:").pack()
    entry3 = tk.Entry(root)
    entry3.pack()

    # Submit Button
    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack()

    root.mainloop()

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging to save in the script's directory
log_file_path = os.path.join(script_dir, "vtp_plugin.txt")
logging.basicConfig(
    filename=log_file_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def get_line_values(line):
    x_match = re.search(r'X\d+(?:\.\d+)?', line)
    y_match = re.search(r'Y\d+(?:\.\d+)?', line)
    z_match = re.search(r'Z\d+(?:\.\d+)?', line)
    e_match = re.search(r'E\d+(?:\.\d+)?', line)
    f_match = re.search(r'F\d+(?:\.\d+)?', line)
    ret = []
    if x_match is not None:
        ret.append(float(x_match.group().removeprefix("X")))
    else:
        ret.append(None)
    if y_match is not None:
        ret.append(float(y_match.group().removeprefix("Y")))
    else:
        ret.append(None)
    if z_match is not None:
        ret.append(float(z_match.group().removeprefix("Z")))
    else:
        ret.append(None)
    if e_match is not None:
        ret.append(float(e_match.group().removeprefix("E")))
    else:
        ret.append(None)
    if f_match is not None:
        ret.append(float(f_match.group().removeprefix("F")))
    else:
        ret.append(None)
    return ret

def process_gcode(input_file):
    current_layer = 0
    current_z = 0.0
    perimeter_type = None
    perimeter_block_count = 0
    inside_perimeter_block = False
    logging.info("Starting G-code processing")
    logging.info(f"Input file: {input_file}")
    logging.info(f"Values: {V_STAR},  {H_STAR},  {E_DOT}")
    # Read the input G-code
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Identify the total number of layers by looking for `G1 Z` commands
    total_layers = sum(1 for line in lines if line.startswith("G1 Z"))

    # Process the G-code
    modified_lines = []
    prev_x = 0
    prev_y = 0
    for line in lines:
        params = get_line_values(line)
        # new layer shifts upwards
        if " ; move to first layer point" in line and line.startswith("G1 Z"):
            logging.info("z move old: " + line)
            new_z = params[2] + H
            line = f"G1 Z{new_z} F720 ; move to first layer point MODIFIED\n"
            logging.info("z move new: " + line)
        # records first point to use in distance calcs
        elif " ; move to first layer point" in line:
            logging.info("first layer point; stored in prev: " + line)
            prev_x = params[0]
            prev_y = params[1]
        elif " ; infill" in line:
            logging.info("old xy move: " + line)
            length = math.dist((prev_x, prev_y), (params[0], params[1]))
            F_new = E_DOT * V_STAR * FIL_AREA / THREAD_AREA
            E_new = length * E_DOT / F_new
            line = f"G1 X{params[0]} Y{params[1]} E{E_new} F{F_new} ; infill modified\n"
            logging.info("new xy move: " + line)
        modified_lines.append(line)

    # Overwrite the input file with the modified G-code
    with open(input_file, 'w') as outfile:
        outfile.writelines(modified_lines)

    logging.info("G-code processing completed")
    logging.info(f"Log file saved at {log_file_path}")


# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process G-code for Z-shifting and extrusion adjustments.")
    parser.add_argument("input_file", help="Path to the input G-code file")
    parser.add_argument("-v", type=float, default=1)
    parser.add_argument("-h_star", type=float, default=3)
    parser.add_argument("-e_dot", type=float, default=1)
    parser.add_argument("-alpha", type=float, default=1)
    parser.add_argument("-nozzle_dia", type=float, default=0.4)
    parser.add_argument("-fil_dia", type=float, default=1.75)
    args = parser.parse_args()

    # V_STAR = args.v
    # H_STAR = args.h_star
    # E_DOT = args.e_dot
    ALPHA = args.alpha
    NOZZLE_DIAM = args.nozzle_dia
    FIL_DIA = args.fil_dia
    gui()
    H = H_STAR * ALPHA * NOZZLE_DIAM
    FIL_AREA = 3.1415 * ((FIL_DIA/2) ** 2)
    THREAD_AREA = 3.1415 * ((ALPHA * NOZZLE_DIAM / 2) ** 2)

    process_gcode(
        input_file=args.input_file
    )
