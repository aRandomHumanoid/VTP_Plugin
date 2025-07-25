import re


class MoveGcodeLine:
    line = None
    x = None
    y = None
    z = None
    e = None
    f = None

    def __init__(self, x=None, y=None, z=None, e=None, f=None, line=None):
        self.x = x
        self.y = y
        self.z = z
        self.e = e
        self.f = f
        self.line = line

    @classmethod
    def from_line(cls, line):
        x_match = re.search(r'X(?:\d*\.\d+|\d+(?:\.\d+)?)', line)
        y_match = re.search(r'Y(?:\d*\.\d+|\d+(?:\.\d+)?)', line)
        z_match = re.search(r'Z(?:\d*\.\d+|\d+(?:\.\d+)?)', line)
        e_match = re.search(r'E(?:\d*\.\d+|\d+(?:\.\d+)?)', line)
        f_match = re.search(r'F(?:\d*\.\d+|\d+(?:\.\d+)?)', line)
        x = y = z = e = f = None
        if x_match is not None:
            x = float(x_match.group().removeprefix("X"))
        if y_match is not None:
            y = float(y_match.group().removeprefix("Y"))
        if z_match is not None:
            z = float(z_match.group().removeprefix("Z"))
        if e_match is not None:
            e = float(e_match.group().removeprefix("E"))
        if f_match is not None:
            f = float(f_match.group().removeprefix("F"))
        return cls(x, y, z, e, f, line)

    def get_stats(self):
        return f"X: {self.x}, Y: {self.y}, Z: {self.z}, E: {self.e}, F: {self.f}"

    def gcode(self, msg="modified lineee"):
        new_line = ["G1 "]
        if self.x is not None:
            new_line.append(f"X{round(self.x, 3)} ")
        if self.y is not None:
            new_line.append(f"Y{round(self.y, 3)} ")
        if self.z is not None:
            new_line.append(f"Z{round(self.z, 3)} ")
        if self.e is not None:
            new_line.append(f"E{round(self.e, 3)} ")
        if self.f is not None:
            new_line.append(f"F{round(self.f, 3)} ")

        new_line.append(msg + "\n")
        return "".join(new_line)
