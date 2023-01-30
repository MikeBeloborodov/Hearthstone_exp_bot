import numpy as np
import time
import datetime
import threading as th
from winotify import Notification, audio
import pyautogui
import cv2 as cv
from .utils import (
    MONITOR_WIDTH,
    MONITOR_HEIGHT,
    CONFIDENCE_TRESHOLD,
    MAX_SEARCH_TRIES,
    MAX_VICTORY_SEARCH,
    ABILITY_ICON,
    ABILITY_ICON_2,
    ABILITY_ICON_3,
    ENEMY_ICON,
    FIGHT_BUTTON,
    VICTORY_EMBLEM,
    T_BETWEEN_CYCLES,
    LOCATION_CHOICE_BUTTON,
    PARTY_CHOICE_BUTTON,
    LOCK_PARTY_BUTTON,
    PLAY_BUTTON,
    YELLOW_PRE_BATTLE_BUTTON,
    MERCS_BUTTON,
    MERCS_NEW_RUN,
    MERCS_CHOOSE_BARRENS,
    TREASURE_ITEM_ICON,
    TREASURE_ITEM_CONFIDENCE_TRESHOLD,
    TAKE_TREASURE_BUTTON,
    YOUR_QUESTS_ICON,
    YOUR_WEEKLY_QUESTS,
    VIEW_PARTY_BUTTON,
    RETIRE_BUTTON,
    RETIRE_CONFIRM_BUTTON,
    BATTLE_SPOILS_ICON,
    ENEMY_CONFIDENCE_TRESHOLD,
)
from .exceptions import (
    MaxTriesReached, 
    MissingAbilityButton,
    MissingEnemyButton
)


class HearthstoneBot:
    """
    Autoclicker bot for Hearthstone mercenaries mode.
    """

    def __init__(self):
        self.target_x = 0
        self.target_y = 0
        self.continue_waiting = True

    
    def show_desktop_notification(self, message: str) -> None:
        """
        This method shows a popup desktop notification.

        Args:
            message (str): Notification text message.
        """

        notification = Notification(app_id="HS bot",
                                    title="HS bot message",
                                    msg=message,
                                    duration="short")
        notification.set_audio(audio.Mail, loop=False)
        notification.show()


    def get_target_values(
        self, 
        target_img_path: str,
        start_x: int = 0,
        start_y: int = 0,
        width: int = MONITOR_WIDTH,
        height: int = MONITOR_HEIGHT
    ) -> tuple:
        """
        Use this method to get a tuple of 
        x and y coordinates of the target centre
        and the value of cv2 confidence.

        Args:
            target_img_path (str): Path to the target image.
            start_x (int): x coordinate of the search area top point.
            start_y (int): y coordinate of the search area top point.
            width (int): Search area width.
            height (int): Search area height.

        Returns:
            (target_x, target_y, max_value)
            target_x (int): Center x coordinate of the target image.
            target_y (int): Center y coordinate of the target image.
            max_value (float): Value from 0 to 1. Max confidence value of cv2.
        """
        
        screenshot = pyautogui.screenshot( 
            region=(start_x, start_y, width, height)
        )
        open_cv_image = np.array(screenshot)
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        haystack = open_cv_image
        needle = cv.imread(target_img_path)

        result = cv.matchTemplate(haystack, needle, cv.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        target_y = max_loc[1] + int(needle.shape[0] / 2)
        target_x = max_loc[0] + int(needle.shape[1] / 2)

        print(f'file - {target_img_path}, max_value - {max_val}')
        return (target_x, target_y, max_val)
    

    def is_target_on_screen(
        self, 
        target_img_path: str,
        max_tries: int = MAX_SEARCH_TRIES,
        confidence_treshold: float = CONFIDENCE_TRESHOLD,
        start_x: int = 0,
        start_y: int = 0,
        width: int = MONITOR_WIDTH,
        height: int = MONITOR_HEIGHT
    ) -> bool:
        """
        Use this method to check if target image is on screen
        and save it's coordinates if it is.

        Args:
            target_img_path (str): Path to the target image.
            confidence_treshold (float): Minimal cv2 confidence for the target.
            max_tries (int): Maximum attempts at searching for target.
            start_x (int): x coordinate of the search area top point.
            start_y (int): y coordinate of the search area top point.
            width (int): Search area width.
            height (int): Search area height.

        Returns:
            True / False (bool): True if target is on screen.
        """

        print(target_img_path)
        for attempt in range(0, max_tries):
            time.sleep(2)
            target_x, target_y, max_value = self.get_target_values(
                target_img_path=target_img_path,
                start_x=start_x,
                start_y=start_y,
                width=width,
                height=height
            )

            if max_value >= confidence_treshold:
                self.target_x = target_x
                self.target_y = target_y

                return True

        return False


    def click_on_target(self) -> None:
        """
        Use this method to click on target with stored x and y values.
        """

        pyautogui.click(self.target_x, self.target_y)


    def search_and_click_on_target(
        self, 
        target_img_path: str,
        max_tries: int = MAX_SEARCH_TRIES,
        confidence_treshold: float = CONFIDENCE_TRESHOLD,
        start_x: int = 0,
        start_y: int = 0,
        width: int = MONITOR_WIDTH,
        height: int = MONITOR_HEIGHT
    ) -> None:
        """
        Use this method to check if target is on the screen and click on it.

        Args:
            target_img_path (str): Path to the target image.
            confidence_treshold (float): Minimal cv2 confidence for the target.
            max_tries (int): Maximum attempts at searching for target.
            start_x (int): x coordinate of the search area top point.
            start_y (int): y coordinate of the search area top point.
            width (int): Search area width.
            height (int): Search area height.
        """

        if self.is_target_on_screen(
            target_img_path=target_img_path,
            confidence_treshold=confidence_treshold,
            max_tries=max_tries,
            start_x=start_x,
            start_y=start_y,
            width=width,
            height=height
        ):
            self.click_on_target()
        else:
            raise MaxTriesReached
        

    def search_multiple_targets(
        self, 
        target_imgs: list,
        max_tries: int = MAX_SEARCH_TRIES,
        confidence_treshold: float = CONFIDENCE_TRESHOLD,
        start_x: int = 0,
        start_y: int = 0,
        width: int = MONITOR_WIDTH,
        height: int = MONITOR_HEIGHT
    ) -> bool:
        """
        Use this method to search trough multiple images.
        If it finds the image it saves it's coordinates
        and returns True.

        Args:
            target_imgs (list[str]): List of paths to target images.
            confidence_treshold (float): Minimal cv2 confidence for the target.
            max_tries (int): Maximum attempts at searching for target.
            start_x (int): x coordinate of the search area top point.
            start_y (int): y coordinate of the search area top point.
            width (int): Search area width.
            height (int): Search area height.

        Returns:
            True / False (bool): True if target is on screen.
        """

        for attempt in range (0, max_tries):
            for target_img in target_imgs:
                if self.is_target_on_screen(
                    target_img_path=target_img,
                    confidence_treshold=confidence_treshold,
                    max_tries=1,
                    start_x=start_x,
                    start_y=start_y,
                    width=width,
                    height=height
                ):
                    return True
        return False



    def go_to_mercenaries(self) -> None:
        """
        Use this method to navigate to the mercenaries mode.
        """

        if self.is_target_on_screen(YOUR_QUESTS_ICON, max_tries=10):
            self.click_on_target()

        if self.is_target_on_screen(YOUR_WEEKLY_QUESTS, max_tries=10):
            self.click_on_target()

        self.search_and_click_on_target(MERCS_BUTTON)

        if self.is_target_on_screen(BATTLE_SPOILS_ICON, max_tries=2):
            self.click_on_target()

        self.search_and_click_on_target(MERCS_NEW_RUN)

        self.search_and_click_on_target(MERCS_CHOOSE_BARRENS)


    def new_run_from_mercenaries(self) -> None:
        """
        Use this method to start new run
        From the location choice menu.
        """

        self.search_and_click_on_target(LOCATION_CHOICE_BUTTON)

        self.search_and_click_on_target(PARTY_CHOICE_BUTTON)
        time.sleep(1)

        if self.is_target_on_screen(LOCK_PARTY_BUTTON, max_tries=1):
            self.click_on_target()
        
        self.search_and_click_on_target(PLAY_BUTTON)

        self.search_and_click_on_target(YELLOW_PRE_BATTLE_BUTTON)


    def battle_sequence(self) -> None:
        """
        Use this method to start the battle sequence
        """

        win = False
        while not win:
            for counter in range(0,3):
                # Press hero ability button
                if self.search_multiple_targets(
                    [ABILITY_ICON, ABILITY_ICON_2, ABILITY_ICON_3],
                ):
                    self.click_on_target()
                else:
                    raise MissingAbilityButton

                # Press enemy icon
                if self.search_multiple_targets(
                    [ENEMY_ICON],
                    confidence_treshold=ENEMY_CONFIDENCE_TRESHOLD,
                    height=int(MONITOR_HEIGHT / 2.5)
                ):
                    self.click_on_target()
                    pyautogui.move(0, -200)
                else:
                    raise MissingEnemyButton

            # Press fight button
            self.search_and_click_on_target(FIGHT_BUTTON)

            # Check if won the battle
            if self.is_target_on_screen(
                VICTORY_EMBLEM,
                max_tries=MAX_VICTORY_SEARCH
            ):
                win = True
                break


    def collect_rewards(self) -> None:
        """
        Use this method to collect all the rewards after the battle.
        Click trough all the prizes and menus.
        """

        while not self.is_target_on_screen(
            TREASURE_ITEM_ICON,
            max_tries=1,
            confidence_treshold=TREASURE_ITEM_CONFIDENCE_TRESHOLD
        ):
            pyautogui.click( int(MONITOR_WIDTH / 2), int(MONITOR_HEIGHT / 2) )
            time.sleep(0.5)

        self.click_on_target()

        self.search_and_click_on_target(TAKE_TREASURE_BUTTON)

        if self.is_target_on_screen(YOUR_QUESTS_ICON, max_tries=2):
            pyautogui.click( int(MONITOR_WIDTH / 2), int(MONITOR_HEIGHT / 2) )

    
    def retire_party(self) -> None:
        """
        Use this method to retire party from the run.
        """

        self.search_and_click_on_target(VIEW_PARTY_BUTTON)

        self.search_and_click_on_target(RETIRE_BUTTON)

        self.search_and_click_on_target(RETIRE_CONFIRM_BUTTON)

        time.sleep(3)
        self.search_and_click_on_target(BATTLE_SPOILS_ICON)


    def key_capture_thread(self) -> None:
        """
        This method is used to capture Enter key in a separate thread.
        """

        input()
        self.continue_waiting = False


    def start_key_capture_thread(self) -> None:
        """
        Use this method to start a new thread to capture
        Enter key and stop waiting cycle between battles.
        """

        thread_names = [thread.name for thread in th.enumerate()]
        if "key_capture_thread" not in thread_names:
            th.Thread(
                target=self.key_capture_thread, 
                args=(), 
                name='key_capture_thread', 
                daemon=True
            ).start()


    async def wait(self) -> None:
        """
        Use this method to wait for T_BETWEEN_CYCLES amount of seconds.
        """

        # Listens for Enter key to stop waiting cycle.

        self.start_key_capture_thread()

        countdown = T_BETWEEN_CYCLES
        while countdown != 0 and self.continue_waiting:
            if countdown % 60 == 0:
                print(f'Time until the battle: {int(countdown / 60)} mins.')
            time.sleep(1)
            countdown -= 1

        # Set continue waiting back to True 
        # In case it was changed in key_capture_thread 
        self.continue_waiting = True


    def save_screenshot(self, folder: str) -> str:
        """
        Use this method to save a screenshot.
        It's name will represent date/time.

        Args:
            folder (str): Screenshot destination folder name.

        Returns:
            (str): Full path to the screenshot.
        """
        screenshot_path = folder + '/' + str(datetime.datetime.now())[:-7].replace(':', '.') + '.jpg'
        pyautogui.screenshot(screenshot_path)

        return screenshot_path