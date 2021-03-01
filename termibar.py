from powerliner import *
import subprocess
import asyncio
from i3ipc.aio import Connection


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

    sq = PowerlineSequence(wksp, True)
    print(sq.render())


asyncio.run(workspaces())


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


print(getVolume())
print(getBatteryStatus())
print(getBatteryCapacity())
print(getDate())
print(getTime())
print(getBatteryTime())
