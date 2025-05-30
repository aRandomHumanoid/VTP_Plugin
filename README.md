Thing for making the thing into the other thing.

TO USE:

1. Download "main.py" 
2. Download python from [https://www.python.org/downloads/]
3. Find the locatioin for python.exe and main.py
4. Navigate to "Output Options" under the "Print Settings" tab in PrusaSlicer
5. Enter the following under post processing scripts: "C:\Your\Path\To\Python\python.exe" "C:\Your\Path\To\Script\main.py"

The following flags can be used:

- "-alpha" : thread expansion ratio : default = 1
- "-nozzle_dia" : diameter of the nozzle : default = 0.4
- "-fil_dia" : diameter of the filament : default = 1.75

Example: "C:\Your\Path\To\Python\python.exe" "C:\Your\Path\To\Script\main.py" -alpha 1.2 -nozzle_dia 0.6 -fil_dia 1.75
