import pygetwindow
import cv2
import mouse
from pynput.keyboard import Key, Listener
import time
import keyboard
import numpy as np
import pyautogui
import pytesseract
from threading import Thread
import win32gui

orgX = -10
orgY = 0
orgWidth = 1920
orgHeight = 1111

mouse_timeout_normal = 0.2
mouse_timeout_fast = 0.1

refresh_Y = 81
refresh_X = 1220

shareTruck_X = 1030
shareTruck_Y = 967

shareBox_Y = 355
shareBox_X = 696

confirmShare_Y = 647
confirmShare_X = 1040

truckItemBox_Y = 876
truckItemBox_X = 700
truckItemWidth = 60
truckItemHeight = 60
truckItemGap = 4
truckItemBoxWidth = 450
truckItemBoxHeight = 60

shareBoxItemHeight = 93
shareBoxItemWidth = 510
shareBoxItemGap = 14
scrollGap = 44
shareOffset= 10

truckScreen__min_X = 683
truckScreen_max_X = 1200
truckScreen_min_Y = 100
truckScreen_max_Y = 722

min_count_share = 3
threshold_urShard = .825
threshold_truck = 0.8

rangeOffset = 20

pictureFolder = './pictures/'

urShard = cv2.imread(pictureFolder+'ur_shard.png', cv2.COLOR_RGB2BGR)
urTruck1 = cv2.imread(pictureFolder+'urtruck1.png', cv2.COLOR_RGB2BGR)
urTruck2 = cv2.imread(pictureFolder+'urtruck2.png', cv2.COLOR_RGB2BGR)
srTruck1 = cv2.imread(pictureFolder+'srtruck1.png', cv2.COLOR_RGB2BGR)

nameBox_Y = 770
nameBox_X = 796
nameBox_Width = 280
nameBox_Height = 30
powerBox_X = 832
powerBox_Y = 831
powerBox_Width = 65
powerBox_Heigth = 22

foundTrucks = []

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        # Initializing the Thread class
        super().__init__(group, target, name, args, kwargs)
        self._return = None

    # Overriding the Thread.run function
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return

def click(x,y,normal):
    if normal:
        mouse_timeout = mouse_timeout_normal
    else:
        mouse_timeout = mouse_timeout_fast

    mouse.move(x,y)
    time.sleep(mouse_timeout)
    mouse.click()
    time.sleep(mouse_timeout)

def pointIsOutside(pt):
    return pt[0] < truckScreen__min_X or pt[0] > truckScreen_max_X or pt[1] < truckScreen__min_X or pt[1] > truckScreen_max_Y

def pointInRange(pt, arr):
    for [x,y] in arr:
        if x-rangeOffset <= pt[0] and pt[0] <= x+rangeOffset and y-rangeOffset <= pt[1] and pt[1] <= y+rangeOffset:
            return True
    return False

def clickShare(x,y):
    click(x,y,True)
    click(confirmShare_X,confirmShare_Y,True)
    click(shareTruck_X,shareTruck_Y,True)

def share_Truck(count,isServer):
    click(shareTruck_X,shareTruck_Y,True)
    shareShot = cv2.cvtColor(np.array(pyautogui.screenshot()),cv2.COLOR_RGB2BGR)
    # cv2.imshow('ShareShot',shareShot)
    # cv2.waitKey(0)
    for j in (0,1):
        for i in (0,4):
            shareItem_X = shareBox_X
            shareItem_Y = shareBox_Y + i*(shareBoxItemHeight+shareBoxItemGap)
            shareImage = shareShot[shareItem_Y:shareItem_Y+shareBoxItemHeight,shareItem_X:shareItem_X+shareBoxItemWidth]
            # cv2.imshow('Shareitem', shareImage)
            # cv2.waitKey(0)
            if j == 0 and i == 0 and isServer and count < 4 :
                clickShare(shareItem_X+shareOffset,shareItem_Y+shareOffset)
                continue
            if j == 0 and i == 1:
                clickShare(shareItem_X+shareOffset,shareItem_Y+shareOffset)
                continue
            if j == 0 and i == 2:
                clickShare(shareItem_X+shareOffset,shareItem_Y+shareOffset)
                continue
            continue                
            content = pytesseract.image_to_string(shareShot[shareItem_Y:shareItem_Y+shareBoxItemHeight,shareItem_X:shareItem_X+shareBoxItemWidth])

def addResToLoc(res,loc):
    resFlatten = res.flatten()
    indSort = np.argsort(resFlatten)
    
    indSort = indSort[::-1]
    indSort = indSort[0:10]

    idx2d = np.unravel_index(indSort, res.shape)
    
    # idx2d = idx2d[::-1]
    # idx2d = idx2d[0:10]

    for n_pt in zip(*idx2d[::-1]):
        if pointInRange(n_pt,loc) or pointIsOutside(n_pt):
            continue
        print(res[n_pt[1]][n_pt[0]])
        if res[n_pt[1]][n_pt[0]] < threshold_truck:
            continue
        loc.append(n_pt)
        if(len(loc) == 2):
            break

def addLocations(locX,loc):
    for pt in locX:
        loc.append(pt)

def analyse_static_Truck(foundTrucks):
    
    screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()),cv2.COLOR_RGB2BGR)
    truckLocations = []

    loc1 = []
    loc2 = []
    loc3 = []

    res1 = cv2.matchTemplate(screenshot,urTruck1,cv2.TM_CCOEFF_NORMED)
    res2 = cv2.matchTemplate(screenshot,urTruck2,cv2.TM_CCOEFF_NORMED)
    res3 = cv2.matchTemplate(screenshot,srTruck1,cv2.TM_CCOEFF_NORMED)

    t1 = CustomThread(target=addResToLoc,args=(res1,loc1))
    t2 = CustomThread(target=addResToLoc,args=(res1,loc2))
    t3 = CustomThread(target=addResToLoc,args=(res1,loc3))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    addLocations(loc1,truckLocations)
    addLocations(loc2,truckLocations)
    addLocations(loc3,truckLocations)

    checkedLocations = []

    for location in truckLocations:

        if pointInRange(location,checkedLocations):
            continue

        checkedLocations.append(location)

        truckLocation_X = location[0]
        truckLocation_Y = location[1]
        count = 0
        click(truckLocation_X,truckLocation_Y,False)


        screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()),cv2.COLOR_RGB2BGR)
        itembox = screenshot[truckItemBox_Y:truckItemBox_Y+truckItemHeight,truckItemBox_X:truckItemBox_X+truckItemBoxWidth]
        namebox = screenshot[nameBox_Y:nameBox_Y+nameBox_Height, nameBox_X:nameBox_X+nameBox_Width]
        powerBox = screenshot[powerBox_Y:powerBox_Y+powerBox_Heigth, powerBox_X:powerBox_X+powerBox_Width]

        # cv2.imshow('Powerbox', powerBox)
        # cv2.waitKey(0)    
        # cv2.imshow('Namebox', namebox)
        # cv2.waitKey(0)    

        name = pytesseract.image_to_string(namebox,config="--psm 7").strip()
        power = pytesseract.image_to_string(powerBox,config="--psm 7").strip()
        truckstring = name + ';' + power
        print(truckstring)

        # cv2.imshow('Itembox', itembox)
        # cv2.waitKey(0)
        if truckstring in foundTrucks:
            return
        
        foundTrucks.append(truckstring)

        for i in range(0,7):
            truckItem_X = i*(truckItemWidth+truckItemGap)
            truckItem_Y = 0
            item = itembox[truckItem_Y:truckItem_Y+truckItemHeight, truckItem_X:truckItem_X+truckItemWidth]
            # cv2.imshow('Item', item)
            # cv2.waitKey(0)
            res = cv2.matchTemplate(item,urShard,cv2.TM_CCOEFF_NORMED)
            loc = np.where( res >= threshold_urShard)
            for pt in zip(*loc[::-1]):
                count += 1

        print(count)

        if count > 2:
            #click(shareTruck_X,shareTruck_Y,True)
            share_Truck(count,False)

        click(refresh_X,refresh_Y,True)
        time.sleep(2)

        


# hwndMain = win32gui.FindWindow(None, "Last War-Survival Game")  
# rect = win32gui.GetWindowRect(hwndMain)
# x = rect[0]
# y = rect[1]
# w = rect[2] - x
# h = rect[3] - y
# print("Window %s:" % win32gui.GetWindowText(hwndMain))
# print("\tLocation: (%d, %d)" % (x, y))
# print("\t    Size: (%d, %d)" % (w, h))

foundTrucks = []
win = pygetwindow.getWindowsWithTitle('Last War-Survival Game')[0]
win.activate()
win.moveTo(orgX,orgY)
win.size = (orgWidth, orgHeight)

time.sleep(2)
break_program = False
def on_press(key):
    global break_program
    if key == Key.f1:
        print ('end pressed')
        break_program = True
        return False



with Listener(on_press=on_press) as listener:
    while(not break_program):
        analyse_static_Truck(foundTrucks)
    listener.join()

    

    