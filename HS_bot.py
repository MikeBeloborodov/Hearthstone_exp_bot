import cv2 as cv
import pyautogui
import time
from win32api import GetSystemMetrics
from winotify import Notification, audio
import threading as th
import numpy as np
import os
from dotenv import load_dotenv
import asyncio
import telegram
import datetime
import argparse

# Parses arguments
# -t option sends a telegram notification when the battle starts
parser = argparse.ArgumentParser(description="Hearthstone exp farming bot.")
parser.add_argument(
    "-t",
    "--telegram_notification",
    help="Sends a telegram notification when the battle starts.",
    action="store_true"
    )

# -i option tells program that you are in game right now
# and it won't launch hearthstone from battle.net
parser.add_argument(
    "-i",
    "--in_game",
    help="Use this option if you are in game right now. Otherwise program will open a new hearthstone window.",
    action="store_true"
)
args = parser.parse_args()

# load env variables
load_dotenv()

# Treshold for cv2
CONFIDENCE_TRESHOLD = 0.7
TREASURE_ITEM_CONFIDENCE_TRESHOLD = 0.4

# Get monitor resolution
MONITOR_WIDTH = GetSystemMetrics(0)
MONITOR_HEIGHT = GetSystemMetrics(1)

TIME_TO_WAIT = 1720 # Time to wait between cycles in seconds
TIME_TO_SLEEP_AFTER_CRASH = 600
TIME_BEFORE_FIND_TARGET = 60 # Used after crash

# Max crashes before program stops
MAX_CRASHES_TRESHOLD = 10

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


def press_button(target_path:str, enemy=False) -> None:
    """
    Find and press a button by it's path name
    Optional 'enemy' argument for get_target_values function
    """
    target_x, target_y, confidence = get_target_values(target_path, enemy)

    pyautogui.click(target_x, target_y)


def wait_for_target(target_img_path: str, click=False, treasure_item=False) -> bool:
    """
    Waits for target to appear on the screen
    and returns True if it did.
    Optional argument 'click' will click the target.
    """
    found = False
    times_tried = 0 
    while not found and times_tried < 300:
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
            times_tried += 1
            time.sleep(1)

        """
        # Sometimes there are aditional rewards and such
        # this helps to click trough them and continue
        if times_tried == 100:
            for i in range(0,3):
                pyautogui.click(MONITOR_WIDTH / 2, MONITOR_HEIGHT / 2)
                time.sleep(1)
        """

    if times_tried >= 150:
        print(f'Error. Max tries reached to find {target_img_path}')
        raise
    else:
        return True


def find_the_target(target_img_path: str, treasure_item=False, time_to_wait=0) -> bool:
    """
    Checks if target is on the screen.
    """

    # Sleep before the search
    # 0 by default
    time.sleep(time_to_wait)

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
            pyautogui.move(0, -200)
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
    

def key_capture_thread() -> None:
    """
    This thread is looking for enter key
    to stop the waiting cycle
    """
    global continue_waiting
    input()
    continue_waiting = False


async def waiting_cycle() -> None:
    """
    Waits for the max amount of exp
    Uses another thread to read enter key
    to break the cycle
    """
    global continue_waiting
    global args

    # Checks other thread 
    # and only starts if there are no other similar ones
    thread_names = [thread.name for thread in th.enumerate()]
    if "key_capture_thread" not in thread_names:
        th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

    countdown = TIME_TO_WAIT
    while countdown != 0 and continue_waiting:
        if countdown % 60 == 0:
            print(f'Time until the battle: {int(countdown / 60)} mins.')
        time.sleep(1)
        countdown -= 1
    
    # desktop notification
    notification.show()
    # if -t option was used sends a telegram notification
    if args.telegram_notification:
        telegram_bot = telegram.Bot(os.environ["BOT_TOKEN"])
        async with telegram_bot:
            await telegram_bot.send_message(
                text=f'Battle starts!',
                chat_id=os.environ["MASTER_CHAT_ID"])
        
    continue_waiting = True
    

async def start_bot():
    """
    Main loop
    """
    
    # Telegram bot for error messages
    telegram_bot = telegram.Bot(os.environ["BOT_TOKEN"])
    
    games_counter = 1
    crashes_counter = 0
    while crashes_counter < MAX_CRASHES_TRESHOLD:
        try:
            # Time to switch to HS or battle.net screen
            time.sleep(3) 

            if not args.in_game:
                # Clicks on play button in battle net
                wait_for_target('data/battle_net_play_button.jpg', click=True)

                # Check if game crashed during the battle
                # then continue fighting
                if find_the_target('data/ability_icon.jpg', time_to_wait=TIME_BEFORE_FIND_TARGET):
                    # Fight
                    battle_sequence()
                    time.sleep(2)

                    # Click trough prizes
                    times_tried = 0
                    while not find_the_target('data/treasure_item.jpg', treasure_item=True):
                        pyautogui.click()
                        time.sleep(1)
                        times_tried += 1
                        if times_tried >= 300:
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

                    # Clicks trough the rewards
                    times_tried = 0
                    while not find_the_target('data/location_choice_button.jpg'):
                        pyautogui.click(MONITOR_WIDTH / 2, MONITOR_HEIGHT / 2)
                        time.sleep(1)
                        times_tried += 1
                        if times_tried > 300:
                            print("Error. Max tries reached while trying to find location_choice_button.jpg")
                            raise

                    # Set in game to true and continue loop from the beginning
                    args.in_game = True
                    continue

                # Clicks on mercenaries mode button
                wait_for_target('data/mercenaries_button.jpg', click=True)

                # Clicks on the new run button
                wait_for_target('data/mercenaries_new_run.jpg', click=True)

                # Clicks on choose barrens button
                wait_for_target('data/mercenaries_choose_barrens.jpg', click=True)

                # Switch to in game after it opens the window for the 1st time
                args.in_game = True

            print(f'Game {games_counter} started.')

            # Location choice
            wait_for_target('data/location_choice_button.jpg', click=True)

            # Party choice
            wait_for_target('data/party_choice_button.jpg', click=True)

            # The very first run asks you to lock in the party
            # This checks for confirmation button
            time.sleep(1)
            if find_the_target('data/lock_in_party_confirmation_button.jpg'):
                wait_for_target('data/lock_in_party_confirmation_button.jpg', click=True)

            # Play button
            wait_for_target('data/play_button.jpg', click=True)

            # Cards choice yellow button
            wait_for_target('data/yellow_button_pre_battle.jpg', click=True)

            # Wait for max exp
            await waiting_cycle()

            # Fight
            if wait_for_target('data/ability_icon.jpg'):
                battle_sequence()
                time.sleep(2)

            # Click trough prizes
            times_tried = 0
            while not find_the_target('data/treasure_item.jpg', treasure_item=True):
                pyautogui.click()
                time.sleep(1)
                times_tried += 1
                if times_tried >= 300:
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

            # Clicks trough the rewards
            times_tried = 0
            while not find_the_target('data/location_choice_button.jpg'):
                pyautogui.click(MONITOR_WIDTH / 2, MONITOR_HEIGHT / 2)
                time.sleep(1)
                times_tried += 1
                if times_tried > 300:
                    print("Error. Max tries reached while trying to find location_choice_button.jpg")
                    raise
            
            print(f'Game {games_counter} ended.')
            games_counter += 1
        except Exception as error:
            
            crashes_counter += 1

            # saves error screenshot
            screenshot_path = 'errors/' + str(datetime.datetime.now())[:-7].replace(':', '.') + '.jpg'
            pyautogui.screenshot(screenshot_path)
            print(error)

            # sends message to the telegram using a bot
            async with telegram_bot:
                await telegram_bot.send_message(
                    text=f'Error with bot during the game #{games_counter}. Crash # {crashes_counter}.',
                    chat_id=os.environ["MASTER_CHAT_ID"])
                await telegram_bot.send_document(
                    chat_id=os.environ["MASTER_CHAT_ID"],
                    document=screenshot_path)

            # Close Hearthstone application and set in game to false
            os.system("taskkill /im Hearthstone.exe")
            args.in_game = False
            time.sleep(TIME_TO_SLEEP_AFTER_CRASH)


if __name__ == '__main__':
    asyncio.run(start_bot())
