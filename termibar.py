import tty
import termios
import sys
import re
import os
from powerliner import *
import subprocess
import asyncio
from i3ipc.aio import Connection
import getpass
import time
import re

strip_ANSI_escape_sequences_sub = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE).sub


def strip_ANSI_escape_sequences(s):
    return strip_ANSI_escape_sequences_sub("", s)


async def workspaces():
    i3 = await Connection().connect()
    workspaces = await i3.get_workspaces()
    wksp = []
    for wk in workspaces:
        bg = "BG"
        fg = "DarkGrey"
        if (wk.focused):
            bg = "Grey"
            fg = "BG"
        if (wk.urgent):
            bg = "Red"
            fg = "White"
        wksp += [[fg, bg, " "+wk.name+" "]]
    return wksp


def getSSID():
    p = subprocess.Popen(
        """iwgetid -r""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    ssid = out.decode("utf-8").replace("\n", "").strip()
    return ssid


def getSignal():
    p = subprocess.Popen(
        """iwconfig wlp2s0 | grep -i quality""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    sig = out.decode("utf-8").split("=")[1].split("/")[0].strip()
    return sig


def getVolume():
    p = subprocess.Popen(
        """awk -F"[][]" '/Left:/ { print $2 }' <(amixer sget Master)""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    vol = out.decode("utf-8").replace("\n", "").strip()
    return vol


def getBatteryStatus():
    p = subprocess.Popen(
        """upower -i /org/freedesktop/UPower/devices/battery_BAT0 | grep -E \"state\"""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    stat = out.decode("utf-8").split(":")[1].replace("\n", "").strip()
    return stat


def getBatteryCapacity():
    p = subprocess.Popen(
        """upower -i /org/freedesktop/UPower/devices/battery_BAT0 | grep -E \"percentage\"""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    cap = out.decode("utf-8").split(":")[1].replace("\n", "").strip()
    return cap


def getBatteryTime():
    p = subprocess.Popen(
        """upower -i /org/freedesktop/UPower/devices/battery_BAT0 | grep -E \"time to\"""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    time = out.decode("utf-8").split(":")[1].replace("\n", "").strip()
    return time


def getTime():
    p = subprocess.Popen(
        """date +'%H:%M'""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    time = out.decode("utf-8").replace("\n", "").strip()
    return time


def getDate():
    p = subprocess.Popen(
        """date +'%d/%m/%Y'""", shell=True, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    date = out.decode("utf-8").replace("\n", "").strip()
    return date


def userSeg():
    return [["Black", "Grey", " \uf103 " + getpass.getuser() + " "]]


def netSeg():
    return [["BG", "DarkGrey", " \uf501 " + getSSID() + " "]]


def wkspSeg():
    return asyncio.run(workspaces())


def timeSeg():
    return [["Black", "Grey", " " + getTime() + " \uf64f ", 5]]


def dateSeg():
    return [["DarkGrey", "BG", " " + getDate() + " \uf5ec ", 4]]


def batSeg():
    return [["BG", "DarkGrey", " \uf57d " + getBatteryCapacity() + " ", 3]]


def soundSeg():
    return [["Black", "Grey", " \ufa7d " + getVolume() + " ", 2]]


def getpos():

    buf = ""
    stdin = sys.stdin.fileno()
    tattr = termios.tcgetattr(stdin)

    try:
        tty.setcbreak(stdin, termios.TCSANOW)
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()

        while True:
            buf += sys.stdin.read(1)
            if buf[-1] == "R":
                break

    finally:
        termios.tcsetattr(stdin, termios.TCSANOW, tattr)

    # reading the actual values, but what if a keystroke appears while reading
    # from stdin? As dirty work around, getpos() returns if this fails: None
    try:
        matches = re.match(r"^\x1b\[(\d*);(\d*)R", buf)
        groups = matches.groups()
    except AttributeError:
        return None

    return (int(groups[0]), int(groups[1]))


lstr = ""
rstr = ""
sys.stdout.write("\u001b[;H")
sys.stdout.write("\u001b[999G")
sys.stdout.flush()
p = getpos()

userSegStr = []
netSegStr = []
wkspSegStr = []
soundSegStr = []
batSegStr = []
dateSegStr = []
timeSegStr = []


def renderBar():
    global lstr
    global rstr
    global p
    sys.stdout.write("\u001b[1G")

    left = PowerlineSequence(userSegStr+netSegStr+wkspSegStr, True)
    right = PowerlineSequence(
        soundSegStr+batSegStr+dateSegStr+timeSegStr, True)

    nlstr = left.render(["Right"])
    nrstr = right.render(["Left"])

    if ((lstr+rstr) != (nlstr+nrstr)):
        lstr = nlstr
        rstr = nrstr

        skp = p[1] - len(strip_ANSI_escape_sequences(lstr)) - \
            len(strip_ANSI_escape_sequences(rstr)) - 1

        sys.stdout.write(lstr)
        sys.stdout.write("\u001b["+str(skp)+"C")
        sys.stdout.write(rstr)
        sys.stdout.flush()


tickquarter = 0
ticksixteenth = 0
ticksixtyfourth = 0

while (1):
    if ticksixtyfourth == 0:
        userSegStr = userSeg()
        dateSegStr = dateSeg()

    if ticksixteenth == 0:
        batSegStr = batSeg()
        netSegStr = netSeg()

    if tickquarter == 0:
        soundSegStr = soundSeg()
        timeSegStr = timeSeg()

    wkspSegStr = wkspSeg()

    renderBar()

    tickquarter += 1
    ticksixteenth += 1
    ticksixtyfourth += 1

    time.sleep(1./30.)
