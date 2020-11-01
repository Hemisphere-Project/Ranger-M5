from m5_receive import M5Interface
from enttecpro_receive import DmxInput
from enttecpro_send import DmxOutput
from scene import SceneBook
from time import sleep
import sys, signal, os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

M5usb = M5Interface()
M5usb.logEvents = False
M5usb.start()

DMXin = DmxInput(1, 'sceneselect', 10)
# DMXin.logEvents = False
DMXin.start()

DMXout = DmxOutput()
# DMXout.test = True
DMXout.start()

Book = SceneBook(DMXout, 'scenario.json')

# SCENE Select
@DMXin.on("sceneselect")
def ss(ev, sceneN):
    Book.selectscene(sceneN)

# MEASURE process
@M5usb.on('measure')
def ms(ev, data):
    Book.process(data['sensor'], data['value'])

#WATCH scenario
def scenarioreload(e):
    if e.src_path.endswith("scenario.json"):
        print('reload', e)
        Book.load()
handler = PatternMatchingEventHandler("*/scenario.json", None, False, True)
handler.on_created = scenarioreload
observer = Observer()
observer.schedule(handler, os.path.dirname(os.path.realpath(__file__)) )
observer.start()

# Book.setup( {'scenes': [
#     {'sensors': [
#         {
#             'hid':1,
#             'dmxchannels': [1],
#             'interpolation': 0,
#             'thresholds': [(500, 10), (1000, 100), (2000, 255)]
#         }
#     ]}
# ]} )

# Book.save()

Book.load()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    M5usb.quit()
    DMXin.quit()
    DMXout.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()