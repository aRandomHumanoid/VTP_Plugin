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
from printing_stats import PrintingStats
from move_gcode_line import MoveGcodeLine
from mesh_stuff import MeshStuff

# Vars: the important ones
global stats
global meshes

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


def remove_nozzle_check(lines, nozzle_dia):
    out = []
    for line in lines:
        if "; nozzle check" in line:
            continue
        out.append(line)
    return out


def read_lines(input_file):
    logging.info("Starting G-code processing")
    logging.info(f"Input file: {input_file}")
    # Read the input G-code
    with open(input_file, 'r') as infile:
        return infile.readlines()


def write_file(out, output_file):
    # Overwrite the input file with the modified G-code
    with open(output_file, 'w') as outfile:
        outfile.writelines(out)

    logging.info("G-code processing completed")
    logging.info(f"Log file saved at {log_file_path}")


def extract_value(line, value):
    match = re.search(rf'{value}(?:\d*\.\d+|\d+(?:\.\d+)?)', line)
    if match is not None:
        return float(match.group().removeprefix(value))
    else:
        return None

def process_gcode(lines):
    ret = []
    prev_x = 0
    prev_y = 0
    current_z = 0
    for i in range(len(lines)):
        line = lines[i]
        params = MoveGcodeLine.from_line(line)
        if "; support" in line:
            new_line = MoveGcodeLine(x=params.x, y=params.y, z=current_z, e=params.e, f=params.f)
            ret.append(new_line.gcode("new support "))
            continue
        if ";Z:" in line:
            current_z = extract_value(line, "Z:")
        if " ; travel" in line and "Z" in line or " ; move" in line and "Z" in line:
            j = i + 1
            while j in range(len(lines)) and " ; infill" not in lines[j]:
                j += 1
            if j >= len(lines):
                continue
            next_line = MoveGcodeLine.from_line(lines[j])
            new_x = next_line.x
            new_y = next_line.y
            mesh_number = meshes.classify_point([new_x, new_y, current_z])
            new_z = stats.evaluate_z_at_point(new_x, new_y, current_z, mesh_number)
            new_line = MoveGcodeLine(z=new_z, f=15000)
            ret.append(new_line.gcode("NEW Z MOVE"))
            continue
        elif " ; travel" in line or " ; move" in line:
            logging.info("first layer point; stored in prev: " + line)
            prev_x = params.x
            prev_y = params.y
        elif " ; infill" in line:
            logging.info("old xy move: " + line)
            new_lines = split_line(prev_x, params.x, prev_y, params.y, current_z, 1)
            ret.extend(new_lines)
            logging.info("new xy move: " + line)
            prev_x = params.x
            prev_y = params.y
            continue
        elif "G1 Z" in line: # if somthing random has a move
            logging.info("bad move (?): " + line)
            continue
        ret.append(line)


    return ret


def split_line(x_start, x_end, y_start, y_end, z_end, increment_length):
    ret = []
    num = math.ceil(math.dist((x_start, y_start), (x_end, y_end)) / increment_length)
    delta_x = (x_end - x_start) / num
    delta_y = (y_end - y_start) / num
    x_prev = x_start
    y_prev = y_start
    for i in range(num):
        x_current = x_start + delta_x * (i + 1)
        y_current = y_start + delta_y * (i + 1)
        mesh_number = meshes.classify_point([x_current, y_current, z_end - stats.layer_height])
        z, e, f = stats.evaluate_vars(x_prev, x_current, y_prev, y_current, z_end, mesh_number)
        new_line = MoveGcodeLine(x_current, y_current, z, e, f)
        ret.append(new_line.gcode("created lines"))
        x_prev = x_current
        y_prev = y_current

    return ret



def main():
    global meshes
    global stats
    parser = argparse.ArgumentParser(description="Post-process G-code for Z-shifting and extrusion adjustments.")
    # parser.add_argument("input_file", help="Path to the input G-code file")
    parser.add_argument("-alpha", type=float, default=1)
    parser.add_argument("-nozzle_dia", type=float, default=0.4)
    parser.add_argument("-fil_dia", type=float, default=1.75)
    parser.add_argument("-eval_increment", type=float, default=1.5)
    parser.add_argument("-e_dot", type=float, default=250)
    args = parser.parse_args()

    equation_file_path = "equations.txt"
    mesh_path = "test_mesh.3mf"
    gcode_path = "test_mesh.gcode"
    meshes = MeshStuff(mesh_path)
    lines = read_lines(gcode_path)
    stats = PrintingStats(lines=lines, path=equation_file_path, alpha=args.alpha, nozzle_dia=args.nozzle_dia,
                          fil_dia=args.fil_dia)

    mod_lines = remove_nozzle_check(lines, stats.nozzle_dia)
    mod_lines = process_gcode(mod_lines)
    write_file(mod_lines, "outputtest.gcode")

# Main execution
if __name__ == "__main__":
    main()