import cv2 as cv
import pyautogui
import time
from win32api import GetSystemMetrics
from winotify import Notification, audio
import threading as th
import numpy as np


# Treshold for cv2
CONFIDENCE_TRESHOLD = 0.7
TREASURE_ITEM_CONFIDENCE_TRESHOLD = 0.4

# Get monitor resolution
MONITOR_WIDTH = GetSystemMetrics(0)
MONITOR_HEIGHT = GetSystemMetrics(1)

# Time to wait between cycles in seconds
TIME_TO_WAIT = 1620

# Continue or stop the waiting cycle
continue_waiting = True

# Notification popup in tray 
notification = Notification(app_id="HS bot",
                            title="Next battle begins",
                            msg="Please open Hearthstone window.",
                            duration="short")
notification.set_audio(audio.Mail, loop=False)


def get_target_values(target_img_path: str, enemy=False) -> tuple:
    """
    Returns x and y coordinates and confidence of a target image.
    Coordinates point to the middle of a target. 
    If it's an enemy icon, takes screenshot of about 1/3 of the screen
    to fit only enemies.
    """
    if enemy:
        screenshot = pyautogui.screenshot( 
            region=(0, 0, MONITOR_WIDTH, int(MONITOR_HEIGHT / 2.5) )
        )
        open_cv_image = np.array(screenshot)
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy()
    else:
        screenshot = pyautogui.screenshot()
        open_cv_image = np.array(screenshot)
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy()

    haystack = open_cv_image
    needle = cv.imread(target_img_path)

    result = cv.matchTemplate(haystack, needle, cv.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    target_y = max_loc[1] + int(needle.shape[0] / 2)
    target_x = max_loc[0] + int(needle.shape[1] / 2)

    return (target_x, target_y, max_val)


def press_button(target_path, enemy=False) -> None:
    """
    Find and press a button by it's path name
    Optional 'enemy' argument for get_target_values function
    """
    target_x, target_y, confidence = get_target_values(target_path, enemy)

    pyautogui.click(target_x, target_y)


def wait_for_target(target_img_path, click=False, treasure_item=False) -> bool:
    """
    Waits for target to appear on the screen
    and returns True if it did.
    Optional argument 'click' will click the target.
    """
    found = False
    max_tries = 0 
    while not found and max_tries < 300:
        screenshot = pyautogui.screenshot()
        open_cv_image = np.array(screenshot)
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        haystack = open_cv_image
        needle = cv.imread(target_img_path)

        result = cv.matchTemplate(haystack, needle, cv.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        if treasure_item:
            treshold = TREASURE_ITEM_CONFIDENCE_TRESHOLD
        else:
            treshold = CONFIDENCE_TRESHOLD

        if max_val >= treshold:
            time.sleep(1)
            found = True
            if click: press_button(target_img_path)
        else:
            max_tries += 1
            time.sleep(1)

    if max_tries >= 300:
        print(f'Error. Max tries reached to find {target_img_path}')
        raise
    else:
        return True


def find_the_target(target_img_path, treasure_item=False) -> bool:
    """
    Checks if target is on the screen.
    """
    screenshot = pyautogui.screenshot()
    open_cv_image = np.array(screenshot)
    # Convert RGB to BGR 
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    haystack = open_cv_image
    needle = cv.imread(target_img_path)

    result = cv.matchTemplate(haystack, needle, cv.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    if treasure_item:
        treshold = TREASURE_ITEM_CONFIDENCE_TRESHOLD
    else:
        treshold = CONFIDENCE_TRESHOLD

    if max_val >= treshold:
        return True

    return False


def battle_sequence() -> None:
    """
    Finds enemy icons and presses hero abilities
    until the victory screen appears
    """
    win = False
    while not win:
        for counter in range(0,3):
            # Press hero ability button
            press_button('data/ability_icon.jpg')
            time.sleep(1)

            # Press enemy icon
            press_button('data/enemy.jpg', enemy=True)
            time.sleep(1)
            pyautogui.move(0, -100)
            time.sleep(2)

        # Start the battle
        press_button('data/fight_button.jpg')
        for countdown in range(0, 25):
            if find_the_target('data/victory_emblem.jpg'):
                break
            time.sleep(1)

        # Check if won the battle
        confidence = get_target_values('data/victory_emblem.jpg')[2]
        if confidence >= CONFIDENCE_TRESHOLD:
            win = True
    

def key_capture_thread():
    """
    This thread is looking for enter key
    to stop the waiting cycle
    """
    global continue_waiting
    input()
    continue_waiting = False


def waiting_cycle() -> None:
    """
    Waits for the max amount of exp
    Uses another thread to read enter key
    to break the cycle
    """
    global continue_waiting
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    countdown = TIME_TO_WAIT
    while countdown != 0 and continue_waiting:
        if countdown % 60 == 0:
            print(f'Time until the battle: {int(countdown / 60)} mins.')
        time.sleep(1)
        countdown -= 1
    
    notification.show()
    continue_waiting = True


def start_bot():
    """
    Main loop
    """
    games_counter = 1
    while True:

        time.sleep(3) # Time to switch to HS screen

        print(f'Game {games_counter} started.')

        # Location choice
        wait_for_target('data/location_choice_button.jpg', click=True)

        # Party choice
        wait_for_target('data/party_choice_button.jpg', click=True)

        # Play button
        wait_for_target('data/play_button.jpg', click=True)

        # Cards choice yellow button
        wait_for_target('data/yellow_button_pre_battle.jpg', click=True)

        # Wait for max exp
        waiting_cycle()

        # Fight
        if wait_for_target('data/ability_icon.jpg'):
            battle_sequence()
            time.sleep(2)

        # Click trough prizes
        max_tries = 0
        while not find_the_target('data/treasure_item.jpg', treasure_item=True):
            pyautogui.click()
            time.sleep(1)
            max_tries += 1
            if max_tries >= 300:
                print("Error. Max tries reached while trying to find treasure_item.jpg")
                raise

        # Click on the treasure icon
        wait_for_target('data/treasure_item.jpg', click=True, treasure_item=True)

        # Click on the take treasure button
        wait_for_target('data/take_treasure_button.jpg', click=True)

        # Click on the view party button
        wait_for_target('data/view_party_button.jpg', click=True)

        # Click on the retire button
        wait_for_target('data/retire_button.jpg', click=True)

        # Click on the retire confirm button
        wait_for_target('data/retire_confirm_button.jpg', click=True)

        max_tries = 0
        while not find_the_target('data/location_choice_button.jpg'):
            pyautogui.click(MONITOR_WIDTH / 2, MONITOR_HEIGHT / 2)
            time.sleep(1)
            max_tries += 1
            if max_tries > 300:
                print("Error. Max tries reached while trying to find location_choice_button.jpg")
                raise
        
        print(f'Game {games_counter} ended.')
        games_counter += 1


if __name__ == '__main__':
    start_bot()
