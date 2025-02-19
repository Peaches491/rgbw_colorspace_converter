#!/usr/bin/env python

import os
import sys
import random

from rgbw_colorspace_converter.colors.converters import RGB, HSV

# Do what I can to get the terminal to maybe show colors, hopefullyt more than 8....
os.environ["TERM"] = "xterm-256color"  # screen
os.system("reset; tput clear; tput init; tput civis;stty -echo; ")

col_width = os.get_terminal_size().columns

sleep = sys.argv[1]

os.system("tput clear; ")

## The following code is basically a mess as it grew from a small testing example to somethign that made pretty patterns.
# But until is needs more features, or stops working, here it is :-)

intro_cmd = """
export COL=`tput color`
echo $COL > num_cols

colr -c 0 "                                    ╦ ╦╔╗ ╔═╗                                  " "ff3100" "#6400ff";
colr -c 0 "                                    ╠═╣╠╩╗╠═╝                                  " "ff3100" "#6400ff";
colr -c 0 "                                    ╩ ╩╚═╝╩                                    " "ff3100" "#6400ff";

sleep 1;

colr -c 0 " ----- ALERT ALERT ALERT ----- " "ff0000" "00ffff"
colr -c 0 " ----- ALERT ALERT ALERT ----- " "ff0000" "00ffff"
colr -c 0 " ----- terminal color support ----- " "ff0000" "00ffff"
colr -c 0 " --- $COL SUPPORTED  COLORS (( $COL )) COLORS SUPPORTED $COL --- " "ff0000" "00ffff" "flash"

echo "

This module will not amaze with it's color handling capabilities via terminal colors :-)  It's really meant as a demonstration of a simple use of the module, and leveraging an easy and pretty UNIxVERSALLY available display to give you the gist of what is going on.  It's still kind of neat.  And give Colr some love, I'm using them as my 'display hardware'.
"

echo "

"
sleep 1
"""

os.system(intro_cmd)

# Abandoned math
# Try to establish the terminal color space so i can increment the colors properly and not send too fine grain codes that just look like repeated colors.  This is a hack :-)
num_colors = float(int(os.popen("tput colors").readline().rstrip()))
nc = int(os.popen("cat num_cols").readline().rstrip())

if nc < num_colors:
    num_colors = nc


# fractional_360 = float(num_colors)/360.0
b = 1.0 / num_colors


# 1/176
# 0.005681818181818
# 176/360 = 0.488888888
# 184/360 = .5222222
# 360/176 = 2.04545
# 2.04545/176 = 0.0116219
# b=(176/360) = 0.488888888888889/175 = 0.002777777777778 ////  .48/.00277 = 181.06 //// .48/176 = 0.002727272 // th
# .48/.52 = .9* / 176 = .00534 * (184*176) = 0.04272
#                /360 = .0026 * (184-176) = =.0208
# 360-176=184
# frac left / frac colorspace represents = tyhid neg num.
# /48/.52 - 1 = -.07692307
# 1/184 = 0.011904
# fix_factor= (float(num_colors)/360.0)
## b=0.04272
# b=0.02078/2


def display_color(color, show_values=None):
    """Use Color to hijack the users display and make it into a demo device for simple color manipulations"""

    col_width = os.get_terminal_size().columns
    ret_code = 0
    l = " " * col_width
    cmd = ""
    if show_values is None:
        cmd = f"""colr  -r 0  "{l}" "{color.hex}" "{color.hex}"  2>/dev/null;"""
    else:
        l = show_values
        cmd = f"""colr  -r 0 "{l}" "000000" "{color.hex}"  2>/dev/null; """

    ret_code = os.system(cmd)
    return int(ret_code)


def color_whirler(color, codes=False):
    """Take a color object and spin around the HUE and SATURATION 1 time"""
    # ASSUMPTION: that hsv_h is set to 0.  IRL, we'd want to get the
    # current hsv_h and hsv_svalue  and loop starting from there.
    ctr = 0
    txt = None
    rolling = True
    color.hsv_h = 1
    color.hsv_s = 0.3
    color.hsv_v = 0.23
    cctr = 0
    while rolling:
        ctr = ctr + 1
        # I modify both 'h' and 's' before submitting for display
        color.hsv_h = color.hsv_h + b * [6, 12, 5, 3][random.randint(0, 3)]
        color.hsv_s = color.hsv_s + b * [2, 6, 4, 3][random.randint(0, 3)]
        color.hsv_v = color.hsv_v - b * 1.2

        sleep_time = 0.1
        if codes is True:
            txt = f"{color}"
            sleep_time = 0.2
        rc = display_color(color, txt)
        if rc != 0:
            raise Exception("escape detected")
        os.system(f"sleep {sleep_time}")
        if color.hsv_s >= 1.0:
            color.hsv_s = 0.00
        if (
            color.hsv_h >= 1.0
        ):  # It is not allowed to go above 1.0, so test for equality
            cctr = cctr + 1
            if cctr == 18:
                rolling = False
            color.hsv_h = 0.0
        if color.hsv_v < 0.15:
            color.hsv_v = 1.0
    print(ctr)


def color_spinner(color, codes=False):
    """Take a color object and spin around HUE"""
    # ASSUMPTION: that hsv_h is set to 0.  IRL, we'd want to get the current hsv_h value
    # and loop starting from there.
    txt = None
    rolling = True
    sleep_time = 0.00
    ctr = 0
    while rolling:
        # Assumption
        color.hsv_h = color.hsv_h + b  # num_cov_increments
        if codes is True:
            txt = f"{color}"
            sleep_time = 0.2
        rc = display_color(color, txt)
        if rc != 0:
            raise Exception("escape detected")
        os.system(f"sleep {sleep_time}")

        if color.hsv_h >= 1.0:
            color.hsv_h = 0.0
            rolling = False
        ctr = ctr + 1
    print(ctr)


color = RGB(255, 0, 0)
# "We are starting with red, which looks like this in the various color spaces {color}",
# "Using the color objects 'h' value, I'll spin around from red through all of the colors and back to red.  The rgb representation of red is {color.rgb}, hsv={color.hsv}* Note, the 'h' value is often represented on a scale of 0-360 degrees.  We have normalized it to be 0-1 for easier programatic use, and to be consistent wit the other values ranges(s and v). Two seconds, and we'll get started.  I'll spin around 2x before moving to saturation.  OH!  And please note, the terminal display is probably lucky to be rendering {num_colors} colors- this is not representing the richnesss of color we should be seeing.",


try:
    # Loop through and just change color hue
    for i in [1, 2]:
        display_color(
            color, f"Starting Cycle {i} with no codes, cycle 2 will have codes."
        )
        os.system("sleep 1")
        codes = False
        if i == 2:
            codes = True
        color_spinner(color, codes)

    # "This simple demo exercised a few parts of this package.  First, I created a color object using RGB.  I then manipulated that object using the corresponding HSV properties(h in particular) to roll around the color wheel.  Then, the cool terminal rendering s/w 'Colr' was hijacked as my display to colorize each row-- and Colr uses Hex.  So, I began in RGB, manipulated things in HSV, and interacted with the display in HEX.  This is the primary motivator to build this module, allowing working in one space and emitting in another.  The second time around I printed out the color codes so you could see how they all change in relation to each other if you wished.",

    display_color(
        color,
        f"Ok!  last demo.  This time, I'm going to move around the color wheel using the 'h' value again, and at the same time move through the saturation value too 's'.  I'm not going to cover V b/c it represents 'brightness', which is not conveyed well in this format.  Again, 2 rounds, the second with color codes, with the changes in RGB and RGBW particularly non-intuitive.",
    )

    os.system(f"sleep {sleep}")

    # This one I'm changing H, S, V with each iteration, semi-randomply.  You gat much more diverse colors than the first example.
    color = RGB(255, 0, 0)
    for i in [2]:
        display_color(
            color, f"Starting Cycle {i} with no codes, cycle 2 will have codes."
        )
        os.system(f"sleep {sleep}")
        codes = False
        if i == 2:
            codes = True
        color_whirler(color, codes)


except Exception as e:
    del e


exit_cmd = f"""
echo "

"
colr -c 0 "                                    ╦ ╦╔╗ ╔═╗                                  " "#ff0000" "#0000ff";
colr -c 0 "                                    ╠═╣╠╩╗╠═╝                                  " "#ff0000" "#0000ff";
colr -c 0 "                                    ╩ ╩╚═╝╩                                    " "#ff0000" "#0000ff";

echo "

"
tput cnorm
stty echo
stty +echo
"""

os.system(exit_cmd)
