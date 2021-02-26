import subprocess
from time import sleep
from ewmh import EWMH
import Xlib


# Run some program, here it is URXVT terminal.
subprocess.Popen(['alacritty', '--class', 'termibar'])
sleep(1)  # Wait until the term is ready, 1 second is really enought time.

ewmh = EWMH()  # Python has a lib for EWMH, I use it for simplicity here.

# Get all windows?
windows = ewmh.display.screen().root.query_tree().children
d = ewmh.display
# Print WM_CLASS properties of all windows.


def findRec(windows, cl):
    if(windows == []):
        return None
    for w in windows:
        if(w is not None):
            w_class_e = w.get_wm_class()
            if(w_class_e != None):
                w_class, _ = w_class_e
                if(w_class == cl):
                    return w
            w_f = findRec(w.query_tree().children, cl)
            if (w_f is not None):
                return w_f


termibar_w = findRec(windows, "termibar")
print(termibar_w.get_wm_class())
wm_window_type = d.intern_atom('_NET_WM_WINDOW_TYPE')
wm_strut = d.intern_atom('_NET_WM_STRUT')
wm_window_type_dock = d.intern_atom('_NET_WM_WINDOW_TYPE_DOCK')

termibar_w.unmap()
termibar_w.change_property(wm_window_type, Xlib.Xatom.ATOM, 32, [
                           wm_window_type_dock, ], Xlib.X.PropModeReplace)
termibar_w.map()
d.flush()

ewmh.setMoveResizeWindow(termibar_w, h=22)
d.flush()
